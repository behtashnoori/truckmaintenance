#!/usr/bin/env python
# -*- coding: utf-8 -*-
import sys
import io
import requests

if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

print('Testing API with new code...\n')

# Test 1: Categories
print('1. Testing categories endpoint:')
r = requests.get('http://localhost:5000/api/public/categories')
data = r.json()
print(f'   Status: {r.status_code}')
print(f'   Categories: {len(data.get("data", []))}')

# Find مکانیکی category
for cat in data.get('data', []):
    if cat['name'] == 'مکانیکی':
        print(f'   ✓ "مکانیکی" has {cat["companies_count"]} companies')
        break

# Test 2: Providers without location
print('\n2. Testing providers endpoint WITHOUT location (NEW CODE):')
r = requests.get('http://localhost:5000/api/public/providers', params={'category': 'مکانیکی'})
data = r.json()
print(f'   Status: {r.status_code}')
print(f'   Success: {data.get("success")}')
print(f'   Providers found: {len(data.get("data", []))}')

if data.get('data'):
    for provider in data['data']:
        print(f'   ✓ Provider: {provider["name"]} (Phone: {provider["phone"]})')
else:
    print('   ✗ NO PROVIDERS RETURNED!')

# Test 3: All categories
print('\n3. Testing all categories:')
categories_to_test = ['تعویض روغن', 'تعمیرات موتور', 'لوازم یدکی']
for cat_name in categories_to_test:
    r = requests.get('http://localhost:5000/api/public/providers', params={'category': cat_name})
    data = r.json()
    count = len(data.get('data', []))
    if count > 0:
        print(f'   ✓ {cat_name}: {count} providers')
    else:
        print(f'   - {cat_name}: 0 providers')

print('\n✅ Testing complete!')

