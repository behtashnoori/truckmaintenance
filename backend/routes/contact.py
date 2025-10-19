from flask import Blueprint, request, jsonify
from backend.models.content import ContentManagement
from backend.app import db
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import os

bp = Blueprint('contact', __name__)

@bp.route('/contact', methods=['POST'])
def submit_contact_form():
    """Submit contact form and send email"""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({
                'success': False,
                'error': 'داده‌های ارسالی نامعتبر است'
            }), 400
        
        # Validate required fields
        required_fields = ['name', 'email', 'message']
        for field in required_fields:
            if not data.get(field, '').strip():
                return jsonify({
                    'success': False,
                    'error': f'فیلد {field} الزامی است'
                }), 400
        
        # Get contact email from database
        contact_email_item = ContentManagement.query.filter_by(
            content_type='contact',
            section_key='contact_email',
            is_active=True
        ).first()
        
        if not contact_email_item:
            return jsonify({
                'success': False,
                'error': 'ایمیل تماس یافت نشد'
            }), 500
        
        contact_email = contact_email_item.content
        
        # Send email
        success = send_contact_email(
            to_email=contact_email,
            name=data['name'],
            email=data['email'],
            subject=data.get('subject', 'پیام جدید از وب‌سایت'),
            message=data['message']
        )
        
        if success:
            return jsonify({
                'success': True,
                'message': 'پیام شما با موفقیت ارسال شد'
            }), 200
        else:
            return jsonify({
                'success': False,
                'error': 'خطا در ارسال ایمیل'
            }), 500
            
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

def send_contact_email(to_email, name, email, subject, message):
    """Send contact form email"""
    try:
        # Email configuration
        smtp_server = os.getenv('SMTP_SERVER', 'smtp.gmail.com')
        smtp_port = int(os.getenv('SMTP_PORT', '587'))
        smtp_username = os.getenv('SMTP_USERNAME', '')
        smtp_password = os.getenv('SMTP_PASSWORD', '')
        
        # If no SMTP configured, just log and return success
        if not smtp_username or not smtp_password:
            print(f"Contact form submission: {name} ({email}) - {subject}")
            print(f"Message: {message}")
            print(f"Would send to: {to_email}")
            return True
        
        # Create message
        msg = MIMEMultipart()
        msg['From'] = smtp_username
        msg['To'] = to_email
        msg['Subject'] = f"پیام جدید از وب‌سایت: {subject}"
        
        # Create email body
        body = f"""
پیام جدید از فرم تماس وب‌سایت:

نام: {name}
ایمیل: {email}
موضوع: {subject}

پیام:
{message}

---
این پیام از طریق فرم تماس وب‌سایت ارسال شده است.
        """
        
        msg.attach(MIMEText(body, 'plain', 'utf-8'))
        
        # Send email
        server = smtplib.SMTP(smtp_server, smtp_port)
        server.starttls()
        server.login(smtp_username, smtp_password)
        text = msg.as_string()
        server.sendmail(smtp_username, to_email, text)
        server.quit()
        
        return True
        
    except Exception as e:
        print(f"Error sending email: {e}")
        return False

