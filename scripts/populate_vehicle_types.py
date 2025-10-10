#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Populate VehicleType table with default vehicle types
"""
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from backend.app import create_app, db
from backend.models.vehicle_type import VehicleType

def populate_vehicle_types():
    """Populate vehicle_type table with default types"""
    app = create_app()
    
    with app.app_context():
        # Check if vehicle types already exist
        existing_count = VehicleType.query.count()
        if existing_count > 0:
            print(f"⚠️  VehicleType table already has {existing_count} records.")
            response = input("Do you want to clear and repopulate? (y/N): ")
            if response.lower() != 'y':
                print("❌ Operation cancelled.")
                return
            
            # Clear existing data
            VehicleType.query.delete()
            db.session.commit()
            print("✅ Existing vehicle types cleared.")
        
        # Default vehicle types
        vehicle_types_data = [
            {
                'name': 'کامیون',
                'name_en': 'truck',
                'description': 'کامیون‌های سبک و سنگین برای حمل و نقل جاده‌ای',
                'icon': 'Truck',
                'capacity_min': 2,
                'capacity_max': 20
            },
            {
                'name': 'کشنده',
                'name_en': 'semi',
                'description': 'کامیون‌های کشنده و تریلر برای حمل‌های سنگین',
                'icon': 'Container',
                'capacity_min': 15,
                'capacity_max': 40
            },
            {
                'name': 'اتوبوس',
                'name_en': 'bus',
                'description': 'اتوبوس‌های مسافربری شهری و بین‌شهری',
                'icon': 'Bus',
                'capacity_min': 20,
                'capacity_max': 60
            }
        ]
        
        # Add vehicle types to database
        added_count = 0
        for vt_data in vehicle_types_data:
            vehicle_type = VehicleType(
                name=vt_data['name'],
                name_en=vt_data['name_en'],
                description=vt_data['description'],
                icon=vt_data['icon'],
                capacity_min=vt_data['capacity_min'],
                capacity_max=vt_data['capacity_max']
            )
            db.session.add(vehicle_type)
            added_count += 1
        
        # Commit changes
        db.session.commit()
        print(f"✅ Successfully added {added_count} vehicle types to the database!")
        for vt in vehicle_types_data:
            print(f"   - {vt['name']} ({vt['name_en']})")


if __name__ == '__main__':
    try:
        populate_vehicle_types()
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

