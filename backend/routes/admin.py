from flask import Blueprint, request, jsonify, session
import psycopg2
from ..db_credentials import POSTGRES_USER, POSTGRES_PASSWORD, POSTGRES_HOST, POSTGRES_PORT, POSTGRES_DB

bp = Blueprint("admin", __name__)


def require_admin():
    """Check if user is admin"""
    if 'user_id' not in session or session.get('role') != 'admin':
        return jsonify({"error": "Access denied"}), 403
    return None


def require_auth():
    """Check if user is authenticated"""
    if 'user_id' not in session:
        return jsonify({"error": "Not authenticated"}), 401
    return None


@bp.route("/applications", methods=["GET"])
def get_applications():
    """Get all provider applications"""
    auth_error = require_auth()
    if auth_error:
        return auth_error
    
    try:
        conn = psycopg2.connect(
            host=POSTGRES_HOST,
            port=POSTGRES_PORT,
            user=POSTGRES_USER,
            password=POSTGRES_PASSWORD,
            database=POSTGRES_DB
        )
        cursor = conn.cursor()
        
        # Get applications with reviewer info
        cursor.execute("""
            SELECT pa.id, pa.company_name, pa.representative_first_name, pa.representative_last_name,
                   pa.address, pa.phone_mobile, pa.phone_landline, pa.service_domain,
                   pa.latitude, pa.longitude, pa.status, pa.created_at,
                   pa.reviewed_by, pa.reviewed_at, pa.review_notes, pa.is_approved,
                   u.username as reviewer_username, u.full_name as reviewer_name
            FROM provider_application pa
            LEFT JOIN users u ON pa.reviewed_by = u.id
            ORDER BY pa.created_at DESC
        """)
        
        applications = []
        for row in cursor.fetchall():
            applications.append({
                "id": row[0],
                "company_name": row[1],
                "representative_first_name": row[2],
                "representative_last_name": row[3],
                "address": row[4],
                "phone_mobile": row[5],
                "phone_landline": row[6],
                "service_domain": row[7],
                "latitude": row[8],
                "longitude": row[9],
                "status": row[10],
                "created_at": row[11].isoformat() if row[11] else None,
                "reviewed_by": row[12],
                "reviewed_at": row[13].isoformat() if row[13] else None,
                "review_notes": row[14],
                "is_approved": row[15],
                "reviewer_username": row[16],
                "reviewer_name": row[17]
            })
        
        cursor.close()
        conn.close()
        
        return jsonify({"applications": applications}), 200
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@bp.route("/applications/<int:app_id>/review", methods=["POST"])
def review_application(app_id):
    """Review a provider application"""
    auth_error = require_auth()
    if auth_error:
        return auth_error
    
    data = request.get_json(silent=True) or {}
    is_approved = data.get("is_approved", False)
    review_notes = data.get("review_notes", "").strip()
    
    try:
        conn = psycopg2.connect(
            host=POSTGRES_HOST,
            port=POSTGRES_PORT,
            user=POSTGRES_USER,
            password=POSTGRES_PASSWORD,
            database=POSTGRES_DB
        )
        cursor = conn.cursor()
        
        # Update application
        cursor.execute("""
            UPDATE provider_application 
            SET reviewed_by = %s, reviewed_at = NOW(), review_notes = %s, 
                is_approved = %s, status = %s
            WHERE id = %s
        """, (
            session['user_id'], 
            review_notes, 
            is_approved,
            'approved' if is_approved else 'rejected',
            app_id
        ))
        
        if cursor.rowcount == 0:
            cursor.close()
            conn.close()
            return jsonify({"error": "Application not found"}), 404
        
        conn.commit()
        cursor.close()
        conn.close()
        
        return jsonify({
            "message": "Application reviewed successfully",
            "is_approved": is_approved
        }), 200
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@bp.route("/applications/<int:app_id>", methods=["DELETE"])
def delete_application(app_id):
    """Delete a provider application (admin only)"""
    admin_error = require_admin()
    if admin_error:
        return admin_error
    
    try:
        conn = psycopg2.connect(
            host=POSTGRES_HOST,
            port=POSTGRES_PORT,
            user=POSTGRES_USER,
            password=POSTGRES_PASSWORD,
            database=POSTGRES_DB
        )
        cursor = conn.cursor()
        
        cursor.execute("DELETE FROM provider_application WHERE id = %s", (app_id,))
        
        if cursor.rowcount == 0:
            cursor.close()
            conn.close()
            return jsonify({"error": "Application not found"}), 404
        
        conn.commit()
        cursor.close()
        conn.close()
        
        return jsonify({"message": "Application deleted successfully"}), 200
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@bp.route("/users/<int:user_id>", methods=["PUT"])
def update_user(user_id):
    """Update user (admin only)"""
    admin_error = require_admin()
    if admin_error:
        return admin_error
    
    data = request.get_json(silent=True) or {}
    
    try:
        conn = psycopg2.connect(
            host=POSTGRES_HOST,
            port=POSTGRES_PORT,
            user=POSTGRES_USER,
            password=POSTGRES_PASSWORD,
            database=POSTGRES_DB
        )
        cursor = conn.cursor()
        
        # Update user
        update_fields = []
        update_values = []
        
        if 'username' in data:
            update_fields.append("username = %s")
            update_values.append(data['username'])
        
        if 'email' in data:
            update_fields.append("email = %s")
            update_values.append(data['email'])
        
        if 'full_name' in data:
            update_fields.append("full_name = %s")
            update_values.append(data['full_name'])
        
        if 'is_active' in data:
            update_fields.append("is_active = %s")
            update_values.append(data['is_active'])
        
        if 'password' in data and data['password']:
            import hashlib
            import secrets
            salt = secrets.token_hex(16)
            password_hash = hashlib.pbkdf2_hmac('sha256', data['password'].encode('utf-8'), salt.encode('utf-8'), 100000).hex() + ':' + salt
            update_fields.append("password_hash = %s")
            update_values.append(password_hash)
        
        if update_fields:
            update_values.append(user_id)
            cursor.execute(f"""
                UPDATE users 
                SET {', '.join(update_fields)}, updated_at = NOW()
                WHERE id = %s
            """, update_values)
        
        # Update role-specific fields
        if 'department' in data:
            cursor.execute("""
                UPDATE support_specialists 
                SET department = %s 
                WHERE user_id = %s
            """, (data['department'], user_id))
        
        if 'max_applications' in data:
            cursor.execute("""
                UPDATE support_specialists 
                SET max_applications = %s 
                WHERE user_id = %s
            """, (data['max_applications'], user_id))
        
        if cursor.rowcount == 0:
            cursor.close()
            conn.close()
            return jsonify({"error": "User not found"}), 404
        
        conn.commit()
        cursor.close()
        conn.close()
        
        return jsonify({"message": "User updated successfully"}), 200
        
    except psycopg2.IntegrityError as e:
        if "username" in str(e):
            return jsonify({"error": "Username already exists"}), 409
        elif "email" in str(e):
            return jsonify({"error": "Email already exists"}), 409
        else:
            return jsonify({"error": "User already exists"}), 409
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@bp.route("/users/<int:user_id>", methods=["DELETE"])
def delete_user(user_id):
    """Delete user (admin only)"""
    admin_error = require_admin()
    if admin_error:
        return admin_error
    
    # Prevent admin from deleting themselves
    if user_id == session['user_id']:
        return jsonify({"error": "Cannot delete your own account"}), 400
    
    try:
        conn = psycopg2.connect(
            host=POSTGRES_HOST,
            port=POSTGRES_PORT,
            user=POSTGRES_USER,
            password=POSTGRES_PASSWORD,
            database=POSTGRES_DB
        )
        cursor = conn.cursor()
        
        cursor.execute("DELETE FROM users WHERE id = %s", (user_id,))
        
        if cursor.rowcount == 0:
            cursor.close()
            conn.close()
            return jsonify({"error": "User not found"}), 404
        
        conn.commit()
        cursor.close()
        conn.close()
        
        return jsonify({"message": "User deleted successfully"}), 200
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@bp.route("/dashboard", methods=["GET"])
def get_dashboard_stats():
    """Get dashboard statistics"""
    auth_error = require_auth()
    if auth_error:
        return auth_error
    
    try:
        conn = psycopg2.connect(
            host=POSTGRES_HOST,
            port=POSTGRES_PORT,
            user=POSTGRES_USER,
            password=POSTGRES_PASSWORD,
            database=POSTGRES_DB
        )
        cursor = conn.cursor()
        
        # Get statistics
        cursor.execute("SELECT COUNT(*) FROM provider_application")
        total_applications = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM provider_application WHERE status = 'pending'")
        pending_applications = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM provider_application WHERE is_approved = TRUE")
        approved_applications = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM users WHERE role = 'support' AND is_active = TRUE")
        active_support = cursor.fetchone()[0]
        
        cursor.close()
        conn.close()
        
        return jsonify({
            "total_applications": total_applications,
            "pending_applications": pending_applications,
            "approved_applications": approved_applications,
            "active_support": active_support
        }), 200
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500


