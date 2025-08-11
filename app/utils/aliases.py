"""Helper utilities for mapping input aliases to canonical slugs."""
from typing import Optional

CATEGORY_ALIASES = {
    "roadside": "roadside",
    "tire": "tyre-wheel",
    "tyre-wheel": "tyre-wheel",
    "recovery": "recovery-accident",
    "recovery-accident": "recovery-accident",
}

VEHICLE_ALIASES = {
    "truck": "truck",
    "semi": "trailer",
    "trailer": "trailer",
    "bus": "bus",
}


def normalize_category(name: str) -> Optional[str]:
    """Return canonical category slug for a given alias."""
    return CATEGORY_ALIASES.get(name.lower())


def normalize_vehicle(name: str) -> Optional[str]:
    """Return canonical vehicle type slug for a given alias."""
    return VEHICLE_ALIASES.get(name.lower())
