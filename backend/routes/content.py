from flask import Blueprint, request, jsonify
from backend.models.content import ContentManagement
from backend.models.user import User
from backend.app import db
from backend.middleware.security import token_required, admin_required
from datetime import datetime, timezone
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import os

bp = Blueprint('content', __name__)

def utc_now():
    """Get current UTC time"""
    return datetime.now(timezone.utc)

@bp.route('/content/<content_type>', methods=['GET'])
def get_content_by_type(content_type):
    """Get content by type (public endpoint)"""
    try:
        content_items = ContentManagement.query.filter_by(
            content_type=content_type,
            is_active=True
        ).all()
        
        if not content_items:
            return jsonify({
                'success': False,
                'error': 'محتوای مورد نظر یافت نشد'
            }), 404
        
        # Convert to dictionary format
        content_dict = {}
        for item in content_items:
            content_dict[item.section_key] = item.content
        
        return jsonify({
            'success': True,
            'data': content_dict
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@bp.route('/admin/content', methods=['GET'])
@token_required
@admin_required
def get_all_content(current_user):
    """Get all content for admin management"""
    try:
        content_items = ContentManagement.query.order_by(
            ContentManagement.content_type,
            ContentManagement.section_key
        ).all()
        
        # Group by content type
        content_by_type = {}
        for item in content_items:
            if item.content_type not in content_by_type:
                content_by_type[item.content_type] = []
            
            content_by_type[item.content_type].append({
                'id': item.id,
                'section_key': item.section_key,
                'content': item.content,
                'is_active': item.is_active,
                'updated_at': item.updated_at.isoformat() if item.updated_at else None,
                'updated_by': item.updated_by
            })
        
        return jsonify({
            'success': True,
            'data': content_by_type
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@bp.route('/admin/content/<int:content_id>', methods=['PUT'])
@token_required
@admin_required
def update_content(current_user, content_id):
    """Update content item"""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({
                'success': False,
                'error': 'داده‌های ارسالی نامعتبر است'
            }), 400
        
        content_item = ContentManagement.query.get(content_id)
        if not content_item:
            return jsonify({
                'success': False,
                'error': 'محتوای مورد نظر یافت نشد'
            }), 404
        
        # Update fields
        if 'content' in data:
            content_item.content = data['content']
        
        if 'is_active' in data:
            content_item.is_active = data['is_active']
        
        content_item.updated_at = utc_now()
        content_item.updated_by = current_user.id
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'محتوا با موفقیت بروزرسانی شد',
            'data': content_item.to_dict()
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@bp.route('/admin/content/bulk-update', methods=['PUT'])
@token_required
@admin_required
def bulk_update_content(current_user):
    """Bulk update multiple content items"""
    try:
        data = request.get_json()
        
        if not data or 'updates' not in data:
            return jsonify({
                'success': False,
                'error': 'داده‌های ارسالی نامعتبر است'
            }), 400
        
        updates = data['updates']
        updated_count = 0
        
        for update in updates:
            content_id = update.get('id')
            content = update.get('content')
            is_active = update.get('is_active', True)
            
            if not content_id:
                continue
            
            content_item = ContentManagement.query.get(content_id)
            if content_item:
                if 'content' in update:
                    content_item.content = content
                if 'is_active' in update:
                    content_item.is_active = is_active
                
                content_item.updated_at = utc_now()
                content_item.updated_by = current_user.id
                updated_count += 1
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': f'{updated_count} مورد با موفقیت بروزرسانی شد'
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500
