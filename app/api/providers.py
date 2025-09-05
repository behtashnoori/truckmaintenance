"""Provider search and registration endpoints."""
from flask import Blueprint, request
from sqlalchemy import select, func
from sqlalchemy.orm import selectinload
import jwt
from geoalchemy2 import WKTElement

from ..config import JWT_SECRET
from ..db import get_db
from ..models import Company, Provider, ServiceCategory, VehicleType
from ..utils.aliases import (
    normalize_category,
    normalize_vehicle,
    ui_category,
    ui_vehicle,
)
from ..utils.errors import json_error


bp = Blueprint("providers", __name__)


def _auth_phone():
    """Return phone number from Authorization header JWT."""
    auth = request.headers.get("Authorization", "")
    parts = auth.split()
    if len(parts) != 2 or parts[0].lower() != "bearer":
        return None
    token = parts[1]
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=["HS256"])
    except jwt.PyJWTError:
        return None
    return payload.get("phone")


@bp.post("/company")
def register_company():
    """Store company information using a verified phone JWT."""
    token_phone = _auth_phone()
    if not token_phone:
        return json_error("unauthorized", "invalid or missing token", 401)

    data = request.get_json() or {}
    name = data.get("name")
    phone = data.get("phone")
    if not all([name, phone]):
        return json_error("invalid_request", "missing fields")
    if phone != token_phone:
        return json_error("phone_mismatch", "phone mismatch", 401)

    db = get_db()
    company = db.execute(select(Company).where(Company.phone == phone)).scalar_one_or_none()
    if company:
        company.name = name
    else:
        company = Company(name=name, phone=phone)
        db.add(company)
    db.commit()
    return {"id": company.id}


@bp.post("/")
def register_provider():
    """Register a new provider using a verified phone JWT."""
    token_phone = _auth_phone()
    if not token_phone:
        return json_error("unauthorized", "invalid or missing token", 401)

    data = request.get_json() or {}
    name = data.get("name")
    phone = data.get("phone")
    loc = data.get("location") or {}
    lat = loc.get("lat")
    lon = loc.get("lon")
    radius_km = int(data.get("radius_km", 50))
    categories = data.get("categories") or []
    is_24_7 = bool(data.get("is_24_7"))
    vehicle_types = data.get("vehicle_types") or []

    if not all([name, phone, lat is not None, lon is not None, categories, vehicle_types]):
        return json_error("invalid_request", "missing fields")
    if phone != token_phone:
        return json_error("phone_mismatch", "phone mismatch", 401)

    cat_slugs = []
    for cat in categories:
        slug = normalize_category(cat)
        if slug is None:
            return json_error("invalid_category", f"invalid category: {cat}")
        cat_slugs.append(slug)

    veh_slugs = []
    for veh in vehicle_types:
        slug = normalize_vehicle(veh)
        if slug is None:
            return json_error("invalid_vehicle_type", f"invalid vehicle type: {veh}")
        veh_slugs.append(slug)

    db = get_db()

    if db.execute(select(Provider).where(Provider.phone == phone)).first():
        return json_error("phone_exists", "phone exists")

    categories_db = db.execute(
        select(ServiceCategory).where(ServiceCategory.slug.in_(cat_slugs))
    ).scalars().all()
    if len(categories_db) != len(set(cat_slugs)):
        return json_error("unknown_category", "unknown category")

    vehicles_db = db.execute(
        select(VehicleType).where(VehicleType.slug.in_(veh_slugs))
    ).scalars().all()
    if len(vehicles_db) != len(set(veh_slugs)):
        return json_error("unknown_vehicle_type", "unknown vehicle type")

    company = db.execute(select(Company).where(Company.phone == phone)).scalar_one_or_none()
    if company:
        company.name = name
    else:
        company = Company(name=name, phone=phone)
        db.add(company)

    point = WKTElement(f"POINT({lon} {lat})", srid=4326)
    provider = Provider(
        name=name,
        phone=phone,
        location=point,
        radius_km=radius_km,
        is_24_7=is_24_7,
    )
    provider.categories = categories_db
    provider.vehicle_types = vehicles_db

    db.add(provider)
    db.commit()
    db.refresh(provider)
    return {"status": "pending", "id": provider.id}

@bp.get("/")
def list_providers():
    """Return providers ordered by distance with optional filtering."""

    lat = request.args.get("lat", type=float)
    lon = request.args.get("lon", type=float)
    if lat is None or lon is None:
        return json_error("invalid_request", "lat and lon required")

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
    if category and cat_slug is None:
        return json_error("invalid_category", f"invalid category: {category}")
    veh_slug = normalize_vehicle(vehicle_type) if vehicle_type else None
    if vehicle_type and veh_slug is None:
        return json_error(
            "invalid_vehicle_type", f"invalid vehicle type: {vehicle_type}"
        )
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
    count_stmt = select(func.count(func.distinct(Provider.id))).where(
        distance_km <= Provider.radius_km
    )

    if cat_slug:
        stmt = stmt.join(Provider.categories).where(ServiceCategory.slug == cat_slug)
        count_stmt = count_stmt.join(Provider.categories).where(
            ServiceCategory.slug == cat_slug
        )
    if veh_slug:
        stmt = stmt.join(Provider.vehicle_types).where(VehicleType.slug == veh_slug)
        count_stmt = count_stmt.join(Provider.vehicle_types).where(
            VehicleType.slug == veh_slug
        )
    if only247_flag:
        stmt = stmt.where(Provider.is_24_7.is_(True))
        count_stmt = count_stmt.where(Provider.is_24_7.is_(True))

    total = db.execute(count_stmt).scalar()
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

    if "page" in request.args:
        return {
            "items": providers,
            "page": page,
            "page_size": limit,
            "total": int(total or 0),
        }
    return providers


@bp.get("/<int:provider_id>")
def get_provider(provider_id: int):
    """Return detailed information for a provider."""

    lat = request.args.get("lat", type=float)
    lon = request.args.get("lon", type=float)
    include_distance = lat is not None and lon is not None

    db = get_db()

    stmt = (
        select(
            Provider,
            func.STX(Provider.location).label("lon"),
            func.STY(Provider.location).label("lat"),
        )
        .options(
            selectinload(Provider.categories),
            selectinload(Provider.vehicle_types),
        )
        .where(Provider.id == provider_id)
    )

    if include_distance:
        point_wkt = f"POINT({lon} {lat})"
        distance_m = func.STDistance(
            Provider.location, func.STPointFromText(point_wkt, 4326)
        )
        stmt = stmt.add_columns((distance_m / 1000.0).label("distance_km"))

    row = db.execute(stmt).first()
    if row is None:
        return json_error("not_found", "provider not found", 404)

    if include_distance:
        provider, prov_lon, prov_lat, dist = row
    else:
        provider, prov_lon, prov_lat = row
        dist = None

    data = {
        "id": provider.id,
        "name": provider.name,
        "phone": provider.phone,
        "address": None,
        "is_24_7": provider.is_24_7,
        "vehicle_types": [ui_vehicle(v.slug) for v in provider.vehicle_types],
        "radius_km": provider.radius_km,
        "categories": [ui_category(c.slug) for c in provider.categories],
        "location": {"lat": float(prov_lat), "lon": float(prov_lon)},
    }

    if dist is not None:
        data["distance_km"] = round(float(dist), 1)

    return data

