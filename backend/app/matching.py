"""Donor matching for an urgency (haversine / city; no PostGIS).

Default GPS radius: 15 km (15_000 m), overridable via MATCH_RADIUS_METERS.
When both hospital and donor have GPS WKT, use haversine distance in meters.
Otherwise fall back to a case-insensitive city match.

Never log phone numbers, GPS coordinates, or blood groups.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.enums import BloodGroup, MatchMethod
from app.geo import haversine_meters, parse_point, same_city
from app.models import Donor, Hospital

logger = logging.getLogger(__name__)

DEFAULT_RADIUS_METERS = 15_000

# Recipients can receive red cells from these donor groups (standard ABO/Rh).
_COMPATIBLE_DONORS: dict[BloodGroup, tuple[BloodGroup, ...]] = {
    BloodGroup.O_NEGATIVE: (BloodGroup.O_NEGATIVE,),
    BloodGroup.O_POSITIVE: (BloodGroup.O_NEGATIVE, BloodGroup.O_POSITIVE),
    BloodGroup.A_NEGATIVE: (BloodGroup.O_NEGATIVE, BloodGroup.A_NEGATIVE),
    BloodGroup.A_POSITIVE: (
        BloodGroup.O_NEGATIVE,
        BloodGroup.O_POSITIVE,
        BloodGroup.A_NEGATIVE,
        BloodGroup.A_POSITIVE,
    ),
    BloodGroup.B_NEGATIVE: (BloodGroup.O_NEGATIVE, BloodGroup.B_NEGATIVE),
    BloodGroup.B_POSITIVE: (
        BloodGroup.O_NEGATIVE,
        BloodGroup.O_POSITIVE,
        BloodGroup.B_NEGATIVE,
        BloodGroup.B_POSITIVE,
    ),
    BloodGroup.AB_NEGATIVE: (
        BloodGroup.O_NEGATIVE,
        BloodGroup.A_NEGATIVE,
        BloodGroup.B_NEGATIVE,
        BloodGroup.AB_NEGATIVE,
    ),
    BloodGroup.AB_POSITIVE: tuple(BloodGroup),
}


@dataclass(frozen=True)
class MatchResult:
    """A matched donor. Callers must not log phone / GPS / blood group."""

    donor: Donor
    method: MatchMethod
    distance_meters: float | None = None


def compatible_donor_groups(needed: BloodGroup) -> tuple[BloodGroup, ...]:
    """Donor groups that can give to ``needed``. Do not log ``needed``."""
    return _COMPATIBLE_DONORS[needed]


def donor_is_nearby(
    *,
    donor_has_location: bool,
    hospital_has_location: bool,
    distance_meters: float | None,
    cities_match: bool,
    radius_meters: int = DEFAULT_RADIUS_METERS,
) -> tuple[bool, MatchMethod | None]:
    """Decide GPS vs city fallback. Do not pass raw coordinates in."""
    if donor_has_location and hospital_has_location:
        if distance_meters is not None and distance_meters <= radius_meters:
            return True, MatchMethod.GPS
        return False, None
    if cities_match:
        return True, MatchMethod.CITY
    return False, None


def find_compatible_donors(
    session: Session,
    hospital: Hospital,
    needed: BloodGroup,
    radius_meters: int = DEFAULT_RADIUS_METERS,
) -> list[MatchResult]:
    """Return available compatible donors near the hospital.

    Always uses Python haversine / city rules so Text WKT works on Railway
    Postgres without PostGIS.
    """
    groups = compatible_donor_groups(needed)
    results = _find_in_python(session, hospital, groups, radius_meters)

    logger.info(
        "Matching finished: %s candidate(s), radius_m=%s (no PII logged)",
        len(results),
        radius_meters,
    )
    return results


def _base_donor_filter(groups: tuple[BloodGroup, ...]) -> list:
    return [Donor.is_available.is_(True), Donor.blood_group.in_(groups)]


def _find_in_python(
    session: Session,
    hospital: Hospital,
    groups: tuple[BloodGroup, ...],
    radius_meters: int,
) -> list[MatchResult]:
    donors = list(
        session.scalars(select(Donor).where(*_base_donor_filter(groups))).unique().all()
    )
    matched: list[MatchResult] = []
    for donor in donors:
        result = _classify_loaded_donor(donor, hospital, radius_meters)
        if result is not None:
            matched.append(result)
    return matched


def _classify_loaded_donor(
    donor: Donor,
    hospital: Hospital,
    radius_meters: int,
) -> MatchResult | None:
    donor_point = parse_point(donor.location)
    hospital_point = parse_point(hospital.location)
    distance: float | None = None
    if donor_point is not None and hospital_point is not None:
        distance = haversine_meters(donor_point, hospital_point)

    ok, method = donor_is_nearby(
        donor_has_location=donor.location is not None,
        hospital_has_location=hospital.location is not None,
        distance_meters=distance,
        cities_match=same_city(donor.city, hospital.city),
        radius_meters=radius_meters,
    )
    if not ok or method is None:
        return None
    return MatchResult(donor=donor, method=method, distance_meters=distance)
