"""
تست سریع API های Backend برای بخش عمومی کاربران
"""

import requests
import json
import sys

class Colors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'

BASE_URL = "http://localhost:5000/api/public"

def print_test(test_name, status, details=""):
    if status:
        print(f"{Colors.OKGREEN}✓{Colors.ENDC} {test_name}")
        if details:
            print(f"  {Colors.OKCYAN}{details}{Colors.ENDC}")
    else:
        print(f"{Colors.FAIL}✗{Colors.ENDC} {test_name}")
        if details:
            print(f"  {Colors.FAIL}{details}{Colors.ENDC}")

def print_section(title):
    print(f"\n{Colors.HEADER}{Colors.BOLD}{'='*80}{Colors.ENDC}")
    print(f"{Colors.HEADER}{Colors.BOLD}{title:^80}{Colors.ENDC}")
    print(f"{Colors.HEADER}{Colors.BOLD}{'='*80}{Colors.ENDC}\n")

def test_server_health():
    """تست سلامت سرور"""
    print_section("تست سلامت سرور Backend")
    
    try:
        response = requests.get(f"{BASE_URL}/health", timeout=5)
        if response.status_code == 200:
            print_test("سرور در دسترس است", True, f"Status: {response.status_code}")
            return True
        else:
            print_test("سرور در دسترس است", False, f"Status: {response.status_code}")
            return False
    except requests.exceptions.ConnectionError:
        print_test("سرور در دسترس است", False, "سرور در حال اجرا نیست")
        print(f"\n{Colors.WARNING}لطفاً سرور Backend را با دستور زیر اجرا کنید:{Colors.ENDC}")
        print(f"{Colors.OKCYAN}python run_backend.py{Colors.ENDC}\n")
        return False
    except Exception as e:
        print_test("سرور در دسترس است", False, str(e))
        return False

def test_categories_endpoint():
    """تست endpoint دسته‌بندی‌ها"""
    print_section("تست API دسته‌بندی‌ها")
    
    try:
        response = requests.get(f"{BASE_URL}/categories", timeout=5)
        
        if response.status_code == 200:
            categories = response.json()
            print_test("دریافت لیست دسته‌بندی‌ها", True, 
                      f"تعداد دسته‌بندی‌ها: {len(categories)}")
            
            if categories:
                print(f"\n  {Colors.OKCYAN}نمونه دسته‌بندی:{Colors.ENDC}")
                print(f"  {json.dumps(categories[0], ensure_ascii=False, indent=2)}\n")
            return True
        else:
            print_test("دریافت لیست دسته‌بندی‌ها", False, 
                      f"Status: {response.status_code}")
            return False
            
    except Exception as e:
        print_test("دریافت لیست دسته‌بندی‌ها", False, str(e))
        return False

def test_providers_endpoint():
    """تست endpoint ارائه‌دهندگان"""
    print_section("تست API ارائه‌دهندگان")
    
    try:
        # تست دریافت لیست ارائه‌دهندگان
        response = requests.get(f"{BASE_URL}/providers", timeout=5)
        
        if response.status_code == 200:
            providers = response.json()
            print_test("دریافت لیست ارائه‌دهندگان", True, 
                      f"تعداد ارائه‌دهندگان: {len(providers.get('providers', []))}")
            
            if providers.get('providers'):
                print(f"\n  {Colors.OKCYAN}نمونه ارائه‌دهنده:{Colors.ENDC}")
                sample = providers['providers'][0]
                print(f"  نام: {sample.get('name', 'N/A')}")
                print(f"  دسته‌بندی: {sample.get('category', 'N/A')}")
                print(f"  آدرس: {sample.get('address', 'N/A')}\n")
            return True
        else:
            print_test("دریافت لیست ارائه‌دهندگان", False, 
                      f"Status: {response.status_code}")
            return False
            
    except Exception as e:
        print_test("دریافت لیست ارائه‌دهندگان", False, str(e))
        return False

def test_provider_signup():
    """تست endpoint ثبت‌نام ارائه‌دهنده"""
    print_section("تست API ثبت‌نام ارائه‌دهنده")
    
    # استفاده از endpoint صحیح
    signup_url = "http://localhost:5000/api/provider-applications"
    
    test_data = {
        "companyName": "تست کارگاه تعمیراتی",
        "representativeFirstName": "علی",
        "representativeLastName": "محمدی",
        "phoneMobile": "09121234567",
        "serviceDomain": "تعمیرگاه",
        "address": "تهران، خیابان تست",
        "latitude": 35.7219,
        "longitude": 51.3347
    }
    
    try:
        response = requests.post(signup_url, 
                                json=test_data, 
                                timeout=5)
        
        if response.status_code in [200, 201]:
            result = response.json()
            print_test("ثبت‌نام ارائه‌دهنده", True, 
                      f"درخواست با موفقیت ثبت شد - ID: {result.get('id', 'N/A')}")
            return True
        elif response.status_code == 409:
            print_test("ثبت‌نام ارائه‌دهنده", True, 
                      "ارائه‌دهنده قبلاً ثبت شده (duplicate test)")
            return True
        else:
            print_test("ثبت‌نام ارائه‌دهنده", False, 
                      f"Status: {response.status_code}, Response: {response.text}")
            return False
            
    except Exception as e:
        print_test("ثبت‌نام ارائه‌دهنده", False, str(e))
        return False

def test_search_providers():
    """تست endpoint جستجوی ارائه‌دهندگان"""
    print_section("تست API جستجوی ارائه‌دهندگان")
    
    try:
        params = {
            "category": "تعمیرگاه",
            "lat": 35.7219,
            "lng": 51.3347,
            "radius": 50
        }
        
        response = requests.get(f"{BASE_URL}/search", 
                               params=params, 
                               timeout=5)
        
        if response.status_code == 200:
            results = response.json()
            print_test("جستجوی ارائه‌دهندگان با فیلتر", True, 
                      f"تعداد نتایج: {len(results.get('providers', []))}")
            return True
        else:
            print_test("جستجوی ارائه‌دهندگان با فیلتر", False, 
                      f"Status: {response.status_code}")
            return False
            
    except Exception as e:
        print_test("جستجوی ارائه‌دهندگان با فیلتر", False, str(e))
        return False

def main():
    """اجرای تست‌های API"""
    print(f"\n{Colors.BOLD}{Colors.OKCYAN}{'*'*80}{Colors.ENDC}")
    print(f"{Colors.BOLD}{Colors.OKCYAN}تست API های Backend برای بخش عمومی کاربران{Colors.ENDC}")
    print(f"{Colors.BOLD}{Colors.OKCYAN}{'*'*80}{Colors.ENDC}")
    
    # تست سلامت سرور
    if not test_server_health():
        print(f"\n{Colors.FAIL}سرور Backend در دسترس نیست. تست‌ها متوقف شد.{Colors.ENDC}\n")
        return False
    
    # تست endpoint های مختلف
    results = []
    
    # تست دسته‌بندی‌ها
    results.append(("دسته‌بندی‌ها", test_categories_endpoint()))
    
    # تست ارائه‌دهندگان
    results.append(("ارائه‌دهندگان", test_providers_endpoint()))
    
    # تست جستجو
    results.append(("جستجو", test_search_providers()))
    
    # تست ثبت‌نام
    results.append(("ثبت‌نام", test_provider_signup()))
    
    # نمایش خلاصه
    print_section("خلاصه نتایج تست API")
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = f"{Colors.OKGREEN}موفق{Colors.ENDC}" if result else f"{Colors.FAIL}ناموفق{Colors.ENDC}"
        icon = f"{Colors.OKGREEN}✓{Colors.ENDC}" if result else f"{Colors.FAIL}✗{Colors.ENDC}"
        print(f"{icon} API {test_name}: {status}")
    
    print(f"\n{Colors.BOLD}نتیجه کلی: {passed}/{total} تست موفق{Colors.ENDC}")
    
    if passed == total:
        print(f"{Colors.OKGREEN}{Colors.BOLD}✓ تمام API ها با موفقیت تست شدند!{Colors.ENDC}\n")
        return True
    else:
        print(f"{Colors.WARNING}{Colors.BOLD}⚠ برخی تست‌ها ناموفق بودند{Colors.ENDC}\n")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)

