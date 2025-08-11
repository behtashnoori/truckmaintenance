"""Provider search endpoints."""
from flask import Blueprint, request
from sqlalchemy import select, func
from sqlalchemy.orm import selectinload

from ..db import get_db
from ..models import Provider, ServiceCategory, VehicleType
from ..utils.aliases import (
    normalize_category,
    normalize_vehicle,
    ui_category,
    ui_vehicle,
)


bp = Blueprint("providers", __name__)


@bp.get("/")
def list_providers():
    """Return providers ordered by distance with optional filtering."""

    lat = request.args.get("lat", type=float)
    lon = request.args.get("lon", type=float)
    if lat is None or lon is None:
        return {"error": "lat and lon required"}, 400

    category = request.args.get("category")
    vehicle_type = request.args.get("vehicleType")
    only247 = request.args.get("only24_7")
    if only247 is None:
        only247 = request.args.get("only247")

    limit = request.args.get("limit", default=20, type=int)
    limit = max(1, min(limit, 50))
    page = request.args.get("page", default=1, type=int)
    offset = (page - 1) * limit

    cat_slug = normalize_category(category) if category else None
    veh_slug = normalize_vehicle(vehicle_type) if vehicle_type else None
    only247_flag = (
        str(only247).lower() in {"1", "true", "t", "yes"}
        if only247 is not None
        else False
    )

    db = get_db()

    point_wkt = f"POINT({lon} {lat})"
    distance_m = func.STDistance(
        Provider.location, func.STPointFromText(point_wkt, 4326)
    )
    distance_km = distance_m / 1000.0

    stmt = (
        select(Provider, distance_km.label("distance_km"))
        .options(
            selectinload(Provider.categories),
            selectinload(Provider.vehicle_types),
        )
        .where(distance_km <= Provider.radius_km)
    )

    if cat_slug:
        stmt = stmt.join(Provider.categories).where(ServiceCategory.slug == cat_slug)
    if veh_slug:
        stmt = stmt.join(Provider.vehicle_types).where(VehicleType.slug == veh_slug)
    if only247_flag:
        stmt = stmt.where(Provider.is_24_7.is_(True))

    stmt = stmt.order_by(distance_km, Provider.name).limit(limit).offset(offset)

    rows = db.execute(stmt).all()

    providers = []
    for provider, dist in rows:
        providers.append(
            {
                "id": provider.id,
                "name": provider.name,
                "phone": provider.phone,
                "address": None,
                "distance_km": round(float(dist), 1),
                "is_24_7": provider.is_24_7,
                "vehicle_types": [
                    ui_vehicle(v.slug) for v in provider.vehicle_types
                ],
                "radius_km": provider.radius_km,
                "categories": [
                    ui_category(c.slug) for c in provider.categories
                ],
            }
        )

    return providers

