"""Create content management table

Revision ID: create_content_management_table
Revises: add_duplicate_prevention_fields
Create Date: 2025-01-15 10:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from datetime import datetime, timezone

# revision identifiers, used by Alembic.
revision = 'create_content_management_table'
down_revision = 'add_duplicate_prevention'
branch_labels = None
depends_on = None


def utc_now():
    return datetime.now(timezone.utc)


def upgrade():
    # Create content_management table
    op.create_table('content_management',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('content_type', sa.String(length=50), nullable=False),
        sa.Column('section_key', sa.String(length=100), nullable=False),
        sa.Column('content', sa.Text(), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.Column('updated_by', sa.Integer(), nullable=True),
        sa.ForeignKeyConstraint(['updated_by'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )

    # Insert default content using raw SQL
    connection = op.get_bind()
    
    # About content
    about_content = [
        ('about', 'hero_title', 'امداد کامیون'),
        ('about', 'hero_subtitle', 'پلتفرم جامع خدمات اضطراری و تعمیرات خودروهای سنگین'),
        ('about', 'mission_text', 'هدف ما ارائه سریع‌ترین و مطمئن‌ترین خدمات امداد و تعمیرات برای رانندگان کامیون و خودروهای سنگین در سراسر کشور است. ما معتقدیم که هر راننده‌ای حق دارد در هر زمان و مکان به خدمات با کیفیت دسترسی داشته باشد.'),
        ('about', 'team_text', 'تیم امداد کامیون متشکل از مهندسان، متخصصان فنی و کارشناسان مجرب در زمینه حمل‌ونقل و خدمات خودرویی است. ما با بیش از ۱۰ سال تجربه در این صنعت، به دنبال ایجاد راه‌حلی مدرن و کارآمد برای نیازهای رانندگان هستیم.'),
        ('about', 'feature_security', 'همه ارائه‌دهندگان خدمات ما تأیید شده و دارای مجوزهای لازم هستند'),
        ('about', 'feature_coverage', 'خدمات در تمام نقاط کشور و جاده‌های اصلی در دسترس است'),
        ('about', 'feature_quality', 'استانداردهای سخت‌گیرانه برای انتخاب و ارزیابی ارائه‌دهندگان'),
        ('about', 'feature_expertise', 'متمرکز بر نیازهای خاص خودروهای سنگین و تجاری'),
    ]

    contact_content = [
        ('contact', 'contact_phone', '۰۲۱-۱۲۳۴۵۶۷۸'),
        ('contact', 'contact_email', 'support@truckaid.ir'),
        ('contact', 'contact_address', 'تهران، خیابان ولیعصر، بالاتر از تقاطع پارک‌ساعی، پلاک ۱۲۳۴، طبقه ۵، واحد ۱۰'),
        ('contact', 'contact_postal_code', '۱۹۱۵۷-۴۴۴۱۱'),
        ('contact', 'working_hours_weekday', '۸:۰۰ - ۲۰:۰۰'),
        ('contact', 'working_hours_friday', '۱۰:۰۰ - ۱۸:۰۰'),
    ]

    # Insert about content
    for content_type, section_key, content_text in about_content:
        connection.execute(sa.text("""
            INSERT INTO content_management (content_type, section_key, content, is_active, created_at, updated_at)
            VALUES (:content_type, :section_key, :content, :is_active, :created_at, :updated_at)
        """), {
            'content_type': content_type,
            'section_key': section_key,
            'content': content_text,
            'is_active': True,
            'created_at': utc_now(),
            'updated_at': utc_now()
        })

    # Insert contact content
    for content_type, section_key, content_text in contact_content:
        connection.execute(sa.text("""
            INSERT INTO content_management (content_type, section_key, content, is_active, created_at, updated_at)
            VALUES (:content_type, :section_key, :content, :is_active, :created_at, :updated_at)
        """), {
            'content_type': content_type,
            'section_key': section_key,
            'content': content_text,
            'is_active': True,
            'created_at': utc_now(),
            'updated_at': utc_now()
        })


def downgrade():
    # Drop content_management table
    op.drop_table('content_management')
