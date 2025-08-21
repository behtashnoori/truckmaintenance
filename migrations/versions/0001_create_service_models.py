"""create service and provider tables"""
from alembic import op
import sqlalchemy as sa
from geoalchemy2 import Geography

# revision identifiers, used by Alembic.
revision = "0001"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "service_category",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("slug", sa.String(length=50), nullable=False, unique=True),
        sa.Column("name", sa.String(length=100), nullable=False),
    )

    op.create_table(
        "vehicle_type",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("slug", sa.String(length=50), nullable=False, unique=True),
        sa.Column("name", sa.String(length=100), nullable=False),
    )

    op.create_table(
        "provider",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("phone", sa.String(length=20), nullable=False, unique=True),
        sa.Column("location", Geography(geometry_type="POINT", srid=4326)),
        sa.Column("radius_km", sa.Integer(), nullable=False, server_default="50"),
        sa.Column("is_24_7", sa.Boolean(), nullable=False, server_default=sa.text("0")),
        sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.func.now()),
    )

    op.create_table(
        "provider_category",
        sa.Column(
            "provider_id",
            sa.Integer(),
            sa.ForeignKey("provider.id", ondelete="CASCADE"),
            primary_key=True,
        ),
        sa.Column(
            "category_id",
            sa.Integer(),
            sa.ForeignKey("service_category.id", ondelete="CASCADE"),
            primary_key=True,
        ),
        sa.UniqueConstraint("provider_id", "category_id", name="uix_provider_category"),
    )

    op.create_table(
        "provider_vehicle_type",
        sa.Column(
            "provider_id",
            sa.Integer(),
            sa.ForeignKey("provider.id", ondelete="CASCADE"),
            primary_key=True,
        ),
        sa.Column(
            "vehicle_type_id",
            sa.Integer(),
            sa.ForeignKey("vehicle_type.id", ondelete="CASCADE"),
            primary_key=True,
        ),
        sa.UniqueConstraint(
            "provider_id",
            "vehicle_type_id",
            name="uix_provider_vehicle_type",
        ),
    )

    op.execute(
        """CREATE SPATIAL INDEX IX_provider_location
        ON provider(location)
        USING GEOGRAPHY_AUTO_GRID
        WITH (BOUNDING_BOX = (-180,-90,180,90));"""
    )

    service_category_table = sa.table(
        "service_category",
        sa.column("slug", sa.String),
        sa.column("name", sa.String),
    )
    vehicle_type_table = sa.table(
        "vehicle_type",
        sa.column("slug", sa.String),
        sa.column("name", sa.String),
    )

    op.bulk_insert(
        service_category_table,
        [
            {"slug": "roadside", "name": "roadside"},
            {"slug": "tyre-wheel", "name": "tyre-wheel"},
            {"slug": "recovery-accident", "name": "recovery-accident"},
            {"slug": "oil-filter", "name": "oil-filter"},
        ],
    )

    op.bulk_insert(
        vehicle_type_table,
        [
            {"slug": "truck", "name": "truck"},
            {"slug": "trailer", "name": "trailer"},
            {"slug": "bus", "name": "bus"},
        ],
    )


def downgrade() -> None:
    op.execute("DROP INDEX IX_provider_location ON provider")
    op.drop_table("provider_vehicle_type")
    op.drop_table("provider_category")
    op.drop_table("provider")
    op.drop_table("vehicle_type")
    op.drop_table("service_category")
