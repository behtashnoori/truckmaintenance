"""create dbo.Company table"""

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "0001"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "Company",
        sa.Column("Id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("Tel", sa.String(length=20), nullable=False),
        sa.Column("Name", sa.String(length=255), nullable=False),
        sa.UniqueConstraint("Tel", name="uq_company_tel"),
        schema="dbo",
    )


def downgrade() -> None:
    op.drop_table("Company", schema="dbo")

