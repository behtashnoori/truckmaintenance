"""
Script to create test data for business expert testing
"""

from backend.app import create_app, db
from backend.models.provider_application import ProviderApplication
from backend.models.company import Company, Category
from datetime import datetime, timezone

def create_test_data():
    app = create_app()
    
    with app.app_context():
        print("Creating test data...")
        
        # Create test categories
        categories_data = [
            'تعمیرات موتور',
            'تعمیرات گیربکس',
            'تعمیرات سیستم برق',
            'نقاشی و صافکاری',
            'تعویض روغن',
        ]
        
        categories = {}
        for cat_name in categories_data:
            cat = Category.query.filter_by(name=cat_name).first()
            if not cat:
                cat = Category(name=cat_name)
                db.session.add(cat)
                print(f"  ✓ Category created: {cat_name}")
            categories[cat_name] = cat
        
        db.session.flush()
        
        # Create test applications (pending)
        test_applications = [
            {
                'company_name': 'تعمیرگاه خودرو سعادت',
                'representative_first_name': 'محمد',
                'representative_last_name': 'احمدی',
                'address': 'تهران، خیابان آزادی، پلاک 123',
                'phone_mobile': '09121234567',
                'phone_landline': '02133445566',
                'service_domain': 'تعمیرات موتور',
                'latitude': 35.6892,
                'longitude': 51.3890,
            },
            {
                'company_name': 'مرکز تخصصی گیربکس پارس',
                'representative_first_name': 'علی',
                'representative_last_name': 'محمدی',
                'address': 'تهران، خیابان انقلاب، نبش خیابان 12 فروردین',
                'phone_mobile': '09123456789',
                'phone_landline': '02144556677',
                'service_domain': 'تعمیرات گیربکس',
                'latitude': 35.7012,
                'longitude': 51.4123,
            },
            {
                'company_name': 'تعمیرات برق خودرو رضا',
                'representative_first_name': 'رضا',
                'representative_last_name': 'کریمی',
                'address': 'تهران، میدان ونک، برج سپهر',
                'phone_mobile': '09122223344',
                'phone_landline': None,
                'service_domain': 'تعمیرات سیستم برق',
                'latitude': 35.7585,
                'longitude': 51.4096,
            },
        ]
        
        for app_data in test_applications:
            # Check if already exists
            existing = ProviderApplication.query.filter_by(
                phone_mobile=app_data['phone_mobile']
            ).first()
            
            if not existing:
                app = ProviderApplication(**app_data, status='pending')
                db.session.add(app)
                print(f"  ✓ Application created: {app_data['company_name']}")
        
        # Create test companies (already approved)
        test_companies = [
            {
                'name': 'تعمیرگاه جامع امین',
                'address': 'تهران، خیابان کارگر، پلاک 456',
                'phone_mobile': '09111234567',
                'phone_landline': '02177889900',
                'latitude': 35.6945,
                'longitude': 51.3917,
                'is_active': True,
                'categories': ['تعمیرات موتور', 'تعویض روغن']
            },
            {
                'name': 'نقاشی و صافکاری مهر',
                'address': 'تهران، خیابان ستارخان، نبش خیابان صدری',
                'phone_mobile': '09191112233',
                'phone_landline': '02166778899',
                'latitude': 35.7234,
                'longitude': 51.3156,
                'is_active': True,
                'categories': ['نقاشی و صافکاری']
            },
        ]
        
        for company_data in test_companies:
            # Check if already exists
            existing = Company.query.filter_by(
                phone_mobile=company_data['phone_mobile']
            ).first()
            
            if not existing:
                cats = company_data.pop('categories')
                company = Company(**company_data)
                
                # Add categories
                for cat_name in cats:
                    if cat_name in categories:
                        company.categories.append(categories[cat_name])
                
                db.session.add(company)
                print(f"  ✓ Company created: {company_data['name']}")
        
        db.session.commit()
        print("\n✅ Test data created successfully!")
        print("\nSummary:")
        print(f"  - Pending applications: {ProviderApplication.query.filter_by(status='pending').count()}")
        print(f"  - Total companies: {Company.query.count()}")
        print(f"  - Categories: {Category.query.count()}")

if __name__ == "__main__":
    create_test_data()

