"""Location helpers. Never log latitude, longitude, or raw WKT."""

from __future__ import annotations

import math
from typing import NamedTuple

from app.schemas.common import GeoPoint

_EARTH_RADIUS_M = 6_371_000


class LatLon(NamedTuple):
    latitude: float
    longitude: float


def geopoint_to_wkt(point: GeoPoint | None) -> str | None:
    """Store a WGS84 point as plain WKT ``POINT(lng lat)``. Do not log the values."""
    if point is None:
        return None
    return f"POINT({point.longitude} {point.latitude})"


def parse_point(value: object) -> LatLon | None:
    """Best-effort parse of WKT / EWKT strings. Returns None if GPS is absent."""
    if value is None:
        return None
    text = getattr(value, "data", None)
    if text is None and isinstance(value, str):
        text = value
    if not isinstance(text, str):
        return None
    stripped = text.strip()
    if stripped.upper().startswith("SRID=") and ";" in stripped:
        stripped = stripped.split(";", 1)[1].strip()
    if not stripped.upper().startswith("POINT"):
        return None
    inside = stripped[stripped.find("(") + 1 : stripped.rfind(")")]
    parts = inside.replace(",", " ").split()
    if len(parts) < 2:
        return None
    try:
        lon = float(parts[0])
        lat = float(parts[1])
    except ValueError:
        return None
    return LatLon(latitude=lat, longitude=lon)


def haversine_meters(a: LatLon, b: LatLon) -> float:
    """Great-circle distance in meters. Do not log the inputs."""
    phi1 = math.radians(a.latitude)
    phi2 = math.radians(b.latitude)
    d_phi = math.radians(b.latitude - a.latitude)
    d_lambda = math.radians(b.longitude - a.longitude)
    hav = (
        math.sin(d_phi / 2) ** 2
        + math.cos(phi1) * math.cos(phi2) * math.sin(d_lambda / 2) ** 2
    )
    return 2 * _EARTH_RADIUS_M * math.asin(math.sqrt(hav))


def same_city(left: str, right: str) -> bool:
    return left.strip().casefold() == right.strip().casefold()
