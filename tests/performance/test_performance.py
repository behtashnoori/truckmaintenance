#!/usr/bin/env python3
"""
Performance Testing Suite for Truck Maintenance API
Tests response times, concurrent requests, and load handling
"""
import requests
import json
import time
import statistics
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed
import sys

# Configuration
BASE_URL = "http://localhost:5000/api"
HEADERS = {"Content-Type": "application/json"}

# Performance thresholds (in seconds)
THRESHOLDS = {
    "login": 1.0,           # Login should be fast
    "get_users": 2.0,       # Simple queries
    "get_applications": 2.0,
    "create_company": 3.0,  # DB writes
    "search": 1.5,          # Search queries
    "public_api": 0.5       # Public endpoints should be fastest
}

# Test configuration
CONCURRENT_USERS = 10
LOAD_TEST_REQUESTS = 50

# Test results storage
performance_results = []
admin_token = None


class PerformanceMetrics:
    """Store and calculate performance metrics"""
    def __init__(self, test_name):
        self.test_name = test_name
        self.response_times = []
        self.errors = []
        self.start_time = None
        self.end_time = None
    
    def add_response_time(self, duration, status_code=200):
        """Add a response time measurement"""
        self.response_times.append(duration)
        if status_code >= 400:
            self.errors.append(status_code)
    
    def get_statistics(self):
        """Calculate statistics from response times"""
        if not self.response_times:
            return {
                "test": self.test_name,
                "count": 0,
                "error": "No data collected"
            }
        
        return {
            "test": self.test_name,
            "count": len(self.response_times),
            "min": round(min(self.response_times), 3),
            "max": round(max(self.response_times), 3),
            "avg": round(statistics.mean(self.response_times), 3),
            "median": round(statistics.median(self.response_times), 3),
            "p95": round(self.calculate_percentile(95), 3),
            "p99": round(self.calculate_percentile(99), 3),
            "errors": len(self.errors),
            "error_rate": round(len(self.errors) / len(self.response_times) * 100, 2) if self.response_times else 0
        }
    
    def calculate_percentile(self, percentile):
        """Calculate percentile from response times"""
        if not self.response_times:
            return 0
        sorted_times = sorted(self.response_times)
        index = int(len(sorted_times) * percentile / 100)
        return sorted_times[min(index, len(sorted_times) - 1)]


def print_header(text):
    """Print formatted header"""
    print(f"\n{'='*80}")
    print(f"  {text}")
    print(f"{'='*80}")


def print_metrics(metrics):
    """Print performance metrics in a formatted table"""
    print(f"\n📊 Performance Metrics: {metrics['test']}")
    print(f"{'─'*80}")
    print(f"  Total Requests: {metrics['count']}")
    print(f"  Min Time:       {metrics.get('min', 'N/A')} seconds")
    print(f"  Max Time:       {metrics.get('max', 'N/A')} seconds")
    print(f"  Avg Time:       {metrics.get('avg', 'N/A')} seconds")
    print(f"  Median Time:    {metrics.get('median', 'N/A')} seconds")
    print(f"  95th %ile:      {metrics.get('p95', 'N/A')} seconds")
    print(f"  99th %ile:      {metrics.get('p99', 'N/A')} seconds")
    print(f"  Errors:         {metrics.get('errors', 0)} ({metrics.get('error_rate', 0)}%)")
    
    # Check threshold
    avg_time = metrics.get('avg', 0)
    threshold = THRESHOLDS.get(metrics['test'].split(':')[0].strip().lower(), 2.0)
    
    if avg_time and avg_time <= threshold:
        print(f"  Status:         ✅ PASS (threshold: {threshold}s)")
    elif avg_time:
        print(f"  Status:         ❌ FAIL (threshold: {threshold}s)")
    print(f"{'─'*80}")


def setup_admin_login():
    """Login as admin and get token"""
    global admin_token
    print_header("Setup: Admin Authentication")
    
    try:
        response = requests.post(
            f"{BASE_URL}/login",
            json={"username": "admin", "password": "admin123"},
            headers=HEADERS,
            timeout=30
        )
        
        if response.status_code == 200:
            data = response.json()
            admin_token = data.get('token')
            print(f"✅ Admin login successful")
            return True
        else:
            print(f"❌ Admin login failed: {response.status_code}")
            print(f"   Response: {response.text}")
            
            # Try to get more details
            try:
                error_data = response.json()
                print(f"   Error details: {json.dumps(error_data, ensure_ascii=False, indent=2)}")
            except:
                pass
            
            return False
    except requests.exceptions.Timeout:
        print(f"❌ Admin login timed out - server may be slow or not responding")
        return False
    except Exception as e:
        print(f"❌ Admin login error: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


# =============================================================================
# Test 1: Single Request Response Times
# =============================================================================

def test_login_performance():
    """Test 1: Login endpoint performance"""
    print_header("Test 1: Login Performance")
    metrics = PerformanceMetrics("login")
    
    # Test multiple login requests
    for i in range(20):
        try:
            start = time.time()
            response = requests.post(
                f"{BASE_URL}/login",
                json={"username": "admin", "password": "admin123"},
                headers=HEADERS,
                timeout=10
            )
            duration = time.time() - start
            metrics.add_response_time(duration, response.status_code)
            
            if (i + 1) % 5 == 0:
                print(f"  Completed {i + 1}/20 requests...")
        
        except Exception as e:
            print(f"  ❌ Request {i + 1} failed: {str(e)}")
            metrics.errors.append(str(e))
    
    stats = metrics.get_statistics()
    print_metrics(stats)
    performance_results.append(stats)
    return stats


def test_get_users_performance():
    """Test 2: Get users list performance"""
    print_header("Test 2: Get Users List Performance")
    
    if not admin_token:
        print("❌ Skipping - no admin token")
        return None
    
    metrics = PerformanceMetrics("get_users")
    auth_headers = {**HEADERS, "Authorization": f"Bearer {admin_token}"}
    
    # Test with different pagination parameters
    test_params = [
        {"page": 1, "per_page": 10},
        {"page": 1, "per_page": 20},
        {"page": 1, "per_page": 50},
        {"page": 2, "per_page": 20},
    ]
    
    for i in range(5):  # 5 iterations
        for params in test_params:
            try:
                start = time.time()
                response = requests.get(
                    f"{BASE_URL}/users",
                    headers=auth_headers,
                    params=params,
                    timeout=10
                )
                duration = time.time() - start
                metrics.add_response_time(duration, response.status_code)
            
            except Exception as e:
                print(f"  ❌ Request failed: {str(e)}")
                metrics.errors.append(str(e))
        
        if (i + 1) % 2 == 0:
            print(f"  Completed {(i + 1) * len(test_params)}/{5 * len(test_params)} requests...")
    
    stats = metrics.get_statistics()
    print_metrics(stats)
    performance_results.append(stats)
    return stats


def test_get_applications_performance():
    """Test 3: Get applications list performance"""
    print_header("Test 3: Get Applications List Performance")
    
    if not admin_token:
        print("❌ Skipping - no admin token")
        return None
    
    metrics = PerformanceMetrics("get_applications")
    auth_headers = {**HEADERS, "Authorization": f"Bearer {admin_token}"}
    
    # Test with different filters
    test_params = [
        {},
        {"page": 1, "per_page": 20},
        {"status": "pending"},
        {"status": "approved"},
    ]
    
    for i in range(5):
        for params in test_params:
            try:
                start = time.time()
                response = requests.get(
                    f"{BASE_URL}/admin/provider-applications",
                    headers=auth_headers,
                    params=params,
                    timeout=10
                )
                duration = time.time() - start
                metrics.add_response_time(duration, response.status_code)
            
            except Exception as e:
                print(f"  ❌ Request failed: {str(e)}")
                metrics.errors.append(str(e))
        
        print(f"  Completed {(i + 1) * len(test_params)}/{5 * len(test_params)} requests...")
    
    stats = metrics.get_statistics()
    print_metrics(stats)
    performance_results.append(stats)
    return stats


def test_public_api_performance():
    """Test 4: Public API endpoints performance"""
    print_header("Test 4: Public API Performance")
    
    metrics = PerformanceMetrics("public_api")
    
    # Test different public endpoints
    endpoints = [
        "/public/health",
        "/public/categories",
        "/public/providers?limit=10",
        "/public/search?search=test&limit=5",
    ]
    
    for i in range(10):  # 10 iterations
        for endpoint in endpoints:
            try:
                start = time.time()
                response = requests.get(
                    f"{BASE_URL}{endpoint}",
                    timeout=10
                )
                duration = time.time() - start
                metrics.add_response_time(duration, response.status_code)
            
            except Exception as e:
                print(f"  ❌ Request to {endpoint} failed: {str(e)}")
                metrics.errors.append(str(e))
        
        if (i + 1) % 3 == 0:
            print(f"  Completed {(i + 1) * len(endpoints)}/{10 * len(endpoints)} requests...")
    
    stats = metrics.get_statistics()
    print_metrics(stats)
    performance_results.append(stats)
    return stats


# =============================================================================
# Test 5: Concurrent Request Load Testing
# =============================================================================

def make_concurrent_request(request_id, endpoint, method="GET", data=None, token=None):
    """Make a single request (used in concurrent testing)"""
    try:
        headers = HEADERS.copy()
        if token:
            headers["Authorization"] = f"Bearer {token}"
        
        start = time.time()
        
        if method == "GET":
            response = requests.get(f"{BASE_URL}{endpoint}", headers=headers, timeout=15)
        elif method == "POST":
            response = requests.post(f"{BASE_URL}{endpoint}", json=data, headers=headers, timeout=15)
        else:
            return {"id": request_id, "duration": 0, "status": 400, "error": "Invalid method"}
        
        duration = time.time() - start
        
        return {
            "id": request_id,
            "duration": duration,
            "status": response.status_code,
            "error": None
        }
    
    except Exception as e:
        return {
            "id": request_id,
            "duration": 0,
            "status": 0,
            "error": str(e)
        }


def test_concurrent_login_requests():
    """Test 5a: Concurrent login requests"""
    print_header("Test 5a: Concurrent Login Requests")
    print(f"Testing with {CONCURRENT_USERS} concurrent users...")
    
    metrics = PerformanceMetrics("concurrent_login")
    
    with ThreadPoolExecutor(max_workers=CONCURRENT_USERS) as executor:
        futures = []
        
        for i in range(LOAD_TEST_REQUESTS):
            future = executor.submit(
                make_concurrent_request,
                i,
                "/login",
                "POST",
                {"username": "admin", "password": "admin123"}
            )
            futures.append(future)
        
        completed = 0
        for future in as_completed(futures):
            result = future.result()
            if result["error"]:
                metrics.errors.append(result["error"])
            else:
                metrics.add_response_time(result["duration"], result["status"])
            
            completed += 1
            if completed % 10 == 0:
                print(f"  Completed {completed}/{LOAD_TEST_REQUESTS} requests...")
    
    stats = metrics.get_statistics()
    print_metrics(stats)
    performance_results.append(stats)
    return stats


def test_concurrent_read_requests():
    """Test 5b: Concurrent read requests (public API)"""
    print_header("Test 5b: Concurrent Read Requests (Public API)")
    print(f"Testing with {CONCURRENT_USERS} concurrent users...")
    
    metrics = PerformanceMetrics("concurrent_reads")
    
    with ThreadPoolExecutor(max_workers=CONCURRENT_USERS) as executor:
        futures = []
        
        # Mix of different endpoints
        endpoints = [
            "/public/health",
            "/public/categories",
            "/public/providers?limit=10",
            "/public/search?search=test",
        ]
        
        for i in range(LOAD_TEST_REQUESTS):
            endpoint = endpoints[i % len(endpoints)]
            future = executor.submit(
                make_concurrent_request,
                i,
                endpoint,
                "GET"
            )
            futures.append(future)
        
        completed = 0
        for future in as_completed(futures):
            result = future.result()
            if result["error"]:
                metrics.errors.append(result["error"])
            else:
                metrics.add_response_time(result["duration"], result["status"])
            
            completed += 1
            if completed % 10 == 0:
                print(f"  Completed {completed}/{LOAD_TEST_REQUESTS} requests...")
    
    stats = metrics.get_statistics()
    print_metrics(stats)
    performance_results.append(stats)
    return stats


def test_concurrent_authenticated_requests():
    """Test 5c: Concurrent authenticated requests"""
    print_header("Test 5c: Concurrent Authenticated Requests")
    
    if not admin_token:
        print("❌ Skipping - no admin token")
        return None
    
    print(f"Testing with {CONCURRENT_USERS} concurrent users...")
    metrics = PerformanceMetrics("concurrent_auth")
    
    with ThreadPoolExecutor(max_workers=CONCURRENT_USERS) as executor:
        futures = []
        
        for i in range(LOAD_TEST_REQUESTS):
            future = executor.submit(
                make_concurrent_request,
                i,
                "/users?page=1&per_page=10",
                "GET",
                token=admin_token
            )
            futures.append(future)
        
        completed = 0
        for future in as_completed(futures):
            result = future.result()
            if result["error"]:
                metrics.errors.append(result["error"])
            else:
                metrics.add_response_time(result["duration"], result["status"])
            
            completed += 1
            if completed % 10 == 0:
                print(f"  Completed {completed}/{LOAD_TEST_REQUESTS} requests...")
    
    stats = metrics.get_statistics()
    print_metrics(stats)
    performance_results.append(stats)
    return stats


# =============================================================================
# Test 6: Database Performance Tests
# =============================================================================

def test_pagination_performance():
    """Test 6: Pagination performance with different page sizes"""
    print_header("Test 6: Pagination Performance")
    
    if not admin_token:
        print("❌ Skipping - no admin token")
        return None
    
    auth_headers = {**HEADERS, "Authorization": f"Bearer {admin_token}"}
    page_sizes = [10, 20, 50, 100]
    
    for per_page in page_sizes:
        metrics = PerformanceMetrics(f"pagination_{per_page}")
        
        print(f"\n  Testing with per_page={per_page}...")
        
        for page in range(1, 6):  # Test first 5 pages
            try:
                start = time.time()
                response = requests.get(
                    f"{BASE_URL}/users",
                    headers=auth_headers,
                    params={"page": page, "per_page": per_page},
                    timeout=10
                )
                duration = time.time() - start
                metrics.add_response_time(duration, response.status_code)
            
            except Exception as e:
                print(f"  ❌ Request failed: {str(e)}")
                metrics.errors.append(str(e))
        
        stats = metrics.get_statistics()
        print(f"  Results for per_page={per_page}: Avg={stats.get('avg', 'N/A')}s, P95={stats.get('p95', 'N/A')}s")
        performance_results.append(stats)
    
    print(f"\n✅ Pagination performance test completed")


def test_filter_performance():
    """Test 7: Filter performance"""
    print_header("Test 7: Filter Performance")
    
    if not admin_token:
        print("❌ Skipping - no admin token")
        return None
    
    auth_headers = {**HEADERS, "Authorization": f"Bearer {admin_token}"}
    
    # Test different filter combinations
    filter_tests = [
        {"name": "No filters", "params": {}},
        {"name": "Role filter", "params": {"role": "user"}},
        {"name": "Active filter", "params": {"is_active": "true"}},
        {"name": "Combined filters", "params": {"role": "user", "is_active": "true"}},
    ]
    
    for test in filter_tests:
        metrics = PerformanceMetrics(f"filter_{test['name']}")
        
        print(f"\n  Testing: {test['name']}...")
        
        for i in range(10):
            try:
                start = time.time()
                response = requests.get(
                    f"{BASE_URL}/users",
                    headers=auth_headers,
                    params=test['params'],
                    timeout=10
                )
                duration = time.time() - start
                metrics.add_response_time(duration, response.status_code)
            
            except Exception as e:
                print(f"  ❌ Request failed: {str(e)}")
                metrics.errors.append(str(e))
        
        stats = metrics.get_statistics()
        print(f"  Results: Avg={stats.get('avg', 'N/A')}s, P95={stats.get('p95', 'N/A')}s")
        performance_results.append(stats)
    
    print(f"\n✅ Filter performance test completed")


# =============================================================================
# Summary and Reporting
# =============================================================================

def generate_performance_report():
    """Generate detailed performance report"""
    print_header("PERFORMANCE TEST SUMMARY")
    
    if not performance_results:
        print("❌ No performance data collected")
        return
    
    # Count passed/failed tests
    passed_tests = 0
    failed_tests = 0
    
    print("\n📋 All Test Results:")
    print(f"{'Test Name':<40} {'Avg Time':<12} {'P95':<12} {'Status':<10}")
    print(f"{'─'*80}")
    
    for result in performance_results:
        test_name = result.get('test', 'Unknown')
        avg_time = result.get('avg', 0)
        p95_time = result.get('p95', 0)
        
        # Determine threshold
        threshold_key = test_name.split(':')[0].strip().lower().split('_')[0]
        threshold = THRESHOLDS.get(threshold_key, 2.0)
        
        # Check if passed
        if avg_time and avg_time <= threshold:
            status = "✅ PASS"
            passed_tests += 1
        elif avg_time:
            status = "❌ FAIL"
            failed_tests += 1
        else:
            status = "⚠️ ERROR"
            failed_tests += 1
        
        print(f"{test_name:<40} {avg_time:<12.3f} {p95_time:<12.3f} {status:<10}")
    
    print(f"{'─'*80}")
    print(f"\n📊 Summary:")
    print(f"  Total Tests:  {len(performance_results)}")
    print(f"  Passed:       {passed_tests} ✅")
    print(f"  Failed:       {failed_tests} ❌")
    print(f"  Success Rate: {(passed_tests/len(performance_results)*100):.1f}%")
    
    # Find slowest and fastest tests
    if performance_results:
        sorted_by_avg = sorted(
            [r for r in performance_results if r.get('avg')],
            key=lambda x: x.get('avg', 0)
        )
        
        if sorted_by_avg:
            print(f"\n🐌 Slowest Test:")
            slowest = sorted_by_avg[-1]
            print(f"  {slowest.get('test')}: {slowest.get('avg')}s (avg)")
            
            print(f"\n🚀 Fastest Test:")
            fastest = sorted_by_avg[0]
            print(f"  {fastest.get('test')}: {fastest.get('avg')}s (avg)")
    
    # Recommendations
    print(f"\n💡 Recommendations:")
    
    slow_tests = [r for r in performance_results if r.get('avg', 0) > 1.0]
    if slow_tests:
        print(f"  ⚠️ {len(slow_tests)} test(s) are slower than 1 second:")
        for test in slow_tests:
            print(f"     - {test.get('test')}: {test.get('avg')}s")
        print(f"  Consider optimizing database queries or adding caching.")
    else:
        print(f"  ✅ All tests are performing well (< 1s average)!")
    
    high_error_tests = [r for r in performance_results if r.get('error_rate', 0) > 5]
    if high_error_tests:
        print(f"\n  ⚠️ {len(high_error_tests)} test(s) have high error rates:")
        for test in high_error_tests:
            print(f"     - {test.get('test')}: {test.get('error_rate')}% errors")
    else:
        print(f"  ✅ Low error rates across all tests!")
    
    print(f"\n{'='*80}")


def save_performance_report():
    """Save performance report to markdown file"""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    report = f"""# Performance Test Report

**Date:** {timestamp}  
**Test Suite:** Truck Maintenance API Performance Tests

---

## Executive Summary

Total tests executed: {len(performance_results)}

### Performance Thresholds
"""
    
    for key, value in THRESHOLDS.items():
        report += f"- **{key}:** {value}s\n"
    
    report += f"\n### Test Configuration\n"
    report += f"- Concurrent Users: {CONCURRENT_USERS}\n"
    report += f"- Load Test Requests: {LOAD_TEST_REQUESTS}\n"
    report += f"- Base URL: {BASE_URL}\n"
    
    report += "\n---\n\n## Detailed Results\n\n"
    report += "| Test Name | Count | Min | Max | Avg | Median | P95 | P99 | Errors | Error Rate | Status |\n"
    report += "|-----------|-------|-----|-----|-----|--------|-----|-----|--------|------------|--------|\n"
    
    for result in performance_results:
        test_name = result.get('test', 'Unknown')
        count = result.get('count', 0)
        min_time = result.get('min', 'N/A')
        max_time = result.get('max', 'N/A')
        avg_time = result.get('avg', 'N/A')
        median = result.get('median', 'N/A')
        p95 = result.get('p95', 'N/A')
        p99 = result.get('p99', 'N/A')
        errors = result.get('errors', 0)
        error_rate = result.get('error_rate', 0)
        
        # Determine status
        threshold_key = test_name.split(':')[0].strip().lower().split('_')[0]
        threshold = THRESHOLDS.get(threshold_key, 2.0)
        
        if avg_time != 'N/A' and avg_time <= threshold:
            status = "✅ PASS"
        elif avg_time != 'N/A':
            status = "❌ FAIL"
        else:
            status = "⚠️ ERROR"
        
        report += f"| {test_name} | {count} | {min_time} | {max_time} | {avg_time} | {median} | {p95} | {p99} | {errors} | {error_rate}% | {status} |\n"
    
    # Performance Analysis
    report += "\n---\n\n## Performance Analysis\n\n"
    
    # Find slowest tests
    slow_tests = sorted(
        [r for r in performance_results if r.get('avg')],
        key=lambda x: x.get('avg', 0),
        reverse=True
    )[:5]
    
    if slow_tests:
        report += "### Slowest Tests (Top 5)\n\n"
        for i, test in enumerate(slow_tests, 1):
            report += f"{i}. **{test.get('test')}**: {test.get('avg')}s (avg), {test.get('max')}s (max)\n"
    
    # Find tests with high error rates
    error_tests = [r for r in performance_results if r.get('error_rate', 0) > 0]
    
    if error_tests:
        report += "\n### Tests with Errors\n\n"
        for test in error_tests:
            report += f"- **{test.get('test')}**: {test.get('errors')} errors ({test.get('error_rate')}%)\n"
    
    # Recommendations
    report += "\n---\n\n## Recommendations\n\n"
    
    slow_tests_1s = [r for r in performance_results if r.get('avg', 0) > 1.0]
    if slow_tests_1s:
        report += "### Performance Optimization\n\n"
        report += f"⚠️ {len(slow_tests_1s)} test(s) have average response times over 1 second:\n\n"
        for test in slow_tests_1s:
            report += f"- **{test.get('test')}**: {test.get('avg')}s\n"
        report += "\n**Suggestions:**\n"
        report += "1. Add database indexes on frequently queried fields\n"
        report += "2. Implement caching for read-heavy endpoints\n"
        report += "3. Optimize database queries (use EXPLAIN ANALYZE)\n"
        report += "4. Consider pagination for large result sets\n"
        report += "5. Use connection pooling for database connections\n"
    else:
        report += "✅ All tests are performing well with average response times under 1 second.\n"
    
    if error_tests:
        report += "\n### Error Handling\n\n"
        report += f"⚠️ {len(error_tests)} test(s) encountered errors during execution.\n\n"
        report += "**Suggestions:**\n"
        report += "1. Review server logs for error details\n"
        report += "2. Check database connection limits\n"
        report += "3. Verify rate limiting configuration\n"
        report += "4. Monitor server resources (CPU, memory, connections)\n"
    
    # Concurrent load analysis
    concurrent_tests = [r for r in performance_results if 'concurrent' in r.get('test', '').lower()]
    if concurrent_tests:
        report += "\n### Concurrent Load Analysis\n\n"
        for test in concurrent_tests:
            report += f"**{test.get('test')}:**\n"
            report += f"- Total Requests: {test.get('count')}\n"
            report += f"- Average Response Time: {test.get('avg')}s\n"
            report += f"- 95th Percentile: {test.get('p95')}s\n"
            report += f"- Error Rate: {test.get('error_rate')}%\n\n"
    
    report += "\n---\n\n## Conclusion\n\n"
    
    passed_count = sum(1 for r in performance_results if r.get('avg', 0) and r.get('avg', 0) <= THRESHOLDS.get(r.get('test', '').split(':')[0].strip().lower().split('_')[0], 2.0))
    total_count = len([r for r in performance_results if r.get('avg')])
    
    if total_count > 0:
        success_rate = (passed_count / total_count) * 100
        
        if success_rate >= 90:
            report += f"✅ **Excellent Performance**: {success_rate:.1f}% of tests passed performance thresholds.\n"
        elif success_rate >= 70:
            report += f"⚠️ **Good Performance**: {success_rate:.1f}% of tests passed, but some optimization needed.\n"
        else:
            report += f"❌ **Performance Issues**: Only {success_rate:.1f}% of tests passed. Significant optimization required.\n"
    
    report += f"\n**Test completed at:** {timestamp}\n"
    
    # Save to file
    filename = "PERFORMANCE_TEST_REPORT.md"
    with open(filename, 'w', encoding='utf-8') as f:
        f.write(report)
    
    print(f"\n📄 Detailed report saved to: {filename}")


# =============================================================================
# Main Test Runner
# =============================================================================

def main():
    """Run all performance tests"""
    print("="*80)
    print("  TRUCK MAINTENANCE API - PERFORMANCE TEST SUITE")
    print("="*80)
    print(f"\nTest Configuration:")
    print(f"  Base URL: {BASE_URL}")
    print(f"  Concurrent Users: {CONCURRENT_USERS}")
    print(f"  Load Test Requests: {LOAD_TEST_REQUESTS}")
    print(f"  Start Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Setup
    if not setup_admin_login():
        print("\n❌ Failed to authenticate admin. Cannot run authenticated tests.")
        print("   Make sure the backend server is running and admin user exists.")
        sys.exit(1)
    
    # Run all tests
    try:
        # Single request performance tests
        test_login_performance()
        test_get_users_performance()
        test_get_applications_performance()
        test_public_api_performance()
        
        # Concurrent request tests
        test_concurrent_login_requests()
        test_concurrent_read_requests()
        test_concurrent_authenticated_requests()
        
        # Database performance tests
        test_pagination_performance()
        test_filter_performance()
        
    except KeyboardInterrupt:
        print("\n\n⚠️ Tests interrupted by user")
    except Exception as e:
        print(f"\n\n❌ Unexpected error: {str(e)}")
        import traceback
        traceback.print_exc()
    
    # Generate reports
    generate_performance_report()
    save_performance_report()
    
    print(f"\n✅ Performance testing completed!")
    print(f"   End Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")


if __name__ == "__main__":
    main()

