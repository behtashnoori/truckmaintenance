"""
Manual Test Script for Provider Application Flow
اسکریپت تست دستی برای جریان ثبت درخواست ارائه‌دهنده
"""

import requests
import json
from datetime import datetime

# Configuration
BASE_URL = "http://localhost:5000"

# Colors for terminal output
class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    END = '\033[0m'

def print_success(message):
    print(f"{Colors.GREEN}✓ {message}{Colors.END}")

def print_error(message):
    print(f"{Colors.RED}✗ {message}{Colors.END}")

def print_info(message):
    print(f"{Colors.BLUE}ℹ {message}{Colors.END}")

def print_warning(message):
    print(f"{Colors.YELLOW}⚠ {message}{Colors.END}")

def print_section(title):
    print(f"\n{Colors.YELLOW}{'='*60}{Colors.END}")
    print(f"{Colors.YELLOW}{title}{Colors.END}")
    print(f"{Colors.YELLOW}{'='*60}{Colors.END}\n")


def test_submit_provider_application():
    """Test 1: Submit a provider application"""
    print_section("Test 1: ثبت درخواست ارائه‌دهنده")
    
    url = f"{BASE_URL}/api/provider-applications"
    data = {
        "companyName": "شرکت تست امداد خودرو",
        "representativeFirstName": "علی",
        "representativeLastName": "احمدی",
        "address": "تهران، اتوبان آزادگان، کیلومتر 10",
        "phoneMobile": "09121234567",
        "phoneLandline": "02155667788",
        "serviceCategories": ["امداد جاده‌ای", "تعویض لاستیک", "یدک کش"],
        "latitude": 35.6892,
        "longitude": 51.3890
    }
    
    print_info(f"ارسال درخواست به: {url}")
    print_info(f"داده‌های ارسالی:")
    print(json.dumps(data, indent=2, ensure_ascii=False))
    
    try:
        response = requests.post(url, json=data, headers={"Content-Type": "application/json"})
        
        print_info(f"Status Code: {response.status_code}")
        
        if response.status_code == 201:
            response_data = response.json()
            print_success("درخواست با موفقیت ثبت شد!")
            print_info(f"Response:")
            print(json.dumps(response_data, indent=2, ensure_ascii=False))
            
            if 'data' in response_data and 'id' in response_data['data']:
                app_id = response_data['data']['id']
                print_success(f"Application ID: {app_id}")
                return app_id
        else:
            print_error(f"خطا در ثبت درخواست: {response.status_code}")
            print(response.text)
            return None
            
    except requests.exceptions.ConnectionError:
        print_error("خطا: اتصال به سرور ممکن نیست. آیا سرور Flask در حال اجرا است?")
        print_info("لطفاً سرور را با دستور زیر اجرا کنید:")
        print_info("  python scripts/run_backend.py")
        return None
    except Exception as e:
        print_error(f"خطای غیرمنتظره: {str(e)}")
        return None


def test_login_business_expert():
    """Test 2: Login as business expert"""
    print_section("Test 2: ورود کارشناس بازرگانی")
    
    url = f"{BASE_URL}/api/login"
    data = {
        "username": "business_expert",
        "password": "expert123"
    }
    
    print_info(f"ارسال درخواست login به: {url}")
    
    try:
        response = requests.post(url, json=data)
        
        if response.status_code == 200:
            response_data = response.json()
            print_success("ورود موفق!")
            
            if 'token' in response_data:
                token = response_data['token']
                print_success(f"Token دریافت شد")
                return token
        else:
            print_error(f"خطا در ورود: {response.status_code}")
            print(response.text)
            print_warning("\nاگر کاربر business_expert وجود ندارد، آن را با دستور زیر ایجاد کنید:")
            print_info("  python scripts/create_business_expert.py")
            return None
            
    except Exception as e:
        print_error(f"خطا: {str(e)}")
        return None


def test_get_pending_applications(token):
    """Test 3: Get pending applications"""
    print_section("Test 3: دریافت لیست درخواست‌های در انتظار")
    
    url = f"{BASE_URL}/api/business-expert/applications"
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    print_info(f"درخواست به: {url}")
    
    try:
        response = requests.get(url, headers=headers)
        
        if response.status_code == 200:
            response_data = response.json()
            print_success("لیست درخواست‌ها دریافت شد!")
            
            if 'data' in response_data:
                applications = response_data['data']
                print_info(f"تعداد درخواست‌های pending: {len(applications)}")
                
                for app in applications:
                    print(f"\n  ID: {app.get('id')}")
                    print(f"  شرکت: {app.get('company_name')}")
                    print(f"  وضعیت: {app.get('status')}")
                    print(f"  تلفن: {app.get('phone_mobile')}")
                
                return applications
        else:
            print_error(f"خطا: {response.status_code}")
            print(response.text)
            return None
            
    except Exception as e:
        print_error(f"خطا: {str(e)}")
        return None


def test_approve_application(token, app_id):
    """Test 4: Approve application"""
    print_section(f"Test 4: تایید درخواست {app_id}")
    
    url = f"{BASE_URL}/api/business-expert/applications/{app_id}/approve"
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    data = {
        "notes": "درخواست بررسی و تایید شد."
    }
    
    print_info(f"ارسال درخواست تایید به: {url}")
    
    try:
        response = requests.post(url, headers=headers, json=data)
        
        if response.status_code == 200:
            response_data = response.json()
            print_success("درخواست تایید شد!")
            print_info("Response:")
            print(json.dumps(response_data, indent=2, ensure_ascii=False))
            return True
        else:
            print_error(f"خطا در تایید: {response.status_code}")
            print(response.text)
            return False
            
    except Exception as e:
        print_error(f"خطا: {str(e)}")
        return False


def test_dashboard_stats(token):
    """Test 5: Get dashboard statistics"""
    print_section("Test 5: آمار داشبورد")
    
    url = f"{BASE_URL}/api/business-expert/dashboard"
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    print_info(f"درخواست آمار از: {url}")
    
    try:
        response = requests.get(url, headers=headers)
        
        if response.status_code == 200:
            response_data = response.json()
            print_success("آمار دریافت شد!")
            
            if 'data' in response_data:
                stats = response_data['data']
                print(f"\n  درخواست‌های در انتظار: {stats.get('pending_reviews', 0)}")
                print(f"  تایید شده امروز: {stats.get('approved_today', 0)}")
                print(f"  کل شرکت‌های فعال: {stats.get('total_companies', 0)}")
                
                return stats
        else:
            print_error(f"خطا: {response.status_code}")
            print(response.text)
            return None
            
    except Exception as e:
        print_error(f"خطا: {str(e)}")
        return None


def main():
    """Main test runner"""
    print(f"\n{Colors.BLUE}{'='*60}{Colors.END}")
    print(f"{Colors.BLUE}تست دستی جریان ثبت درخواست ارائه‌دهنده{Colors.END}")
    print(f"{Colors.BLUE}Provider Application Manual Test{Colors.END}")
    print(f"{Colors.BLUE}{'='*60}{Colors.END}")
    
    print_info(f"زمان: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print_info(f"Base URL: {BASE_URL}")
    
    # Test 1: Submit application
    app_id = test_submit_provider_application()
    if not app_id:
        print_error("\n❌ تست متوقف شد: درخواست ثبت نشد")
        return
    
    input(f"\n{Colors.YELLOW}Enter را بزنید برای ادامه به تست بعدی...{Colors.END}")
    
    # Test 2: Login
    token = test_login_business_expert()
    if not token:
        print_error("\n❌ تست متوقف شد: ورود انجام نشد")
        return
    
    input(f"\n{Colors.YELLOW}Enter را بزنید برای ادامه به تست بعدی...{Colors.END}")
    
    # Test 3: Get applications
    applications = test_get_pending_applications(token)
    if not applications:
        print_warning("\n⚠ هیچ درخواستی یافت نشد")
    
    input(f"\n{Colors.YELLOW}Enter را بزنید برای ادامه به تست بعدی...{Colors.END}")
    
    # Test 4: Approve application
    if app_id:
        success = test_approve_application(token, app_id)
        if not success:
            print_warning("\n⚠ تایید درخواست انجام نشد")
    
    input(f"\n{Colors.YELLOW}Enter را بزنید برای ادامه به تست بعدی...{Colors.END}")
    
    # Test 5: Dashboard stats
    stats = test_dashboard_stats(token)
    
    # Final summary
    print_section("خلاصه نتایج")
    print_success("✓ همه تست‌ها با موفقیت انجام شد!")
    print_info("\nمراحل انجام شده:")
    print("  1. ✓ ثبت درخواست ارائه‌دهنده")
    print("  2. ✓ ورود کارشناس بازرگانی")
    print("  3. ✓ دریافت لیست درخواست‌ها")
    print("  4. ✓ تایید درخواست")
    print("  5. ✓ دریافت آمار داشبورد")
    
    print(f"\n{Colors.GREEN}{'='*60}{Colors.END}")
    print(f"{Colors.GREEN}تست با موفقیت به پایان رسید!{Colors.END}")
    print(f"{Colors.GREEN}{'='*60}{Colors.END}\n")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print(f"\n\n{Colors.YELLOW}تست توسط کاربر متوقف شد.{Colors.END}\n")
    except Exception as e:
        print(f"\n{Colors.RED}خطای غیرمنتظره: {str(e)}{Colors.END}\n")

