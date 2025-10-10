"""Add extended fields to Company model

Revision ID: add_company_extended_fields
Revises: sync_company_schema
Create Date: 2025-10-09 19:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = 'add_company_extended_fields'
down_revision = 'sync_company_schema'
branch_labels = None
depends_on = None


def upgrade():
    # Add company_name column (allowing NULL initially)
    op.add_column('company', sa.Column('company_name', sa.String(length=255), nullable=True))
    
    # Copy data from name to company_name for existing records
    op.execute("UPDATE company SET company_name = name WHERE company_name IS NULL")
    
    # Now make it non-nullable
    op.alter_column('company', 'company_name', nullable=False)
    
    # Add service_radius_km with default value
    op.add_column('company', sa.Column('service_radius_km', sa.Float(), nullable=False, server_default='50.0'))
    
    # Add is_24_7 with default value
    op.add_column('company', sa.Column('is_24_7', sa.Boolean(), nullable=False, server_default='false'))
    
    # Add vehicle_types as JSON
    op.add_column('company', sa.Column('vehicle_types', sa.JSON(), nullable=True))
    
    # Add description
    op.add_column('company', sa.Column('description', sa.Text(), nullable=True))
    
    # Add services
    op.add_column('company', sa.Column('services', sa.Text(), nullable=True))
    
    # Add working_hours
    op.add_column('company', sa.Column('working_hours', sa.String(length=200), nullable=True))


def downgrade():
    # Remove added columns
    op.drop_column('company', 'working_hours')
    op.drop_column('company', 'services')
    op.drop_column('company', 'description')
    op.drop_column('company', 'vehicle_types')
    op.drop_column('company', 'is_24_7')
    op.drop_column('company', 'service_radius_km')
    op.drop_column('company', 'company_name')

