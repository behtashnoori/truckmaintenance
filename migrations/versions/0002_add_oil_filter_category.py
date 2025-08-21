"""add oil filter category"""

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = "0002"
down_revision = "0001"
branch_labels = None
depends_on = None


def upgrade() -> None:
    service_category_table = sa.table(
        "service_category",
        sa.column("slug", sa.String),
        sa.column("name", sa.String),
    )
    op.bulk_insert(
        service_category_table,
        [
            {"slug": "oil-filter", "name": "oil-filter"},
        ],
    )


def downgrade() -> None:
    op.execute(
        sa.text("DELETE FROM service_category WHERE slug='oil-filter'")
    )
