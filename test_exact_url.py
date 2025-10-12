#!/usr/bin/env python
# -*- coding: utf-8 -*-
import sys
import io
import requests
from urllib.parse import quote

if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

print('Testing exact URLs that browser would call...\n')

# Test 1: What frontend sends with slug "مکانیکی"
slug = "مکانیکی"
category_name = slug.replace('-', ' ')
print(f'1. Slug: "{slug}"')
print(f'   Category name: "{category_name}"')

# Test with URL encoding
url = f'http://localhost:5000/api/public/providers?category={quote(category_name)}'
print(f'   URL: {url}')

r = requests.get('http://localhost:5000/api/public/providers', params={'category': category_name})
print(f'   Status: {r.status_code}')
data = r.json()
print(f'   Success: {data.get("success")}')
print(f'   Providers: {len(data.get("data", []))}')

if data.get('data'):
    for p in data['data']:
        print(f'   ✓ {p["name"]}')
else:
    print(f'   Response: {data}')

# Test 2: Test with different slugs
print('\n2. Testing different slug formats:')
test_cases = [
    ('مکانیکی', 'مکانیکی'),
    ('تعویض-روغن', 'تعویض روغن'),
    ('لوازم-یدکی', 'لوازم یدکی'),
]

for slug, expected_name in test_cases:
    category_name = slug.replace('-', ' ')
    r = requests.get('http://localhost:5000/api/public/providers', params={'category': category_name})
    data = r.json()
    count = len(data.get('data', []))
    print(f'   Slug "{slug}" → Category "{category_name}" → {count} providers')

