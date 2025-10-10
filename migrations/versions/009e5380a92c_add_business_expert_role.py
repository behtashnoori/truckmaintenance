"""add_business_expert_role

Revision ID: 009e5380a92c
Revises: complete_company_model
Create Date: 2025-10-08 22:21:27.538165

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '009e5380a92c'
down_revision = 'complete_company_model'
branch_labels = None
depends_on = None


def upgrade():
    # Drop the old constraint
    op.drop_constraint('users_role_check', 'users', type_='check')
    
    # Add the new constraint with business_expert role
    op.create_check_constraint(
        'users_role_check',
        'users',
        "role IN ('admin', 'support', 'business_expert')"
    )


def downgrade():
    # Drop the new constraint
    op.drop_constraint('users_role_check', 'users', type_='check')
    
    # Restore the old constraint
    op.create_check_constraint(
        'users_role_check',
        'users',
        "role IN ('admin', 'support')"
    )
