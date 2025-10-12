"""Add many-to-many relationship for provider application categories

Revision ID: add_application_categories
Revises: create_vehicle_type_table
Create Date: 2025-10-11 12:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy import text


# revision identifiers, used by Alembic.
revision = 'add_application_categories'
down_revision = 'create_vehicle_type_table'
branch_labels = None
depends_on = None


def upgrade():
    # Check if tables exist before creating
    connection = op.get_bind()
    inspector = sa.inspect(connection)
    existing_tables = inspector.get_table_names()
    
    # Create category table if it doesn't exist
    if 'category' not in existing_tables:
        op.create_table('category',
            sa.Column('id', sa.Integer(), nullable=False),
            sa.Column('name', sa.String(length=100), nullable=False),
            sa.Column('icon', sa.String(length=50), nullable=True),
            sa.Column('description', sa.Text(), nullable=True),
            sa.Column('is_active', sa.Boolean(), nullable=False, server_default='true'),
            sa.PrimaryKeyConstraint('id'),
            sa.UniqueConstraint('name')
        )
    
    # Create association table for provider_application and category if it doesn't exist
    if 'provider_application_category' not in existing_tables:
        op.create_table('provider_application_category',
            sa.Column('application_id', sa.Integer(), nullable=False),
            sa.Column('category_id', sa.Integer(), nullable=False),
            sa.ForeignKeyConstraint(['application_id'], ['provider_application.id'], ondelete='CASCADE'),
            sa.ForeignKeyConstraint(['category_id'], ['category.id'], ondelete='CASCADE'),
            sa.PrimaryKeyConstraint('application_id', 'category_id')
        )
    
    # Check if service_domain column exists before migration
    columns = [col['name'] for col in inspector.get_columns('provider_application')]
    
    if 'service_domain' in columns:
        # Migrate existing service_domain data to the new relationship table
        # First, get all existing applications with their service_domain
        applications = connection.execute(
            text("SELECT id, service_domain FROM provider_application WHERE service_domain IS NOT NULL")
        ).fetchall()
        
        for app_id, service_domain in applications:
            if service_domain:
                # Find or create the category
                category_result = connection.execute(
                    text("SELECT id FROM category WHERE name = :name"),
                    {"name": service_domain}
                ).fetchone()
                
                if category_result:
                    category_id = category_result[0]
                else:
                    # Create new category
                    result = connection.execute(
                        text("INSERT INTO category (name) VALUES (:name) RETURNING id"),
                        {"name": service_domain}
                    )
                    category_id = result.fetchone()[0]
                
                # Insert into association table (check if not exists)
                existing = connection.execute(
                    text("SELECT 1 FROM provider_application_category WHERE application_id = :app_id AND category_id = :cat_id"),
                    {"app_id": app_id, "cat_id": category_id}
                ).fetchone()
                
                if not existing:
                    connection.execute(
                        text("INSERT INTO provider_application_category (application_id, category_id) VALUES (:app_id, :cat_id)"),
                        {"app_id": app_id, "cat_id": category_id}
                    )
        
        # Drop the old service_domain column
        with op.batch_alter_table('provider_application', schema=None) as batch_op:
            batch_op.drop_column('service_domain')


def downgrade():
    # Add back the service_domain column
    with op.batch_alter_table('provider_application', schema=None) as batch_op:
        batch_op.add_column(sa.Column('service_domain', sa.String(length=100), nullable=True))
    
    # Migrate data back (take first category if multiple)
    connection = op.get_bind()
    
    applications = connection.execute(
        text("""
            SELECT pac.application_id, c.name 
            FROM provider_application_category pac
            JOIN category c ON c.id = pac.category_id
        """)
    ).fetchall()
    
    # Group by application_id and take first category
    app_categories = {}
    for app_id, category_name in applications:
        if app_id not in app_categories:
            app_categories[app_id] = category_name
    
    # Update service_domain
    for app_id, category_name in app_categories.items():
        connection.execute(
            text("UPDATE provider_application SET service_domain = :name WHERE id = :id"),
            {"name": category_name, "id": app_id}
        )
    
    # Drop the association table
    op.drop_table('provider_application_category')

