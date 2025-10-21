#!/usr/bin/env python3
"""
Script to seed initial content data for contact and support pages
"""
import sys
import os

# Add the project root to the Python path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.app import create_app, db
from backend.models.content import ContentManagement
from datetime import datetime, timezone

def utc_now():
    return datetime.now(timezone.utc)

def seed_content_data():
    """Seed initial content data for contact and support pages"""
    app = create_app()
    
    with app.app_context():
        # Check if content already exists
        existing_contact = ContentManagement.query.filter_by(content_type='contact').first()
        existing_about = ContentManagement.query.filter_by(content_type='about').first()
        
        if existing_contact and existing_about:
            print("Content data already exists. Skipping seed.")
            return
        
        # Contact page content
        contact_content = [
            {
                'content_type': 'contact',
                'section_key': 'hero_title',
                'content': 'تماس با ما',
                'is_active': True
            },
            {
                'content_type': 'contact',
                'section_key': 'hero_description',
                'content': 'برای دریافت اطلاعات بیشتر و راهنمایی، با ما در تماس باشید',
                'is_active': True
            },
            {
                'content_type': 'contact',
                'section_key': 'contact_email',
                'content': 'info@truckmaintenance.com',
                'is_active': True
            },
            {
                'content_type': 'contact',
                'section_key': 'contact_phone',
                'content': '021-12345678',
                'is_active': True
            },
            {
                'content_type': 'contact',
                'section_key': 'contact_address',
                'content': 'تهران، خیابان ولیعصر، پلاک 123',
                'is_active': True
            },
            {
                'content_type': 'contact',
                'section_key': 'contact_hours',
                'content': 'شنبه تا پنجشنبه: 8:00 - 17:00',
                'is_active': True
            },
            {
                'content_type': 'contact',
                'section_key': 'contact_form_title',
                'content': 'فرم تماس',
                'is_active': True
            },
            {
                'content_type': 'contact',
                'section_key': 'contact_form_description',
                'content': 'پیام خود را از طریق فرم زیر برای ما ارسال کنید',
                'is_active': True
            }
        ]
        
        # About page content
        about_content = [
            {
                'content_type': 'about',
                'section_key': 'about_title',
                'content': 'درباره ما',
                'is_active': True
            },
            {
                'content_type': 'about',
                'section_key': 'about_description',
                'content': 'ما در زمینه خدمات اضطراری و تعمیرات خودروهای سنگین فعالیت می‌کنیم',
                'is_active': True
            },
            {
                'content_type': 'about',
                'section_key': 'about_mission',
                'content': 'ماموریت ما ارائه بهترین خدمات اضطراری و تعمیرات خودروهای سنگین است',
                'is_active': True
            },
            {
                'content_type': 'about',
                'section_key': 'about_vision',
                'content': 'چشم‌انداز ما تبدیل شدن به مرجع اصلی خدمات خودروهای سنگین در کشور است',
                'is_active': True
            },
            {
                'content_type': 'about',
                'section_key': 'about_values',
                'content': 'ارزش‌های ما شامل کیفیت، سرعت، اعتماد و رضایت مشتری است',
                'is_active': True
            },
            {
                'content_type': 'about',
                'section_key': 'about_history',
                'content': 'ما از سال 1400 فعالیت خود را در زمینه خدمات خودروهای سنگین آغاز کرده‌ایم',
                'is_active': True
            },
            {
                'content_type': 'about',
                'section_key': 'about_team',
                'content': 'تیم ما شامل متخصصان مجرب در زمینه تعمیرات و خدمات اضطراری است',
                'is_active': True
            },
            {
                'content_type': 'about',
                'section_key': 'about_achievements',
                'content': 'دستاوردهای ما شامل خدمت به بیش از 1000 مشتری و رضایت 95% آن‌ها است',
                'is_active': True
            },
            {
                'content_type': 'about',
                'section_key': 'about_contact',
                'content': 'برای ارتباط با ما می‌توانید از طریق تماس یا ایمیل اقدام کنید',
                'is_active': True
            },
            {
                'content_type': 'about',
                'section_key': 'about_address',
                'content': 'تهران، خیابان ولیعصر، پلاک 123',
                'is_active': True
            }
        ]
        
        # Insert contact content
        for item in contact_content:
            content_item = ContentManagement(
                content_type=item['content_type'],
                section_key=item['section_key'],
                content=item['content'],
                is_active=item['is_active'],
                created_at=utc_now(),
                updated_at=utc_now()
            )
            db.session.add(content_item)
        
        # Insert about content
        for item in about_content:
            content_item = ContentManagement(
                content_type=item['content_type'],
                section_key=item['section_key'],
                content=item['content'],
                is_active=item['is_active'],
                created_at=utc_now(),
                updated_at=utc_now()
            )
            db.session.add(content_item)
        
        try:
            db.session.commit()
            print("Content data seeded successfully!")
            print(f"Added {len(contact_content)} contact content items")
            print(f"Added {len(about_content)} about content items")
        except Exception as e:
            db.session.rollback()
            print(f"Error seeding content data: {e}")
            raise

if __name__ == '__main__':
    seed_content_data()
