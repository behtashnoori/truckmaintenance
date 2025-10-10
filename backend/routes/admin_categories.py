from flask import Blueprint, request, jsonify
from datetime import datetime
from pydantic import ValidationError, BaseModel, Field
from ..app import db
from ..models.company import Category, Company
from ..middleware.security import token_required, admin_required, validate_input, sanitize_string
from ..schemas.pagination import PaginationParams, PaginatedResponse
from ..schemas.response import ApiResponse, ErrorResponse
import logging

logger = logging.getLogger(__name__)

bp = Blueprint("admin_categories", __name__)


class CategoryCreate(BaseModel):
    """Schema for creating a category"""
    name: str = Field(..., min_length=2, max_length=100, description="Category name")


@bp.route("/categories", methods=["GET"])
@token_required
@admin_required
def get_categories(current_user):
    """Get all categories with company counts and pagination - Admin only"""
    try:
        # Parse pagination parameters
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 20, type=int)
        
        pagination = PaginationParams(page=page, per_page=per_page)
        
        # Query categories
        query = Category.query.order_by(Category.name)
        total = query.count()
        categories = query.offset(pagination.offset).limit(pagination.limit).all()
        
        categories_data = []
        for category in categories:
            # Count companies in this category
            companies_count = len(category.companies)
            
            categories_data.append({
                "id": category.id,
                "name": category.name,
                "companies_count": companies_count
            })
        
        # Return paginated response
        response = PaginatedResponse.create(
            items=categories_data,
            page=pagination.page,
            per_page=pagination.per_page,
            total=total
        )
        
        return jsonify(response), 200
        
    except Exception as e:
        logger.error(f"Error getting categories: {str(e)}", exc_info=True)
        return jsonify({
            "success": False,
            "error": "خطا در دریافت دسته‌بندی‌ها"
        }), 500


@bp.route("/categories", methods=["POST"])
@token_required
@admin_required
def create_category(current_user):
    """Create a new category - Admin only"""
    try:
        data = request.get_json(silent=True)
        
        # Check if JSON is valid
        if data is None:
            return jsonify({
                "success": False,
                "error": "داده‌های ورودی نامعتبر است"
            }), 400
        
        # Validate with Pydantic
        try:
            category_data = CategoryCreate(**data)
        except ValidationError as e:
            return jsonify({
                "success": False,
                "error": "خطای اعتبارسنجی داده‌ها",
                "details": e.errors()
            }), 400
        
        name = sanitize_string(category_data.name)
        
        # Check if category already exists
        existing_category = Category.query.filter_by(name=name).first()
        if existing_category:
            return jsonify({
                "success": False,
                "error": "دسته‌بندی با این نام قبلاً وجود دارد"
            }), 409

        # Create new category
        new_category = Category(name=name)
        db.session.add(new_category)
        db.session.commit()

        return jsonify({
            "success": True,
            "message": "دسته‌بندی با موفقیت ایجاد شد",
            "data": {
                "id": new_category.id,
                "name": new_category.name,
                "companies_count": 0
            }
        }), 201

    except Exception as e:
        db.session.rollback()
        logger.error(f"Error creating category: {str(e)}", exc_info=True)
        return jsonify({
            "success": False,
            "error": "خطا در ایجاد دسته‌بندی"
        }), 500


@bp.route("/categories/<int:category_id>", methods=["PUT"])
@token_required
@admin_required
def update_category(current_user, category_id):
    """Update an existing category - Admin only"""
    try:
        category = Category.query.get(category_id)
        
        if not category:
            return jsonify({
                "success": False,
                "error": "دسته‌بندی یافت نشد"
            }), 404
        
        data = request.get_json()
        
        # Validate with Pydantic
        try:
            category_data = CategoryCreate(**data)
        except ValidationError as e:
            return jsonify({
                "success": False,
                "error": "خطای اعتبارسنجی داده‌ها",
                "details": e.errors()
            }), 400

        new_name = sanitize_string(category_data.name)
        
        # Check if another category with this name exists
        existing_category = Category.query.filter(
            Category.name == new_name,
            Category.id != category_id
        ).first()
        
        if existing_category:
            return jsonify({
                "success": False,
                "error": "دسته‌بندی با این نام قبلاً وجود دارد"
            }), 409

        # Update category name
        category.name = new_name
        db.session.commit()

        return jsonify({
            "success": True,
            "message": "دسته‌بندی با موفقیت بروزرسانی شد",
            "data": {
                "id": category.id,
                "name": category.name,
                "companies_count": len(category.companies)
            }
        }), 200

    except Exception as e:
        db.session.rollback()
        logger.error(f"Error updating category: {str(e)}", exc_info=True)
        return jsonify({
            "success": False,
            "error": "خطا در بروزرسانی دسته‌بندی"
        }), 500


@bp.route("/categories/<int:category_id>", methods=["DELETE"])
@token_required
@admin_required
def delete_category(current_user, category_id):
    """Delete a category (only if no companies are using it) - Admin only"""
    try:
        category = Category.query.get(category_id)
        
        if not category:
            return jsonify({
                "success": False,
                "error": "دسته‌بندی یافت نشد"
            }), 404
        
        # Check if any companies are using this category
        companies_count = len(category.companies)
        if companies_count > 0:
            return jsonify({
                "success": False,
                "error": f"امکان حذف دسته‌بندی وجود ندارد. {companies_count} شرکت از این دسته‌بندی استفاده می‌کنند."
            }), 400

        # Delete the category
        db.session.delete(category)
        db.session.commit()

        return jsonify({
            "success": True,
            "message": "دسته‌بندی با موفقیت حذف شد"
        }), 200

    except Exception as e:
        db.session.rollback()
        logger.error(f"Error deleting category: {str(e)}", exc_info=True)
        return jsonify({
            "success": False,
            "error": "خطا در حذف دسته‌بندی"
        }), 500


@bp.route("/categories/<int:category_id>/companies", methods=["GET"])
@token_required
@admin_required
def get_category_companies(current_user, category_id):
    """Get all companies in a specific category with pagination - Admin only"""
    try:
        category = Category.query.get(category_id)
        
        if not category:
            return jsonify({
                "success": False,
                "error": "دسته‌بندی یافت نشد"
            }), 404
        
        # Parse pagination parameters
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 20, type=int)
        
        pagination = PaginationParams(page=page, per_page=per_page)
        
        # Get companies for this category
        companies = category.companies
        total = len(companies)
        
        # Manual pagination
        start = pagination.offset
        end = start + pagination.limit
        paginated_companies = companies[start:end]
        
        companies_data = []
        for company in paginated_companies:
            companies_data.append({
                "id": company.id,
                "name": company.name,
                "address": company.address,
                "phone_mobile": company.phone_mobile,
                "phone_landline": company.phone_landline,
                "is_active": company.is_active
            })
        
        # Return paginated response
        response = PaginatedResponse.create(
            items=companies_data,
            page=pagination.page,
            per_page=pagination.per_page,
            total=total
        )
        
        # Add category info to response
        response['category'] = {
            "id": category.id,
            "name": category.name
        }
        
        return jsonify(response), 200

    except Exception as e:
        logger.error(f"Error getting category companies: {str(e)}", exc_info=True)
        return jsonify({
            "success": False,
            "error": "خطا در دریافت شرکت‌های دسته‌بندی"
        }), 500


@bp.route("/categories/statistics", methods=["GET"])
@token_required
@admin_required
def get_category_statistics(current_user):
    """Get statistics about categories and companies - Admin only"""
    try:
        total_categories = Category.query.count()
        total_companies = Company.query.filter_by(is_active=True).count()
        
        # Get categories with company counts
        categories_with_counts = []
        for category in Category.query.all():
            companies_count = len(category.companies)
            categories_with_counts.append({
                "id": category.id,
                "name": category.name,
                "companies_count": companies_count
            })
        
        # Sort by company count (descending)
        categories_with_counts.sort(key=lambda x: x['companies_count'], reverse=True)
        
        return jsonify({
            "success": True,
            "data": {
                "total_categories": total_categories,
                "total_companies": total_companies,
                "categories": categories_with_counts,
                "most_popular_category": categories_with_counts[0] if categories_with_counts else None
            }
        }), 200

    except Exception as e:
        logger.error(f"Error getting category statistics: {str(e)}", exc_info=True)
        return jsonify({
            "success": False,
            "error": "خطا در دریافت آمار دسته‌بندی‌ها"
        }), 500
