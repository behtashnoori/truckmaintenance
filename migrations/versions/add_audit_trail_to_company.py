"""add_audit_trail_to_company

Revision ID: add_audit_trail
Revises: 009e5380a92c
Create Date: 2025-10-08 22:55:00.000000

"""
from alembic import op
import sqlalchemy as sa
from datetime import datetime, timezone


# revision identifiers, used by Alembic.
revision = 'add_audit_trail'
down_revision = '009e5380a92c'
branch_labels = None
depends_on = None


def upgrade():
    # Add audit trail columns to company table
    op.add_column('company', sa.Column('created_at', sa.DateTime(), nullable=False, 
                                       server_default=sa.text('CURRENT_TIMESTAMP')))
    op.add_column('company', sa.Column('updated_at', sa.DateTime(), nullable=False,
                                       server_default=sa.text('CURRENT_TIMESTAMP')))
    op.add_column('company', sa.Column('created_by', sa.Integer(), nullable=True))
    
    # Add foreign key constraint
    op.create_foreign_key(
        'fk_company_created_by_users',
        'company',
        'users',
        ['created_by'],
        ['id']
    )


def downgrade():
    # Drop foreign key constraint
    op.drop_constraint('fk_company_created_by_users', 'company', type_='foreignkey')
    
    # Drop audit trail columns
    op.drop_column('company', 'created_by')
    op.drop_column('company', 'updated_at')
    op.drop_column('company', 'created_at')

