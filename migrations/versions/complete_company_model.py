"""Complete Company model and add Category

Revision ID: complete_company_model
Revises: 
Create Date: 2024-01-01 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'complete_company_model'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # Create category table
    op.create_table('category',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(length=100), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('name')
    )
    
    # Create company_category association table
    op.create_table('company_category',
        sa.Column('company_id', sa.Integer(), nullable=False),
        sa.Column('category_id', sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(['category_id'], ['category.id'], ),
        sa.ForeignKeyConstraint(['company_id'], ['company.id'], ),
        sa.PrimaryKeyConstraint('company_id', 'category_id')
    )
    
    # Add new columns to company table
    op.add_column('company', sa.Column('address', sa.Text(), nullable=False, server_default=''))
    op.add_column('company', sa.Column('phone_landline', sa.String(length=20), nullable=True))
    op.add_column('company', sa.Column('latitude', sa.Float(), nullable=False, server_default='0.0'))
    op.add_column('company', sa.Column('longitude', sa.Float(), nullable=False, server_default='0.0'))
    op.add_column('company', sa.Column('is_active', sa.Boolean(), nullable=False, server_default='true'))
    
    # Rename tel column to phone_mobile
    op.alter_column('company', 'tel', new_column_name='phone_mobile')
    
    # Update unique constraint
    op.drop_constraint('uq_company_tel', 'company', type_='unique')
    op.create_unique_constraint('uq_company_phone_mobile', 'company', ['phone_mobile'])


def downgrade():
    # Reverse the changes
    op.drop_constraint('uq_company_phone_mobile', 'company', type_='unique')
    op.create_unique_constraint('uq_company_tel', 'company', ['tel'])
    
    op.alter_column('company', 'phone_mobile', new_column_name='tel')
    
    op.drop_column('company', 'is_active')
    op.drop_column('company', 'longitude')
    op.drop_column('company', 'latitude')
    op.drop_column('company', 'phone_landline')
    op.drop_column('company', 'address')
    
    op.drop_table('company_category')
    op.drop_table('category')
