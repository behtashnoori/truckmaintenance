"""Populate the database with demo provider data."""
from geoalchemy2 import WKTElement
from sqlalchemy.orm import Session

from app.db import SessionLocal
from app.models import Provider, ServiceCategory, VehicleType


PROVIDERS = [
    # Roadside assistance
    {
        "name": "Tehran Roadside 1",
        "phone": "+989110000001",
        "lat": 35.6892,
        "lon": 51.3890,
        "categories": ["roadside"],
        "vehicles": ["truck"],
        "is_24_7": True,
    },
    {
        "name": "Isfahan Roadside 1",
        "phone": "+989110000002",
        "lat": 32.6546,
        "lon": 51.6680,
        "categories": ["roadside"],
        "vehicles": ["truck", "trailer"],
        "is_24_7": False,
    },
    {
        "name": "Tabriz Roadside 1",
        "phone": "+989110000003",
        "lat": 38.0962,
        "lon": 46.2738,
        "categories": ["roadside"],
        "vehicles": ["truck"],
        "is_24_7": True,
    },
    {
        "name": "Tehran Roadside 2",
        "phone": "+989110000004",
        "lat": 35.7000,
        "lon": 51.4100,
        "categories": ["roadside"],
        "vehicles": ["truck", "bus"],
        "is_24_7": False,
    },
    {
        "name": "Isfahan Roadside 2",
        "phone": "+989110000005",
        "lat": 32.6600,
        "lon": 51.7000,
        "categories": ["roadside"],
        "vehicles": ["truck"],
        "is_24_7": True,
    },
    # Tyre and wheel services
    {
        "name": "Tehran Tyre 1",
        "phone": "+989120000001",
        "lat": 35.6893,
        "lon": 51.3900,
        "categories": ["tyre-wheel"],
        "vehicles": ["truck", "trailer"],
        "is_24_7": True,
    },
    {
        "name": "Isfahan Tyre 1",
        "phone": "+989120000002",
        "lat": 32.6550,
        "lon": 51.6700,
        "categories": ["tyre-wheel"],
        "vehicles": ["bus"],
        "is_24_7": False,
    },
    {
        "name": "Tabriz Tyre 1",
        "phone": "+989120000003",
        "lat": 38.0970,
        "lon": 46.2750,
        "categories": ["tyre-wheel"],
        "vehicles": ["truck"],
        "is_24_7": True,
    },
    {
        "name": "Tehran Tyre 2",
        "phone": "+989120000004",
        "lat": 35.7000,
        "lon": 51.4200,
        "categories": ["tyre-wheel"],
        "vehicles": ["trailer"],
        "is_24_7": False,
    },
    {
        "name": "Isfahan Tyre 2",
        "phone": "+989120000005",
        "lat": 32.6600,
        "lon": 51.7100,
        "categories": ["tyre-wheel"],
        "vehicles": ["truck", "bus"],
        "is_24_7": True,
    },
    # Recovery services
    {
        "name": "Tehran Recovery 1",
        "phone": "+989130000001",
        "lat": 35.6894,
        "lon": 51.3910,
        "categories": ["recovery-accident"],
        "vehicles": ["truck", "trailer"],
        "is_24_7": True,
    },
    {
        "name": "Isfahan Recovery 1",
        "phone": "+989130000002",
        "lat": 32.6560,
        "lon": 51.6720,
        "categories": ["recovery-accident"],
        "vehicles": ["truck"],
        "is_24_7": False,
    },
    {
        "name": "Tabriz Recovery 1",
        "phone": "+989130000003",
        "lat": 38.0980,
        "lon": 46.2760,
        "categories": ["recovery-accident"],
        "vehicles": ["truck", "bus"],
        "is_24_7": True,
    },
    {
        "name": "Tehran Recovery 2",
        "phone": "+989130000004",
        "lat": 35.7100,
        "lon": 51.4300,
        "categories": ["recovery-accident"],
        "vehicles": ["trailer"],
        "is_24_7": False,
    },
    {
        "name": "Isfahan Recovery 2",
        "phone": "+989130000005",
        "lat": 32.6700,
        "lon": 51.7200,
        "categories": ["recovery-accident"],
        "vehicles": ["truck"],
        "is_24_7": True,
    },
]


def create_provider(session: Session, data: dict, categories: dict, vehicles: dict) -> Provider:
    provider = Provider(
        name=data["name"],
        phone=data["phone"],
        location=WKTElement(f"POINT({data['lon']} {data['lat']})", srid=4326),
        radius_km=data.get("radius_km", 50),
        is_24_7=data.get("is_24_7", False),
    )
    provider.categories = [categories[c] for c in data["categories"]]
    provider.vehicle_types = [vehicles[v] for v in data["vehicles"]]
    return provider


def main() -> None:
    session = SessionLocal()
    try:
        session.query(Provider).delete()
        categories = {c.slug: c for c in session.query(ServiceCategory).all()}
        vehicles = {v.slug: v for v in session.query(VehicleType).all()}
        for pdata in PROVIDERS:
            provider = create_provider(session, pdata, categories, vehicles)
            session.add(provider)
        session.commit()
        print("Seed data inserted")
    finally:
        session.close()


if __name__ == "__main__":
    main()
