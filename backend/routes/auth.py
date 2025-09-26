from flask import Blueprint, request, jsonify, current_app
from ..app import db
from ..models.user import User, Admin, SupportSpecialist
from ..middleware.security import token_required, admin_required, validate_input, sanitize_string, validate_email
from ..middleware.rate_limiting import rate_limit, login_rate_limit
from ..middleware.logging import log_authentication_attempts, log_security_event
import jwt
import datetime

bp = Blueprint("auth", __name__)


@bp.route("/login", methods=["POST"])
@login_rate_limit(max_attempts=5, window_minutes=15)
@validate_input(required_fields=['username', 'password'])
@log_authentication_attempts
def login():
    """User login with JWT token"""
    data = request.get_json()
    username = sanitize_string(data.get("username", ""))
    password = data.get("password", "")

    if not username or not password:
        return jsonify({"error": "Username and password are required"}), 400

    try:
        # Find user using ORM
        user = User.query.filter_by(username=username, is_active=True).first()
        
        if not user or not user.check_password(password):
            return jsonify({"error": "Invalid credentials"}), 401
        
        # Generate JWT token
        token = jwt.encode({
            'user_id': user.id,
            'username': user.username,
            'role': user.role,
            'exp': datetime.datetime.utcnow() + datetime.timedelta(hours=24)
        }, current_app.config['SECRET_KEY'], algorithm='HS256')
        
        return jsonify({
            "message": "Login successful",
            "token": token,
            "user": {
                "id": user.id,
                "username": user.username,
                "email": user.email,
                "full_name": user.full_name,
                "role": user.role
            }
        }), 200
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@bp.route("/logout", methods=["POST"])
def logout():
    """User logout (client should remove token)"""
    return jsonify({"message": "Logout successful"}), 200


@bp.route("/me", methods=["GET"])
def get_current_user():
    """Get current user info - requires JWT token"""
    token = None
    
    if 'Authorization' in request.headers:
        auth_header = request.headers['Authorization']
        try:
            token = auth_header.split(" ")[1]  # Bearer <token>
        except IndexError:
            return jsonify({'error': 'Token format invalid'}), 401
    
    if not token:
        return jsonify({'error': 'Token is missing'}), 401
    
    try:
        data = jwt.decode(token, current_app.config['SECRET_KEY'], algorithms=['HS256'])
        user = User.query.filter_by(id=data['user_id']).first()
        
        if not user or not user.is_active:
            return jsonify({'error': 'User not found or inactive'}), 401
        
        return jsonify({
            "id": user.id,
            "username": user.username,
            "email": user.email,
            "full_name": user.full_name,
            "role": user.role,
            "is_active": user.is_active
        }), 200
        
    except jwt.ExpiredSignatureError:
        return jsonify({'error': 'Token has expired'}), 401
    except jwt.InvalidTokenError:
        return jsonify({'error': 'Token is invalid'}), 401
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@bp.route("/users", methods=["GET"])
def get_users():
    """Get all users (admin only)"""
    if 'user_id' not in session or session.get('role') != 'admin':
        return jsonify({"error": "Access denied"}), 403
    
    try:
        conn = psycopg2.connect(
            host=POSTGRES_HOST,
            port=POSTGRES_PORT,
            user=POSTGRES_USER,
            password=POSTGRES_PASSWORD,
            database=POSTGRES_DB
        )
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT u.id, u.username, u.email, u.full_name, u.role, u.is_active, u.created_at,
                   CASE 
                       WHEN u.role = 'admin' THEN a.permissions
                       WHEN u.role = 'support' THEN s.department
                       ELSE NULL
                   END as additional_info
            FROM users u
            LEFT JOIN admins a ON u.id = a.user_id
            LEFT JOIN support_specialists s ON u.id = s.user_id
            ORDER BY u.created_at DESC
        """)
        
        users = []
        for row in cursor.fetchall():
            users.append({
                "id": row[0],
                "username": row[1],
                "email": row[2],
                "full_name": row[3],
                "role": row[4],
                "is_active": row[5],
                "created_at": row[6].isoformat() if row[6] else None,
                "additional_info": row[7]
            })
        
        cursor.close()
        conn.close()
        
        return jsonify({"users": users}), 200
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@bp.route("/users", methods=["POST"])
@token_required
@admin_required
@validate_input(required_fields=['username', 'email', 'password', 'full_name', 'role'], 
                allowed_fields=['username', 'email', 'password', 'full_name', 'role', 'department', 'max_applications'])
def create_user(current_user):
    """Create new user (admin only)"""
    data = request.get_json()
    username = sanitize_string(data.get("username", ""))
    email = sanitize_string(data.get("email", ""))
    password = data.get("password", "")
    full_name = sanitize_string(data.get("full_name", ""))
    role = data.get("role", "").strip()
    
    if not all([username, email, password, full_name, role]):
        return jsonify({"error": "All fields are required"}), 400
    
    if role not in ['admin', 'business_expert', 'support']:
        return jsonify({"error": "Invalid role"}), 400
    
    if not validate_email(email):
        return jsonify({"error": "Invalid email format"}), 400
    
    try:
        # Check if user already exists
        if User.query.filter_by(username=username).first():
            return jsonify({"error": "Username already exists"}), 409
        
        if User.query.filter_by(email=email).first():
            return jsonify({"error": "Email already exists"}), 409
        
        # Create new user using ORM
        new_user = User(
            username=username,
            email=email,
            full_name=full_name,
            role=role,
            is_active=True
        )
        new_user.set_password(password)
        
        db.session.add(new_user)
        db.session.flush()  # Get the ID
        
        # Create role-specific record
        if role == 'admin':
            admin = Admin(user_id=new_user.id, permissions={"all": True})
            db.session.add(admin)
        elif role == 'support':
            department = data.get("department", "")
            max_applications = data.get("max_applications", 50)
            support = SupportSpecialist(
                user_id=new_user.id, 
                department=department, 
                max_applications=max_applications
            )
            db.session.add(support)
        
        db.session.commit()
        
        return jsonify({
            "message": "User created successfully",
            "user_id": new_user.id
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500


