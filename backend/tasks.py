"""
Background tasks for bulk operations and notifications
"""
import os
import pandas as pd
import tempfile
from datetime import datetime
from celery import current_task
from backend.celery_app import celery_app
from backend.app import db
from backend.models.company import Company, Category
from backend.models.provider_application import ProviderApplication
from backend.models.user import User

@celery_app.task(bind=True, name='backend.tasks.process_bulk_upload')
def process_bulk_upload(self, file_path, user_id, task_id):
    """
    Process bulk upload of providers in background
    """
    try:
        # Update task status
        self.update_state(
            state='PROGRESS',
            meta={'status': 'Reading file...', 'progress': 10}
        )
        
        # Read Excel file
        df = pd.read_excel(file_path)
        
        # Update progress
        self.update_state(
            state='PROGRESS',
            meta={'status': 'Validating data...', 'progress': 20}
        )
        
        # Validate required columns
        required_columns = [
            'نام مجموعه', 'نام نماینده', 'نام خانوادگی نماینده', 
            'آدرس', 'شماره موبایل', 'حوزه خدمات', 
            'عرض جغرافیایی', 'طول جغرافیایی'
        ]
        
        missing_columns = [col for col in required_columns if col not in df.columns]
        if missing_columns:
            raise ValueError(f"Missing required columns: {missing_columns}")
        
        # Process each row
        total_rows = len(df)
        success_count = 0
        failed_count = 0
        errors = []
        
        for index, row in df.iterrows():
            try:
                # Update progress
                progress = 20 + (index / total_rows) * 70
                self.update_state(
                    state='PROGRESS',
                    meta={
                        'status': f'Processing row {index + 1}/{total_rows}...',
                        'progress': int(progress)
                    }
                )
                
                # Validate row data
                if pd.isna(row['نام مجموعه']) or pd.isna(row['شماره موبایل']):
                    failed_count += 1
                    errors.append(f"Row {index + 2}: Missing required data")
                    continue
                
                # Check if company already exists
                existing_company = Company.query.filter_by(
                    phone_mobile=str(row['شماره موبایل'])
                ).first()
                if existing_company:
                    failed_count += 1
                    errors.append(f"Row {index + 2}: Company with phone {row['شماره موبایل']} already exists")
                    continue
                
                # Get or create category
                service_domain = str(row['حوزه خدمات']).strip()
                category = Category.query.filter_by(name=service_domain).first()
                if not category:
                    category = Category(name=service_domain)
                    db.session.add(category)
                    db.session.flush()
                
                # Create company
                company = Company(
                    name=str(row['نام مجموعه']).strip(),
                    address=str(row['آدرس']).strip(),
                    phone_mobile=str(row['شماره موبایل']).strip(),
                    phone_landline=str(row['تلفن ثابت']).strip() if not pd.isna(row['تلفن ثابت']) else None,
                    latitude=float(row['عرض جغرافیایی']),
                    longitude=float(row['طول جغرافیایی']),
                    is_active=bool(row.get('وضعیت فعال', True))
                )
                
                company.categories.append(category)
                db.session.add(company)
                success_count += 1
                
            except Exception as e:
                failed_count += 1
                errors.append(f"Row {index + 2}: {str(e)}")
        
        # Commit all changes
        db.session.commit()
        
        # Clean up temp file
        if os.path.exists(file_path):
            os.remove(file_path)
        
        # Final result
        result = {
            'status': 'COMPLETED',
            'total': total_rows,
            'success': success_count,
            'failed': failed_count,
            'errors': errors[:10],  # Limit to first 10 errors
            'message': f'Bulk upload completed. {success_count} providers added successfully.'
        }
        
        return result
        
    except Exception as e:
        # Clean up temp file on error
        if os.path.exists(file_path):
            os.remove(file_path)
        
        return {
            'status': 'FAILED',
            'error': str(e),
            'message': 'Bulk upload failed due to an error.'
        }

@celery_app.task(name='backend.tasks.send_notification')
def send_notification(user_id, notification_type, data):
    """
    Send notification to user (email, SMS, etc.)
    """
    try:
        user = User.query.get(user_id)
        if not user:
            return {'status': 'FAILED', 'error': 'User not found'}
        
        # Here you would implement actual notification sending
        # For now, just log the notification
        print(f"Sending {notification_type} notification to user {user.username}: {data}")
        
        return {
            'status': 'SUCCESS',
            'message': f'Notification sent to {user.username}'
        }
        
    except Exception as e:
        return {
            'status': 'FAILED',
            'error': str(e)
        }

@celery_app.task(name='backend.tasks.cleanup_temp_files')
def cleanup_temp_files():
    """
    Clean up temporary files older than 1 hour
    """
    try:
        temp_dir = tempfile.gettempdir()
        current_time = datetime.now().timestamp()
        cleaned_count = 0
        
        for filename in os.listdir(temp_dir):
            if filename.startswith('bulk_upload_'):
                file_path = os.path.join(temp_dir, filename)
                file_age = current_time - os.path.getctime(file_path)
                
                # Delete files older than 1 hour
                if file_age > 3600:
                    os.remove(file_path)
                    cleaned_count += 1
        
        return {
            'status': 'SUCCESS',
            'message': f'Cleaned up {cleaned_count} temporary files'
        }
        
    except Exception as e:
        return {
            'status': 'FAILED',
            'error': str(e)
        }

@celery_app.task(name='backend.tasks.send_daily_reports')
def send_daily_reports():
    """
    Send daily reports to admins
    """
    try:
        # Get statistics
        total_applications = ProviderApplication.query.count()
        pending_applications = ProviderApplication.query.filter_by(status='pending').count()
        total_companies = Company.query.filter_by(is_active=True).count()
        
        # Get admin users
        admins = User.query.filter_by(role='admin', is_active=True).all()
        
        report_data = {
            'date': datetime.now().strftime('%Y-%m-%d'),
            'total_applications': total_applications,
            'pending_applications': pending_applications,
            'total_companies': total_companies
        }
        
        # Send report to each admin
        for admin in admins:
            send_notification.delay(admin.id, 'daily_report', report_data)
        
        return {
            'status': 'SUCCESS',
            'message': f'Daily reports sent to {len(admins)} admins'
        }
        
    except Exception as e:
        return {
            'status': 'FAILED',
            'error': str(e)
        }
