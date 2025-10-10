"""Sync company schema with model

Revision ID: sync_company_schema
Revises: complete_company_model
Create Date: 2025-01-09 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'sync_company_schema'
down_revision = 'add_audit_trail'
branch_labels = None
depends_on = None


def upgrade():
    # Rename company_name to name
    op.alter_column('company', 'company_name', new_column_name='name')
    
    # Drop email and status columns if they exist
    try:
        op.drop_column('company', 'email')
    except:
        pass
    
    try:
        op.drop_column('company', 'status')
    except:
        pass


def downgrade():
    # Reverse the changes
    op.alter_column('company', 'name', new_column_name='company_name')
    
    # Add back email and status columns
    op.add_column('company', sa.Column('email', sa.String(length=100), nullable=True))
    op.add_column('company', sa.Column('status', sa.String(length=50), nullable=True))

