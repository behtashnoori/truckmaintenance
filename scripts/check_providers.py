"""
Script to check providers status and debug why they don't show up
"""

from backend.app import create_app, db
from backend.models.company import Company, Category

def check_providers():
    app = create_app()
    
    with app.app_context():
        print("=" * 60)
        print("🔍 بررسی وضعیت Providers")
        print("=" * 60)
        
        # Get all providers
        providers = Company.query.all()
        print(f"\n📊 تعداد کل providers: {len(providers)}")
        
        if len(providers) == 0:
            print("❌ هیچ provider ای در دیتابیس وجود ندارد!")
            return
        
        # Check each provider
        for i, p in enumerate(providers, 1):
            print(f"\n{'─' * 60}")
            print(f"Provider #{i}:")
            print(f"  🆔 ID: {p.id}")
            print(f"  📛 نام: {p.name}")
            print(f"  📛 company_name: {p.company_name}")
            print(f"  ✅ فعال: {'بله' if p.is_active else 'خیر'}")
            print(f"  📍 موقعیت: ({p.latitude}, {p.longitude})")
            print(f"  📏 شعاع سرویس: {p.service_radius_km} کیلومتر")
            print(f"  📞 تلفن: {p.phone_mobile}")
            print(f"  🏷️  دسته‌بندی‌ها: {[c.name for c in p.categories] if p.categories else '❌ بدون دسته‌بندی'}")
            print(f"  👤 ایجاد شده توسط: {p.created_by}")
            
            # Check potential issues
            issues = []
            if not p.is_active:
                issues.append("❌ غیرفعال است")
            if not p.categories or len(p.categories) == 0:
                issues.append("❌ دسته‌بندی ندارد")
            if p.latitude == 0 and p.longitude == 0:
                issues.append("⚠️  موقعیت جغرافیایی صفر است")
            
            if issues:
                print(f"  🚨 مشکلات:")
                for issue in issues:
                    print(f"     {issue}")
        
        print(f"\n{'=' * 60}")
        
        # Summary
        active_count = Company.query.filter_by(is_active=True).count()
        inactive_count = len(providers) - active_count
        
        # Check providers without categories
        no_category_count = 0
        for p in providers:
            if not p.categories or len(p.categories) == 0:
                no_category_count += 1
        
        print("\n📈 خلاصه:")
        print(f"  ✅ فعال: {active_count}")
        print(f"  ❌ غیرفعال: {inactive_count}")
        print(f"  🏷️  بدون دسته‌بندی: {no_category_count}")
        
        # Check categories
        categories = Category.query.all()
        print(f"\n📚 دسته‌بندی‌های موجود: {len(categories)}")
        for cat in categories:
            company_count = len(cat.companies)
            print(f"  - {cat.name}: {company_count} provider")
        
        print(f"\n{'=' * 60}")

if __name__ == "__main__":
    check_providers()

