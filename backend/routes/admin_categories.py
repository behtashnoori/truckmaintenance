from flask import Blueprint, request, jsonify
from datetime import datetime
from ..app import db
from ..models.company import Category, Company
from ..middleware.security import token_required, admin_required, validate_input, sanitize_string

bp = Blueprint("admin_categories", __name__)


@bp.route("/admin/categories", methods=["GET"])
@token_required
@admin_required
def get_categories(current_user):
    """Get all categories with company counts - Admin only"""
    try:
        categories = Category.query.all()
        categories_data = []
        
        for category in categories:
            # Count companies in this category
            companies_count = len(category.companies)
            
            categories_data.append({
                "id": category.id,
                "name": category.name,
                "companies_count": companies_count,
                "created_at": category.id  # Using ID as a simple timestamp proxy
            })
        
        return jsonify({"categories": categories_data}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@bp.route("/admin/categories", methods=["POST"])
@token_required
@admin_required
@validate_input(required_fields=['name'], allowed_fields=['name'])
def create_category(current_user):
    """Create a new category - Admin only"""
    try:
        data = request.get_json()
        name = sanitize_string(data.get('name', ''))
        
        if not name:
            return jsonify({"error": "Category name is required"}), 400

        # Check if category already exists
        existing_category = Category.query.filter_by(name=name).first()
        if existing_category:
            return jsonify({"error": "Category with this name already exists"}), 400

        # Create new category
        new_category = Category(name=name)
        db.session.add(new_category)
        db.session.commit()

        return jsonify({
            "message": "Category created successfully",
            "category": {
                "id": new_category.id,
                "name": new_category.name,
                "companies_count": 0
            }
        }), 201

    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500


@bp.route("/admin/categories/<int:category_id>", methods=["PUT"])
def update_category(category_id):
    """Update an existing category"""
    try:
        category = Category.query.get_or_404(category_id)
        data = request.get_json()
        
        if not data or not data.get('name'):
            return jsonify({"error": "Category name is required"}), 400

        new_name = data['name'].strip()
        
        # Check if another category with this name exists
        existing_category = Category.query.filter(
            Category.name == new_name,
            Category.id != category_id
        ).first()
        
        if existing_category:
            return jsonify({"error": "Category with this name already exists"}), 400

        # Update category name
        old_name = category.name
        category.name = new_name
        db.session.commit()

        return jsonify({
            "message": "Category updated successfully",
            "category": {
                "id": category.id,
                "name": category.name,
                "companies_count": len(category.companies)
            }
        }), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500


@bp.route("/admin/categories/<int:category_id>", methods=["DELETE"])
def delete_category(category_id):
    """Delete a category (only if no companies are using it)"""
    try:
        category = Category.query.get_or_404(category_id)
        
        # Check if any companies are using this category
        if len(category.companies) > 0:
            return jsonify({
                "error": f"Cannot delete category. {len(category.companies)} companies are using this category."
            }), 400

        # Delete the category
        db.session.delete(category)
        db.session.commit()

        return jsonify({"message": "Category deleted successfully"}), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500


@bp.route("/admin/categories/<int:category_id>/companies", methods=["GET"])
def get_category_companies(category_id):
    """Get all companies in a specific category"""
    try:
        category = Category.query.get_or_404(category_id)
        
        companies_data = []
        for company in category.companies:
            companies_data.append({
                "id": company.id,
                "name": company.name,
                "address": company.address,
                "phone_mobile": company.phone_mobile,
                "phone_landline": company.phone_landline,
                "is_active": company.is_active
            })
        
        return jsonify({
            "category": {
                "id": category.id,
                "name": category.name
            },
            "companies": companies_data
        }), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@bp.route("/admin/categories/statistics", methods=["GET"])
def get_category_statistics():
    """Get statistics about categories and companies"""
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
            "total_categories": total_categories,
            "total_companies": total_companies,
            "categories": categories_with_counts,
            "most_popular_category": categories_with_counts[0] if categories_with_counts else None
        }), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500
