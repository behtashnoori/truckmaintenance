# Performance Test Report

**Date:** 2025-10-09 14:01:36  
**Test Suite:** Truck Maintenance API Performance Tests

---

## Executive Summary

Total tests executed: 15

### Performance Thresholds
- **login:** 1.0s
- **get_users:** 2.0s
- **get_applications:** 2.0s
- **create_company:** 3.0s
- **search:** 1.5s
- **public_api:** 0.5s

### Test Configuration
- Concurrent Users: 10
- Load Test Requests: 50
- Base URL: http://localhost:5000/api

---

## Detailed Results

| Test Name | Count | Min | Max | Avg | Median | P95 | P99 | Errors | Error Rate | Status |
|-----------|-------|-----|-----|-----|--------|-----|-----|--------|------------|--------|
| login | 20 | 2.023 | 2.162 | 2.065 | 2.048 | 2.162 | 2.162 | 17 | 85.0% | ❌ FAIL |
| get_users | 20 | 2.022 | 2.096 | 2.059 | 2.058 | 2.096 | 2.096 | 0 | 0.0% | ❌ FAIL |
| get_applications | 20 | 2.038 | 2.079 | 2.05 | 2.048 | 2.079 | 2.079 | 20 | 100.0% | ❌ FAIL |
| public_api | 40 | 2.024 | 2.086 | 2.049 | 2.05 | 2.081 | 2.086 | 40 | 100.0% | ❌ FAIL |
| concurrent_login | 50 | 2.016 | 2.091 | 2.051 | 2.049 | 2.081 | 2.091 | 50 | 100.0% | ❌ FAIL |
| concurrent_reads | 50 | 2.018 | 2.206 | 2.06 | 2.051 | 2.197 | 2.206 | 50 | 100.0% | ❌ FAIL |
| concurrent_auth | 50 | 2.038 | 2.328 | 2.099 | 2.067 | 2.315 | 2.328 | 0 | 0.0% | ❌ FAIL |
| pagination_10 | 5 | 2.039 | 2.063 | 2.05 | 2.046 | 2.063 | 2.063 | 0 | 0.0% | ❌ FAIL |
| pagination_20 | 5 | 2.056 | 2.08 | 2.07 | 2.073 | 2.08 | 2.08 | 0 | 0.0% | ❌ FAIL |
| pagination_50 | 5 | 2.033 | 2.059 | 2.045 | 2.046 | 2.059 | 2.059 | 0 | 0.0% | ❌ FAIL |
| pagination_100 | 5 | 2.035 | 2.069 | 2.058 | 2.061 | 2.069 | 2.069 | 0 | 0.0% | ❌ FAIL |
| filter_No filters | 10 | 2.034 | 2.115 | 2.072 | 2.067 | 2.115 | 2.115 | 0 | 0.0% | ❌ FAIL |
| filter_Role filter | 10 | 2.035 | 2.117 | 2.066 | 2.066 | 2.117 | 2.117 | 0 | 0.0% | ❌ FAIL |
| filter_Active filter | 10 | 2.036 | 2.076 | 2.058 | 2.059 | 2.076 | 2.076 | 0 | 0.0% | ❌ FAIL |
| filter_Combined filters | 10 | 2.038 | 2.085 | 2.068 | 2.071 | 2.085 | 2.085 | 0 | 0.0% | ❌ FAIL |

---

## Performance Analysis

### Slowest Tests (Top 5)

1. **concurrent_auth**: 2.099s (avg), 2.328s (max)
2. **filter_No filters**: 2.072s (avg), 2.115s (max)
3. **pagination_20**: 2.07s (avg), 2.08s (max)
4. **filter_Combined filters**: 2.068s (avg), 2.085s (max)
5. **filter_Role filter**: 2.066s (avg), 2.117s (max)

### Tests with Errors

- **login**: 17 errors (85.0%)
- **get_applications**: 20 errors (100.0%)
- **public_api**: 40 errors (100.0%)
- **concurrent_login**: 50 errors (100.0%)
- **concurrent_reads**: 50 errors (100.0%)

---

## Recommendations

### Performance Optimization

⚠️ 15 test(s) have average response times over 1 second:

- **login**: 2.065s
- **get_users**: 2.059s
- **get_applications**: 2.05s
- **public_api**: 2.049s
- **concurrent_login**: 2.051s
- **concurrent_reads**: 2.06s
- **concurrent_auth**: 2.099s
- **pagination_10**: 2.05s
- **pagination_20**: 2.07s
- **pagination_50**: 2.045s
- **pagination_100**: 2.058s
- **filter_No filters**: 2.072s
- **filter_Role filter**: 2.066s
- **filter_Active filter**: 2.058s
- **filter_Combined filters**: 2.068s

**Suggestions:**
1. Add database indexes on frequently queried fields
2. Implement caching for read-heavy endpoints
3. Optimize database queries (use EXPLAIN ANALYZE)
4. Consider pagination for large result sets
5. Use connection pooling for database connections

### Error Handling

⚠️ 5 test(s) encountered errors during execution.

**Suggestions:**
1. Review server logs for error details
2. Check database connection limits
3. Verify rate limiting configuration
4. Monitor server resources (CPU, memory, connections)

### Concurrent Load Analysis

**concurrent_login:**
- Total Requests: 50
- Average Response Time: 2.051s
- 95th Percentile: 2.081s
- Error Rate: 100.0%

**concurrent_reads:**
- Total Requests: 50
- Average Response Time: 2.06s
- 95th Percentile: 2.197s
- Error Rate: 100.0%

**concurrent_auth:**
- Total Requests: 50
- Average Response Time: 2.099s
- 95th Percentile: 2.315s
- Error Rate: 0.0%


---

## Conclusion

❌ **Performance Issues**: Only 0.0% of tests passed. Significant optimization required.

**Test completed at:** 2025-10-09 14:01:36
