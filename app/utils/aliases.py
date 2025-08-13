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

# Reverse mappings for presenting slugs back to the UI.
CATEGORY_CANONICAL_TO_UI = {
    "roadside": "roadside",
    "tyre-wheel": "tyre-wheel",
    "recovery-accident": "recovery",
}

VEHICLE_CANONICAL_TO_UI = {
    "truck": "truck",
    "trailer": "semi",
    "bus": "bus",
}


def normalize_category(name: str) -> Optional[str]:
    """Return canonical category slug for a given alias."""
    return CATEGORY_ALIASES.get(name.lower())


def normalize_vehicle(name: str) -> Optional[str]:
    """Return canonical vehicle type slug for a given alias."""
    return VEHICLE_ALIASES.get(name.lower())


def ui_category(slug: str) -> str:
    """Return preferred UI alias for a canonical category slug."""
    return CATEGORY_CANONICAL_TO_UI.get(slug, slug)


def ui_vehicle(slug: str) -> str:
    """Return preferred UI alias for a canonical vehicle type slug."""
    return VEHICLE_CANONICAL_TO_UI.get(slug, slug)
