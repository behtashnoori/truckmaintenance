#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Populate Location table with Iranian provinces and cities
"""
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from backend.app import create_app, db
from backend.models.location import Location

def populate_locations():
    """Populate location table with Iranian provinces and cities"""
    app = create_app()
    
    with app.app_context():
        # Check if locations already exist
        existing_count = Location.query.count()
        if existing_count > 0:
            print(f"⚠️  Location table already has {existing_count} records.")
            response = input("Do you want to clear and repopulate? (y/N): ")
            if response.lower() != 'y':
                print("❌ Operation cancelled.")
                return
            
            # Clear existing data
            Location.query.delete()
            db.session.commit()
            print("✅ Existing locations cleared.")
        
        # List of locations (provinces and major cities of Iran)
        locations_data = [
            { 'name': 'تهران', 'lat': 35.6892, 'lon': 51.3890, 'type': 'province' },
            { 'name': 'اصفهان', 'lat': 32.6539, 'lon': 51.6660, 'type': 'province' },
            { 'name': 'مشهد', 'lat': 36.2605, 'lon': 59.6168, 'type': 'province' },
            { 'name': 'شیراز', 'lat': 29.5918, 'lon': 52.5837, 'type': 'province' },
            { 'name': 'تبریز', 'lat': 38.0806, 'lon': 46.2919, 'type': 'province' },
            { 'name': 'کرج', 'lat': 35.8400, 'lon': 50.9391, 'type': 'city' },
            { 'name': 'قم', 'lat': 34.6399, 'lon': 50.8764, 'type': 'province' },
            { 'name': 'اهواز', 'lat': 31.3183, 'lon': 48.6706, 'type': 'province' },
            { 'name': 'کرمانشاه', 'lat': 34.3277, 'lon': 47.0778, 'type': 'province' },
            { 'name': 'ارومیه', 'lat': 37.5527, 'lon': 45.0761, 'type': 'province' },
            { 'name': 'زاهدان', 'lat': 29.4960, 'lon': 60.8629, 'type': 'province' },
            { 'name': 'رشت', 'lat': 37.2808, 'lon': 49.5832, 'type': 'province' },
            { 'name': 'کرمان', 'lat': 30.2839, 'lon': 57.0834, 'type': 'province' },
            { 'name': 'همدان', 'lat': 34.7992, 'lon': 48.5146, 'type': 'province' },
            { 'name': 'یزد', 'lat': 31.8974, 'lon': 54.3569, 'type': 'province' },
            { 'name': 'اردبیل', 'lat': 38.2512, 'lon': 48.2963, 'type': 'province' },
            { 'name': 'بندر عباس', 'lat': 27.1833, 'lon': 56.2667, 'type': 'province' },
            { 'name': 'سنندج', 'lat': 35.3142, 'lon': 46.9983, 'type': 'province' },
            { 'name': 'زنجان', 'lat': 36.6769, 'lon': 48.4963, 'type': 'province' },
            { 'name': 'گرگان', 'lat': 36.8456, 'lon': 54.4342, 'type': 'province' },
            { 'name': 'ساری', 'lat': 36.5633, 'lon': 53.0601, 'type': 'province' },
            { 'name': 'بابول', 'lat': 36.5450, 'lon': 52.6789, 'type': 'city' },
            { 'name': 'ایلام', 'lat': 33.6374, 'lon': 46.4227, 'type': 'province' },
            { 'name': 'بوشهر', 'lat': 28.9234, 'lon': 50.8203, 'type': 'province' },
            { 'name': 'بیرجند', 'lat': 32.8649, 'lon': 59.2262, 'type': 'province' },
            { 'name': 'خرم‌آباد', 'lat': 33.4878, 'lon': 48.3558, 'type': 'province' },
            { 'name': 'یاسوج', 'lat': 30.6680, 'lon': 51.5880, 'type': 'province' },
            { 'name': 'سمنان', 'lat': 35.5728, 'lon': 53.3971, 'type': 'province' },
            { 'name': 'قزوین', 'lat': 36.2669, 'lon': 50.0039, 'type': 'province' },
            { 'name': 'شاهرود', 'lat': 36.4181, 'lon': 54.9764, 'type': 'city' }
        ]
        
        # Add locations to database
        added_count = 0
        for loc_data in locations_data:
            location = Location(
                name=loc_data['name'],
                type=loc_data['type'],
                latitude=loc_data['lat'],
                longitude=loc_data['lon']
            )
            db.session.add(location)
            added_count += 1
        
        # Commit changes
        db.session.commit()
        print(f"✅ Successfully added {added_count} locations to the database!")
        print(f"   - Provinces: {sum(1 for loc in locations_data if loc['type'] == 'province')}")
        print(f"   - Cities: {sum(1 for loc in locations_data if loc['type'] == 'city')}")


if __name__ == '__main__':
    try:
        populate_locations()
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

