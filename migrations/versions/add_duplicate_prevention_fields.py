"""Add duplicate prevention fields and constraints to provider_application

Revision ID: add_duplicate_prevention
Revises: add_application_categories
Create Date: 2025-10-12 12:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy import text
from datetime import datetime, timezone


# revision identifiers, used by Alembic.
revision = 'add_duplicate_prevention'
down_revision = 'add_application_categories'
branch_labels = None
depends_on = None


def upgrade():
    """Add duplicate prevention fields and constraints"""
    connection = op.get_bind()
    inspector = sa.inspect(connection)
    
    # Get existing columns
    columns = {col['name']: col for col in inspector.get_columns('provider_application')}
    
    # Add new columns if they don't exist
    with op.batch_alter_table('provider_application', schema=None) as batch_op:
        
        # Add reapplication_count if it doesn't exist
        if 'reapplication_count' not in columns:
            batch_op.add_column(sa.Column('reapplication_count', sa.Integer(), nullable=False, server_default='1'))
        
        # Add last_submitted_at if it doesn't exist
        if 'last_submitted_at' not in columns:
            batch_op.add_column(sa.Column('last_submitted_at', sa.DateTime(), nullable=False, server_default=sa.func.now()))
        
        # Add fuzzy_match_warning if it doesn't exist
        if 'fuzzy_match_warning' not in columns:
            batch_op.add_column(sa.Column('fuzzy_match_warning', sa.Boolean(), nullable=True, server_default='false'))
        
        # Add similar_company_names if it doesn't exist
        if 'similar_company_names' not in columns:
            batch_op.add_column(sa.Column('similar_company_names', sa.Text(), nullable=True))
    
    # Handle existing duplicates before adding unique constraint
    # Find and mark duplicate phone numbers (keep oldest, mark others)
    duplicates = connection.execute(
        text("""
            SELECT phone_mobile, COUNT(*) as count
            FROM provider_application
            GROUP BY phone_mobile
            HAVING COUNT(*) > 1
        """)
    ).fetchall()
    
    if duplicates:
        print(f"Found {len(duplicates)} duplicate phone numbers. Handling duplicates...")
        
        for phone, count in duplicates:
            # Get all applications with this phone number, ordered by created_at
            apps = connection.execute(
                text("""
                    SELECT id, created_at, status
                    FROM provider_application
                    WHERE phone_mobile = :phone
                    ORDER BY created_at ASC
                """),
                {"phone": phone}
            ).fetchall()
            
            if len(apps) > 1:
                # Keep the first one (oldest), modify others
                oldest_id = apps[0][0]
                
                for i, (app_id, created_at, status) in enumerate(apps[1:], start=2):
                    # Append suffix to make phone unique for duplicates
                    new_phone = f"{phone}_dup_{i}"
                    connection.execute(
                        text("""
                            UPDATE provider_application 
                            SET phone_mobile = :new_phone,
                                review_notes = COALESCE(review_notes || E'\n', '') || 'شماره تکراری شناسایی شد. شماره اصلی: ' || :original_phone
                            WHERE id = :id
                        """),
                        {"new_phone": new_phone, "original_phone": phone, "id": app_id}
                    )
                    print(f"  Modified duplicate application ID {app_id}: {phone} -> {new_phone}")
    
    # Now add unique constraint and indexes
    with op.batch_alter_table('provider_application', schema=None) as batch_op:
        # Check if unique constraint doesn't already exist
        existing_constraints = [c['name'] for c in inspector.get_unique_constraints('provider_application')]
        
        if 'uq_provider_application_phone_mobile' not in existing_constraints:
            try:
                batch_op.create_unique_constraint('uq_provider_application_phone_mobile', ['phone_mobile'])
            except Exception as e:
                print(f"Warning: Could not create unique constraint: {e}")
        
        # Add indexes for better query performance
        existing_indexes = [idx['name'] for idx in inspector.get_indexes('provider_application')]
        
        if 'ix_provider_application_company_name' not in existing_indexes:
            batch_op.create_index('ix_provider_application_company_name', ['company_name'])
        
        if 'ix_provider_application_created_at' not in existing_indexes:
            batch_op.create_index('ix_provider_application_created_at', ['created_at'])


def downgrade():
    """Remove duplicate prevention fields and constraints"""
    
    with op.batch_alter_table('provider_application', schema=None) as batch_op:
        # Drop indexes
        batch_op.drop_index('ix_provider_application_company_name', if_exists=True)
        batch_op.drop_index('ix_provider_application_created_at', if_exists=True)
        
        # Drop unique constraint
        batch_op.drop_constraint('uq_provider_application_phone_mobile', type_='unique')
        
        # Drop columns
        batch_op.drop_column('similar_company_names')
        batch_op.drop_column('fuzzy_match_warning')
        batch_op.drop_column('last_submitted_at')
        batch_op.drop_column('reapplication_count')

