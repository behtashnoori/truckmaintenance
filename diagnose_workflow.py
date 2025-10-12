#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Database Diagnostic Script for Provider Registration Workflow
Tests the complete workflow from application to company creation and category linking
"""

import sys
import os
import io

# Fix Unicode encoding for Windows console
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from backend.app import create_app, db
from backend.models.provider_application import ProviderApplication
from backend.models.company import Company, Category
from sqlalchemy import func, inspect

def print_section(title):
    """Print a formatted section header"""
    print("\n" + "=" * 70)
    print(f" {title}")
    print("=" * 70)

def check_model_fields(model_class, instance):
    """Check which fields are populated in a model instance"""
    mapper = inspect(model_class)
    fields = {}
    for column in mapper.columns:
        value = getattr(instance, column.name)
        fields[column.name] = value
    return fields

app = create_app()

with app.app_context():
    print_section("DATABASE DIAGNOSTIC REPORT")
    
    # 1. Provider Applications Summary
    print_section("1. Provider Applications Summary")
    apps = ProviderApplication.query.all()
    print(f"Total applications: {len(apps)}")
    
    pending = ProviderApplication.query.filter_by(status='pending').count()
    approved = ProviderApplication.query.filter_by(status='approved').count()
    rejected = ProviderApplication.query.filter_by(status='rejected').count()
    
    print(f"  • Pending:  {pending}")
    print(f"  • Approved: {approved}")
    print(f"  • Rejected: {rejected}")
    
    # 2. Companies Summary
    print_section("2. Companies Summary")
    companies = Company.query.all()
    print(f"Total companies: {len(companies)}")
    
    active = Company.query.filter_by(is_active=True).count()
    inactive = Company.query.filter_by(is_active=False).count()
    
    print(f"  • Active:   {active}")
    print(f"  • Inactive: {inactive}")
    
    # 3. Categories Summary
    print_section("3. Categories Summary")
    categories = Category.query.all()
    print(f"Total categories: {len(categories)}\n")
    
    for cat in categories:
        company_count = db.session.query(func.count(Company.id)).join(
            Company.categories
        ).filter(
            Category.id == cat.id,
            Company.is_active == True
        ).scalar() or 0
        print(f"  • {cat.name:30s} → {company_count} active companies")
    
    # 4. Detailed Approved Applications Check
    print_section("4. Approved Applications → Company Mapping")
    approved_apps = ProviderApplication.query.filter_by(status='approved').all()
    
    if not approved_apps:
        print("No approved applications found.")
    
    issues_found = []
    
    for app in approved_apps:
        print(f"\n📋 Application #{app.id}: {app.company_name}")
        print(f"   Phone: {app.phone_mobile}")
        print(f"   Categories: {[cat.name for cat in app.categories]}")
        print(f"   Approved at: {app.reviewed_at}")
        
        # Check if company exists
        company = Company.query.filter_by(phone_mobile=app.phone_mobile).first()
        if company:
            print(f"   ✅ Company found (ID: {company.id})")
            print(f"      name field:         '{company.name}'")
            print(f"      company_name field: '{company.company_name}'")
            print(f"      is_active:          {company.is_active}")
            print(f"      Categories linked:  {[cat.name for cat in company.categories]}")
            
            # Check for issues
            if not company.name and not company.company_name:
                issues_found.append(f"Company {company.id}: Both name fields are empty")
            if company.name != company.company_name:
                issues_found.append(f"Company {company.id}: name != company_name")
            if not company.is_active:
                issues_found.append(f"Company {company.id}: is_active=False")
            if len(company.categories) == 0:
                issues_found.append(f"Company {company.id}: No categories linked")
            if len(company.categories) != len(app.categories):
                issues_found.append(f"Company {company.id}: Category count mismatch ({len(company.categories)} vs {len(app.categories)})")
        else:
            print(f"   ❌ NO COMPANY FOUND!")
            issues_found.append(f"Application {app.id}: Approved but no company exists")
    
    # 5. Company Field Consistency Check
    print_section("5. Company Field Consistency Check")
    all_companies = Company.query.all()
    
    for company in all_companies:
        has_issues = False
        issue_list = []
        
        if not company.name:
            issue_list.append("name is NULL")
            has_issues = True
        if not company.company_name:
            issue_list.append("company_name is NULL")
            has_issues = True
        if company.name != company.company_name:
            issue_list.append(f"name '{company.name}' != company_name '{company.company_name}'")
            has_issues = True
        
        if has_issues:
            print(f"\n⚠️  Company #{company.id}:")
            for issue in issue_list:
                print(f"     • {issue}")
    
    if not any([not c.name or not c.company_name or c.name != c.company_name for c in all_companies]):
        print("✅ All companies have consistent name fields")
    
    # 6. Category Association Check
    print_section("6. Category Association Verification")
    
    for cat in categories:
        # Get companies through association
        associated_companies = Company.query.join(Company.categories).filter(
            Category.id == cat.id,
            Company.is_active == True
        ).all()
        
        print(f"\n📁 {cat.name}")
        if associated_companies:
            for company in associated_companies:
                print(f"   • Company #{company.id}: {company.name or company.company_name}")
        else:
            print(f"   (No active companies)")
    
    # 7. Issues Summary
    print_section("7. Issues Summary")
    
    if issues_found:
        print(f"❌ Found {len(issues_found)} issue(s):\n")
        for i, issue in enumerate(issues_found, 1):
            print(f"   {i}. {issue}")
    else:
        print("✅ No issues found! Database is consistent.")
    
    # 8. API Simulation Test
    print_section("8. API Query Simulation")
    print("Testing public/providers endpoint query logic:\n")
    
    for cat in categories:
        # Simulate the exact query from public.py
        query = Company.query.filter(Company.is_active == True)
        query = query.join(Company.categories).filter(Category.name == cat.name)
        companies_found = query.all()
        
        print(f"Category '{cat.name}':")
        print(f"  Query returned: {len(companies_found)} companies")
        
        if companies_found:
            for company in companies_found:
                print(f"    • {company.name or company.company_name} (ID: {company.id})")
        else:
            # Debug why no results
            all_active = Company.query.filter(Company.is_active == True).count()
            print(f"    ⚠️  No results (Total active companies: {all_active})")
    
    print_section("END OF DIAGNOSTIC REPORT")
    print()

