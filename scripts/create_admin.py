#!/usr/bin/env python3
"""
Create initial admin user for testing
"""
from backend.app import create_app, db
from backend.models.user import User, Admin

def create_admin_user():
    """Create admin user if not exists"""
    app = create_app()
    
    with app.app_context():
        # Check if admin already exists
        admin_user = User.query.filter_by(username='admin').first()
        
        if admin_user:
            print("✅ Admin user already exists")
            print(f"   Username: {admin_user.username}")
            print(f"   Email: {admin_user.email}")
            print(f"   Role: {admin_user.role}")
            return
        
        try:
            # Create admin user
            admin_user = User(
                username='admin',
                email='admin@truckmaintenance.local',
                full_name='System Administrator',
                role='admin',
                is_active=True
            )
            admin_user.set_password('admin123')
            
            db.session.add(admin_user)
            db.session.flush()
            
            # Create admin record
            admin_record = Admin(
                user_id=admin_user.id,
                permissions={'all': True}
            )
            db.session.add(admin_record)
            
            db.session.commit()
            
            print("✅ Admin user created successfully!")
            print(f"   Username: admin")
            print(f"   Password: admin123")
            print(f"   Email: {admin_user.email}")
            print(f"   Role: {admin_user.role}")
            print(f"   User ID: {admin_user.id}")
            
        except Exception as e:
            db.session.rollback()
            print(f"❌ Error creating admin user: {e}")
            raise


if __name__ == '__main__':
    create_admin_user()

