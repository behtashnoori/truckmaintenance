"""
Script to create a Business Expert user for testing
"""

from backend.app import create_app, db
from backend.models.user import User, BusinessExpert

def create_business_expert_user():
    app = create_app()
    
    with app.app_context():
        # Check if business expert already exists
        existing_user = User.query.filter_by(username='business_expert').first()
        
        if existing_user:
            print("Business Expert user already exists!")
            print(f"Username: {existing_user.username}")
            print(f"Role: {existing_user.role}")
            
            # Update password if needed
            existing_user.set_password('expert123')
            
            # Ensure BusinessExpert record exists
            if not existing_user.business_expert:
                business_expert_record = BusinessExpert(
                    user_id=existing_user.id,
                    expertise_area='Provider Management',
                    is_active=True
                )
                db.session.add(business_expert_record)
                print("BusinessExpert record created")
            
            db.session.commit()
            print("Password reset to: expert123")
        else:
            # Create new business expert user
            business_expert_user = User(
                username='business_expert',
                email='business_expert@truckmaintenance.com',
                full_name='کارشناس بازرگانی',
                role='business_expert',
                is_active=True
            )
            business_expert_user.set_password('expert123')
            
            db.session.add(business_expert_user)
            db.session.flush()  # Get the user ID
            
            # Create BusinessExpert record
            business_expert_record = BusinessExpert(
                user_id=business_expert_user.id,
                expertise_area='Provider Management',
                is_active=True
            )
            db.session.add(business_expert_record)
            db.session.commit()
            
            print("Business Expert user created successfully!")
            print(f"Username: business_expert")
            print(f"Password: expert123")
            print(f"Role: business_expert")

if __name__ == "__main__":
    create_business_expert_user()

