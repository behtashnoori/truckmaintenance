"""
تست جامع روت‌های عمومی کاربران (Public User Flows)
این اسکریپت تمام صفحات عمومی را تست می‌کند
"""

import os
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
    UNDERLINE = '\033[4m'

def print_section(title):
    print(f"\n{Colors.HEADER}{Colors.BOLD}{'='*80}{Colors.ENDC}")
    print(f"{Colors.HEADER}{Colors.BOLD}{title:^80}{Colors.ENDC}")
    print(f"{Colors.HEADER}{Colors.BOLD}{'='*80}{Colors.ENDC}\n")

def print_test(test_name, status, details=""):
    if status:
        print(f"{Colors.OKGREEN}✓{Colors.ENDC} {test_name}")
        if details:
            print(f"  {Colors.OKCYAN}{details}{Colors.ENDC}")
    else:
        print(f"{Colors.FAIL}✗{Colors.ENDC} {test_name}")
        if details:
            print(f"  {Colors.FAIL}{details}{Colors.ENDC}")

def check_file_exists(file_path):
    """بررسی وجود فایل"""
    return os.path.isfile(file_path)

def check_file_content(file_path, required_keywords=None):
    """بررسی محتوای فایل"""
    if not check_file_exists(file_path):
        return False, "فایل وجود ندارد"
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        if not content.strip():
            return False, "فایل خالی است"
        
        if required_keywords:
            missing = [kw for kw in required_keywords if kw not in content]
            if missing:
                return False, f"کلمات کلیدی موجود نیست: {', '.join(missing)}"
        
        return True, f"فایل معتبر است ({len(content)} کاراکتر)"
    except Exception as e:
        return False, f"خطا در خواندن فایل: {str(e)}"

def check_component_imports(file_path):
    """بررسی import های کامپوننت"""
    if not check_file_exists(file_path):
        return False, "فایل وجود ندارد"
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # بررسی import های اساسی React
        if 'import' not in content and 'export' not in content:
            return False, "فایل TypeScript/React معتبری نیست"
        
        return True, "Import ها معتبر هستند"
    except Exception as e:
        return False, f"خطا: {str(e)}"

def test_route_configuration():
    """تست پیکربندی روت‌ها در App.tsx"""
    print_section("تست 1: پیکربندی روت‌ها (App.tsx)")
    
    app_tsx = "src/App.tsx"
    routes = [
        ('/', 'صفحه اصلی', '<Index />'),
        ('/services', 'صفحه جستجوی خدمات', '<SearchPage />'),
        ('/c/:slug', 'صفحه دسته‌بندی', '<CategoryPage />'),
        ('/results', 'صفحه نتایج', '<ResultsPage />'),
        ('/provider/:id', 'جزئیات ارائه‌دهنده', '<ProviderDetail />'),
        ('/signup', 'ثبت‌نام ارائه‌دهنده', '<ProviderSignup />'),
        ('/signup/success', 'موفقیت ثبت‌نام', '<SignupSuccess />'),
        ('/about', 'درباره ما', '<AboutPage />'),
        ('/contact', 'تماس با ما', '<ContactPage />'),
        ('/legal/privacy', 'حریم خصوصی', '<PrivacyPolicy />'),
        ('/legal/terms', 'قوانین و مقررات', '<TermsOfService />'),
        ('/location-error', 'خطای مکان‌یابی', '<LocationError />'),
    ]
    
    if not check_file_exists(app_tsx):
        print_test("فایل App.tsx", False, "فایل وجود ندارد")
        return False
    
    with open(app_tsx, 'r', encoding='utf-8') as f:
        content = f.read()
    
    all_passed = True
    for route_path, route_name, component in routes:
        route_exists = route_path in content and component in content
        print_test(f"روت {route_path} ({route_name})", route_exists, 
                  f"کامپوننت: {component}")
        if not route_exists:
            all_passed = False
    
    return all_passed

def test_page_components():
    """تست کامپوننت‌های صفحات"""
    print_section("تست 2: کامپوننت‌های صفحات")
    
    pages = [
        ('src/pages/Index.tsx', 'صفحه اصلی', ['export']),
        ('src/pages/SearchPage.tsx', 'صفحه جستجو', ['export', 'SearchPage']),
        ('src/pages/CategoryPage.tsx', 'صفحه دسته‌بندی', ['export', 'CategoryPage']),
        ('src/pages/ResultsPage.tsx', 'صفحه نتایج', ['export', 'ResultsPage']),
        ('src/pages/ProviderDetail.tsx', 'جزئیات ارائه‌دهنده', ['export', 'ProviderDetail']),
        ('src/pages/ProviderSignup.tsx', 'ثبت‌نام', ['export', 'ProviderSignup']),
        ('src/pages/SignupSuccess.tsx', 'موفقیت ثبت‌نام', ['export', 'SignupSuccess']),
        ('src/pages/AboutPage.tsx', 'درباره ما', ['export', 'AboutPage']),
        ('src/pages/ContactPage.tsx', 'تماس با ما', ['export', 'ContactPage']),
        ('src/pages/PrivacyPolicy.tsx', 'حریم خصوصی', ['export', 'PrivacyPolicy']),
        ('src/pages/TermsOfService.tsx', 'قوانین', ['export', 'TermsOfService']),
        ('src/pages/LocationError.tsx', 'خطای مکان', ['export', 'LocationError']),
        ('src/pages/NotFound.tsx', 'صفحه 404', ['export', 'NotFound']),
    ]
    
    all_passed = True
    for file_path, page_name, keywords in pages:
        status, details = check_file_content(file_path, keywords)
        print_test(f"{page_name} ({file_path})", status, details)
        if not status:
            all_passed = False
    
    return all_passed

def test_shared_components():
    """تست کامپوننت‌های مشترک"""
    print_section("تست 3: کامپوننت‌های مشترک")
    
    components = [
        ('src/components/Header.tsx', 'هدر', ['export']),
        ('src/components/Footer.tsx', 'فوتر', ['export']),
        ('src/components/LoadingSpinner.tsx', 'لودینگ', ['export']),
        ('src/components/ErrorBoundary.tsx', 'مدیریت خطا', ['export', 'ErrorBoundary']),
        ('src/components/ProviderCard.tsx', 'کارت ارائه‌دهنده', ['export', 'ProviderCard']),
        ('src/components/CategorySelector.tsx', 'انتخاب دسته', ['export']),
        ('src/components/LocationSelector.tsx', 'انتخاب مکان', ['export']),
        ('src/components/VehicleFilter.tsx', 'فیلتر وسیله', ['export']),
    ]
    
    all_passed = True
    for file_path, comp_name, keywords in components:
        status, details = check_file_content(file_path, keywords)
        print_test(f"{comp_name} ({file_path})", status, details)
        if not status:
            all_passed = False
    
    return all_passed

def test_context_and_providers():
    """تست Context ها و Provider ها"""
    print_section("تست 4: Context ها و Provider ها")
    
    contexts = [
        ('src/contexts/LocationContext.tsx', 'Location Context', ['LocationProvider', 'export']),
    ]
    
    all_passed = True
    for file_path, context_name, keywords in contexts:
        status, details = check_file_content(file_path, keywords)
        print_test(f"{context_name} ({file_path})", status, details)
        if not status:
            all_passed = False
    
    return all_passed

def test_api_integration():
    """تست فایل‌های API"""
    print_section("تست 5: یکپارچگی API")
    
    api_files = [
        ('src/lib/api.ts', 'API Helper', ['export']),
        ('src/utils/api.ts', 'API Utils', ['export']),
    ]
    
    all_passed = True
    for file_path, api_name, keywords in api_files:
        if check_file_exists(file_path):
            status, details = check_file_content(file_path, keywords)
            print_test(f"{api_name} ({file_path})", status, details)
            if not status:
                all_passed = False
        else:
            print_test(f"{api_name} ({file_path})", False, "فایل وجود ندارد (اختیاری)")
    
    return all_passed

def test_styling_and_assets():
    """تست فایل‌های استایل و asset ها"""
    print_section("تست 6: استایل‌ها و Asset ها")
    
    files = [
        ('src/index.css', 'استایل اصلی'),
        ('src/App.css', 'استایل App'),
        ('tailwind.config.ts', 'پیکربندی Tailwind'),
        ('public/favicon.ico', 'Favicon'),
        ('public/truck-bg.svg', 'تصویر پس‌زمینه'),
    ]
    
    all_passed = True
    for file_path, file_name in files:
        exists = check_file_exists(file_path)
        print_test(f"{file_name} ({file_path})", exists)
        if not exists:
            all_passed = False
    
    return all_passed

def test_build_configuration():
    """تست پیکربندی build"""
    print_section("تست 7: پیکربندی Build")
    
    configs = [
        ('package.json', 'Package.json', ['scripts', 'dependencies']),
        ('vite.config.ts', 'Vite Config', ['export']),
        ('tsconfig.json', 'TypeScript Config', ['compilerOptions']),
        ('index.html', 'HTML اصلی', ['root', 'script']),
    ]
    
    all_passed = True
    for file_path, config_name, keywords in configs:
        status, details = check_file_content(file_path, keywords)
        print_test(f"{config_name} ({file_path})", status, details)
        if not status:
            all_passed = False
    
    return all_passed

def test_specific_page_features():
    """تست ویژگی‌های خاص هر صفحه"""
    print_section("تست 8: ویژگی‌های خاص صفحات")
    
    all_passed = True
    
    # تست صفحه اصلی
    if check_file_exists('src/pages/Index.tsx'):
        with open('src/pages/Index.tsx', 'r', encoding='utf-8') as f:
            index_content = f.read()
        
        has_header = 'Header' in index_content or 'header' in index_content.lower()
        has_footer = 'Footer' in index_content or 'footer' in index_content.lower()
        
        print_test("صفحه اصلی - دارای Header", has_header)
        print_test("صفحه اصلی - دارای Footer", has_footer)
        
        if not has_header or not has_footer:
            all_passed = False
    
    # تست صفحه جستجو
    if check_file_exists('src/pages/SearchPage.tsx'):
        with open('src/pages/SearchPage.tsx', 'r', encoding='utf-8') as f:
            search_content = f.read()
        
        has_search = 'search' in search_content.lower() or 'جستجو' in search_content
        print_test("صفحه جستجو - دارای قابلیت جستجو", has_search)
        
        if not has_search:
            all_passed = False
    
    # تست صفحه ثبت‌نام
    if check_file_exists('src/pages/ProviderSignup.tsx'):
        with open('src/pages/ProviderSignup.tsx', 'r', encoding='utf-8') as f:
            signup_content = f.read()
        
        has_form = 'form' in signup_content.lower() or 'Form' in signup_content
        print_test("صفحه ثبت‌نام - دارای فرم", has_form)
        
        if not has_form:
            all_passed = False
    
    return all_passed

def run_all_tests():
    """اجرای تمام تست‌ها"""
    print(f"\n{Colors.BOLD}{Colors.OKCYAN}{'*'*80}{Colors.ENDC}")
    print(f"{Colors.BOLD}{Colors.OKCYAN}تست جامع بخش پنل عمومی کاربران (Public User Flows){Colors.ENDC}")
    print(f"{Colors.BOLD}{Colors.OKCYAN}{'*'*80}{Colors.ENDC}")
    
    tests = [
        ("پیکربندی روت‌ها", test_route_configuration),
        ("کامپوننت‌های صفحات", test_page_components),
        ("کامپوننت‌های مشترک", test_shared_components),
        ("Context ها و Provider ها", test_context_and_providers),
        ("یکپارچگی API", test_api_integration),
        ("استایل‌ها و Asset ها", test_styling_and_assets),
        ("پیکربندی Build", test_build_configuration),
        ("ویژگی‌های خاص صفحات", test_specific_page_features),
    ]
    
    results = []
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"{Colors.FAIL}خطا در تست {test_name}: {str(e)}{Colors.ENDC}")
            results.append((test_name, False))
    
    # نمایش خلاصه نتایج
    print_section("خلاصه نتایج")
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status_icon = f"{Colors.OKGREEN}✓{Colors.ENDC}" if result else f"{Colors.FAIL}✗{Colors.ENDC}"
        status_text = f"{Colors.OKGREEN}موفق{Colors.ENDC}" if result else f"{Colors.FAIL}ناموفق{Colors.ENDC}"
        print(f"{status_icon} {test_name}: {status_text}")
    
    print(f"\n{Colors.BOLD}نتیجه کلی: {passed}/{total} تست موفق{Colors.ENDC}")
    
    if passed == total:
        print(f"{Colors.OKGREEN}{Colors.BOLD}✓ تمام تست‌ها با موفقیت انجام شد!{Colors.ENDC}")
        return True
    else:
        print(f"{Colors.WARNING}{Colors.BOLD}⚠ برخی تست‌ها ناموفق بودند{Colors.ENDC}")
        return False

if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)

