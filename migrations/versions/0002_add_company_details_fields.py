"""add additional company detail fields"""

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "0002"
down_revision = "0001"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("Company", sa.Column("Type_Of_Service", sa.String(length=255), nullable=True), schema="dbo")
    op.add_column("Company", sa.Column("Radius_Of_Activity", sa.Integer(), nullable=True), schema="dbo")
    op.add_column("Company", sa.Column("Working_Hours", sa.String(length=100), nullable=True), schema="dbo")
    op.add_column("Company", sa.Column("Vehicle_Type", sa.String(length=255), nullable=True), schema="dbo")
    op.add_column("Company", sa.Column("Date", sa.DateTime(), nullable=True), schema="dbo")


def downgrade() -> None:
    op.drop_column("Company", "Date", schema="dbo")
    op.drop_column("Company", "Vehicle_Type", schema="dbo")
    op.drop_column("Company", "Working_Hours", schema="dbo")
    op.drop_column("Company", "Radius_Of_Activity", schema="dbo")
    op.drop_column("Company", "Type_Of_Service", schema="dbo")

