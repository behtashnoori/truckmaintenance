from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    ForeignKey,
    Integer,
    String,
    Table,
    UniqueConstraint,
)
from sqlalchemy.orm import declarative_base, relationship
from sqlalchemy.sql import func
from geoalchemy2 import Geography


Base = declarative_base()


class ServiceCategory(Base):
    __tablename__ = "service_category"

    id = Column(Integer, primary_key=True)
    slug = Column(String(50), unique=True, nullable=False)
    name = Column(String(100), nullable=False)


class VehicleType(Base):
    __tablename__ = "vehicle_type"

    id = Column(Integer, primary_key=True)
    slug = Column(String(50), unique=True, nullable=False)
    name = Column(String(100), nullable=False)


provider_category = Table(
    "provider_category",
    Base.metadata,
    Column("provider_id", ForeignKey("provider.id", ondelete="CASCADE"), primary_key=True),
    Column(
        "category_id",
        ForeignKey("service_category.id", ondelete="CASCADE"),
        primary_key=True,
    ),
    UniqueConstraint("provider_id", "category_id", name="uix_provider_category"),
)


provider_vehicle_type = Table(
    "provider_vehicle_type",
    Base.metadata,
    Column("provider_id", ForeignKey("provider.id", ondelete="CASCADE"), primary_key=True),
    Column(
        "vehicle_type_id",
        ForeignKey("vehicle_type.id", ondelete="CASCADE"),
        primary_key=True,
    ),
    UniqueConstraint("provider_id", "vehicle_type_id", name="uix_provider_vehicle_type"),
)


class Provider(Base):
    __tablename__ = "provider"

    id = Column(Integer, primary_key=True)
    name = Column(String(255), nullable=False)
    phone = Column(String(20), unique=True, nullable=False)
    location = Column(Geography(geometry_type="POINT", srid=4326))
    radius_km = Column(Integer, nullable=False, default=50)
    is_24_7 = Column(Boolean, nullable=False, default=False)
    created_at = Column(DateTime, nullable=False, server_default=func.now())

    categories = relationship(
        "ServiceCategory", secondary=provider_category, backref="providers"
    )
    vehicle_types = relationship(
        "VehicleType", secondary=provider_vehicle_type, backref="providers"
    )
