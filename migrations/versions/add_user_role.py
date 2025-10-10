"""Add user role to allowed roles

Revision ID: add_user_role
Revises: sync_company_schema
Create Date: 2025-01-09 12:00:00.000000

"""
from alembic import op


# revision identifiers, used by Alembic.
revision = 'add_user_role'
down_revision = 'sync_company_schema'
branch_labels = None
depends_on = None


def upgrade():
    # Drop the old constraint
    op.drop_constraint('users_role_check', 'users', type_='check')
    
    # Add the new constraint with 'user' role included
    op.create_check_constraint(
        'users_role_check',
        'users',
        "role IN ('admin', 'support', 'business_expert', 'user')"
    )


def downgrade():
    # Drop the new constraint
    op.drop_constraint('users_role_check', 'users', type_='check')
    
    # Restore the old constraint without 'user'
    op.create_check_constraint(
        'users_role_check',
        'users',
        "role IN ('admin', 'support', 'business_expert')"
    )

