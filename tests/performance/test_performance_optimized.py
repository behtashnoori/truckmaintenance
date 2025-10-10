#!/usr/bin/env python3
"""
Optimized Performance Testing Suite using Flask Test Client
This avoids network overhead and rate limiting issues
"""
from backend.app import create_app, db
from backend.models.user import User
import json
import time
import statistics
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed
import sys

# Performance thresholds (in seconds) - adjusted for test client
THRESHOLDS = {
    "login": 0.5,            # Should be very fast with test client
    "get_users": 0.5,       
    "get_applications": 0.5,
    "create_company": 1.0,  
    "search": 0.5,          
    "public_api": 0.2        
}

# Test configuration
CONCURRENT_USERS = 5
LOAD_TEST_REQUESTS = 20  # Reduced for faster testing

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
            "min": round(min(self.response_times) * 1000, 2),  # Convert to ms
            "max": round(max(self.response_times) * 1000, 2),
            "avg": round(statistics.mean(self.response_times) * 1000, 2),
            "median": round(statistics.median(self.response_times) * 1000, 2),
            "p95": round(self.calculate_percentile(95) * 1000, 2),
            "p99": round(self.calculate_percentile(99) * 1000, 2),
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
    print(f"  Min Time:       {metrics.get('min', 'N/A')} ms")
    print(f"  Max Time:       {metrics.get('max', 'N/A')} ms")
    print(f"  Avg Time:       {metrics.get('avg', 'N/A')} ms")
    print(f"  Median Time:    {metrics.get('median', 'N/A')} ms")
    print(f"  95th %ile:      {metrics.get('p95', 'N/A')} ms")
    print(f"  99th %ile:      {metrics.get('p99', 'N/A')} ms")
    print(f"  Errors:         {metrics.get('errors', 0)} ({metrics.get('error_rate', 0)}%)")
    
    # Check threshold (convert threshold to ms)
    avg_time_ms = metrics.get('avg', 0)
    avg_time_s = avg_time_ms / 1000
    threshold = THRESHOLDS.get(metrics['test'].split(':')[0].strip().lower().split('_')[0], 0.5)
    
    if avg_time_ms and avg_time_s <= threshold:
        print(f"  Status:         ✅ PASS (threshold: {threshold*1000}ms)")
    elif avg_time_ms:
        print(f"  Status:         ❌ FAIL (threshold: {threshold*1000}ms)")
    print(f"{'─'*80}")


# Create Flask app and test client
app = create_app()
app.config['TESTING'] = True  # Disable rate limiting
client = app.test_client()


def setup_admin_login():
    """Login as admin and get token"""
    global admin_token
    print_header("Setup: Admin Authentication")
    
    try:
        response = client.post(
            '/api/login',
            data=json.dumps({"username": "admin", "password": "admin123"}),
            content_type='application/json'
        )
        
        if response.status_code == 200:
            data = json.loads(response.get_data(as_text=True))
            admin_token = data.get('token')
            print(f"✅ Admin login successful")
            return True
        else:
            print(f"❌ Admin login failed: {response.status_code}")
            print(f"   Response: {response.get_data(as_text=True)}")
            return False
    except Exception as e:
        print(f"❌ Admin login error: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


def test_login_performance():
    """Test 1: Login endpoint performance"""
    print_header("Test 1: Login Performance")
    metrics = PerformanceMetrics("login")
    
    # Test multiple login requests
    for i in range(100):
        try:
            start = time.perf_counter()
            response = client.post(
                '/api/login',
                data=json.dumps({"username": "admin", "password": "admin123"}),
                content_type='application/json'
            )
            duration = time.perf_counter() - start
            metrics.add_response_time(duration, response.status_code)
            
            if (i + 1) % 25 == 0:
                print(f"  Completed {i + 1}/100 requests...")
        
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
    
    # Test with different pagination parameters
    test_params = [
        {"page": 1, "per_page": 10},
        {"page": 1, "per_page": 20},
        {"page": 1, "per_page": 50},
    ]
    
    for i in range(30):  # 30 iterations
        for params in test_params:
            try:
                query_string = '&'.join([f"{k}={v}" for k, v in params.items()])
                
                start = time.perf_counter()
                response = client.get(
                    f'/api/users?{query_string}',
                    headers={"Authorization": f"Bearer {admin_token}"}
                )
                duration = time.perf_counter() - start
                metrics.add_response_time(duration, response.status_code)
            
            except Exception as e:
                print(f"  ❌ Request failed: {str(e)}")
                metrics.errors.append(str(e))
        
        if (i + 1) % 10 == 0:
            print(f"  Completed {(i + 1) * len(test_params)}/{30 * len(test_params)} requests...")
    
    stats = metrics.get_statistics()
    print_metrics(stats)
    performance_results.append(stats)
    return stats


def test_public_api_performance():
    """Test 3: Public API endpoints performance"""
    print_header("Test 3: Public API Performance")
    
    metrics = PerformanceMetrics("public_api")
    
    # Test different public endpoints
    endpoints = [
        "/api/public/health",
        "/api/public/categories",
        "/api/public/providers?limit=10",
    ]
    
    for i in range(50):  # 50 iterations
        for endpoint in endpoints:
            try:
                start = time.perf_counter()
                response = client.get(endpoint)
                duration = time.perf_counter() - start
                metrics.add_response_time(duration, response.status_code)
            
            except Exception as e:
                print(f"  ❌ Request to {endpoint} failed: {str(e)}")
                metrics.errors.append(str(e))
        
        if (i + 1) % 15 == 0:
            print(f"  Completed {(i + 1) * len(endpoints)}/{50 * len(endpoints)} requests...")
    
    stats = metrics.get_statistics()
    print_metrics(stats)
    performance_results.append(stats)
    return stats


def test_database_query_performance():
    """Test 4: Direct database query performance"""
    print_header("Test 4: Database Query Performance")
    
    with app.app_context():
        metrics = PerformanceMetrics("database_queries")
        
        for i in range(100):
            try:
                start = time.perf_counter()
                
                # Test common queries
                users = User.query.limit(20).all()
                admin_users = User.query.filter_by(role='admin').all()
                active_users = User.query.filter_by(is_active=True).limit(10).all()
                
                duration = time.perf_counter() - start
                metrics.add_response_time(duration, 200)
            
            except Exception as e:
                print(f"  ❌ Query {i + 1} failed: {str(e)}")
                metrics.errors.append(str(e))
            
            if (i + 1) % 25 == 0:
                print(f"  Completed {i + 1}/100 queries...")
        
        stats = metrics.get_statistics()
        print_metrics(stats)
        performance_results.append(stats)
        return stats


def test_pagination_performance():
    """Test 5: Pagination performance with different page sizes"""
    print_header("Test 5: Pagination Performance")
    
    if not admin_token:
        print("❌ Skipping - no admin token")
        return None
    
    page_sizes = [10, 20, 50, 100]
    
    for per_page in page_sizes:
        metrics = PerformanceMetrics(f"pagination_{per_page}")
        
        print(f"\n  Testing with per_page={per_page}...")
        
        for page in range(1, 11):  # Test first 10 pages
            try:
                start = time.perf_counter()
                response = client.get(
                    f'/api/users?page={page}&per_page={per_page}',
                    headers={"Authorization": f"Bearer {admin_token}"}
                )
                duration = time.perf_counter() - start
                metrics.add_response_time(duration, response.status_code)
            
            except Exception as e:
                print(f"  ❌ Request failed: {str(e)}")
                metrics.errors.append(str(e))
        
        stats = metrics.get_statistics()
        print(f"  Results for per_page={per_page}: Avg={stats.get('avg', 'N/A')}ms, P95={stats.get('p95', 'N/A')}ms")
        performance_results.append(stats)
    
    print(f"\n✅ Pagination performance test completed")


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
    print(f"{'Test Name':<40} {'Avg (ms)':<12} {'P95 (ms)':<12} {'Status':<10}")
    print(f"{'─'*80}")
    
    for result in performance_results:
        test_name = result.get('test', 'Unknown')
        avg_time_ms = result.get('avg', 0)
        p95_time_ms = result.get('p95', 0)
        
        # Determine threshold
        threshold_key = test_name.split(':')[0].strip().lower().split('_')[0]
        threshold_s = THRESHOLDS.get(threshold_key, 0.5)
        threshold_ms = threshold_s * 1000
        
        # Check if passed
        if avg_time_ms and avg_time_ms <= threshold_ms:
            status = "✅ PASS"
            passed_tests += 1
        elif avg_time_ms:
            status = "❌ FAIL"
            failed_tests += 1
        else:
            status = "⚠️ ERROR"
            failed_tests += 1
        
        print(f"{test_name:<40} {avg_time_ms:<12.2f} {p95_time_ms:<12.2f} {status:<10}")
    
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
            print(f"  {slowest.get('test')}: {slowest.get('avg')}ms (avg)")
            
            print(f"\n🚀 Fastest Test:")
            fastest = sorted_by_avg[0]
            print(f"  {fastest.get('test')}: {fastest.get('avg')}ms (avg)")
    
    # Recommendations
    print(f"\n💡 Recommendations:")
    
    slow_tests = [r for r in performance_results if r.get('avg', 0) > 100]
    if slow_tests:
        print(f"  ⚠️ {len(slow_tests)} test(s) are slower than 100ms:")
        for test in slow_tests:
            print(f"     - {test.get('test')}: {test.get('avg')}ms")
        print(f"  Consider optimizing database queries or adding indexes.")
    else:
        print(f"  ✅ All tests are performing well (< 100ms average)!")
    
    print(f"\n{'='*80}")


def main():
    """Run all performance tests"""
    print("="*80)
    print("  TRUCK MAINTENANCE API - OPTIMIZED PERFORMANCE TEST SUITE")
    print("="*80)
    print(f"\nTest Configuration:")
    print(f"  Using Flask Test Client (no network overhead)")
    print(f"  TESTING mode: Enabled (rate limiting disabled)")
    print(f"  Start Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Setup
    if not setup_admin_login():
        print("\n❌ Failed to authenticate admin.")
        sys.exit(1)
    
    # Run all tests
    try:
        test_login_performance()
        test_get_users_performance()
        test_public_api_performance()
        test_database_query_performance()
        test_pagination_performance()
        
    except KeyboardInterrupt:
        print("\n\n⚠️ Tests interrupted by user")
    except Exception as e:
        print(f"\n\n❌ Unexpected error: {str(e)}")
        import traceback
        traceback.print_exc()
    
    # Generate reports
    generate_performance_report()
    
    print(f"\n✅ Performance testing completed!")
    print(f"   End Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")


if __name__ == "__main__":
    main()

