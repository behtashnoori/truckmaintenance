"""merge multiple heads

Revision ID: 36399b37d4f4
Revises: add_user_role, create_location_table
Create Date: 2025-10-09 19:08:03.523947

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '36399b37d4f4'
down_revision = ('add_user_role', 'create_location_table')
branch_labels = None
depends_on = None


def upgrade():
    pass


def downgrade():
    pass
