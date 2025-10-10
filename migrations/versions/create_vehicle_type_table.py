"""Create vehicle_type table

Revision ID: create_vehicle_type_table
Revises: 36399b37d4f4
Create Date: 2025-10-09 19:15:00.000000

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = 'create_vehicle_type_table'
down_revision = '36399b37d4f4'
branch_labels = None
depends_on = None


def upgrade():
    # Create vehicle_type table
    op.create_table('vehicle_type',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(length=100), nullable=False),
        sa.Column('name_en', sa.String(length=100), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('icon', sa.String(length=50), nullable=True),
        sa.Column('capacity_min', sa.Integer(), nullable=True),
        sa.Column('capacity_max', sa.Integer(), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('name'),
        sa.UniqueConstraint('name_en')
    )


def downgrade():
    # Drop vehicle_type table
    op.drop_table('vehicle_type')

