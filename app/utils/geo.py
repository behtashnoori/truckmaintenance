"""Geospatial helper utilities."""

from math import radians, sin, cos, sqrt, atan2


def calculate_distance(a, b):
    """Return haversine distance between two ``(lat, lon)`` points in km."""

    lat1, lon1 = a
    lat2, lon2 = b

    rlat1, rlon1, rlat2, rlon2 = map(radians, [lat1, lon1, lat2, lon2])
    dlat = rlat2 - rlat1
    dlon = rlon2 - rlon1

    hav = sin(dlat / 2) ** 2 + cos(rlat1) * cos(rlat2) * sin(dlon / 2) ** 2
    return 6371 * 2 * atan2(sqrt(hav), sqrt(1 - hav))
