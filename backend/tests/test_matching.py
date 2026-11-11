"""Matching rules: ABO/Rh compatibility, GPS radius, city fallback."""

from uuid import uuid4

from sqlalchemy.orm import Session

from app.enums import BloodGroup, MatchMethod
from app.geo import geopoint_to_wkt, parse_point
from app.matching import (
    DEFAULT_RADIUS_METERS,
    compatible_donor_groups,
    donor_is_nearby,
    find_compatible_donors,
)
from app.models import Donor, Hospital
from app.schemas.common import GeoPoint


def test_parse_point_accepts_wkt_and_ewkt() -> None:
    wkt = parse_point("POINT(2.42 6.37)")
    ewkt = parse_point("SRID=4326;POINT(2.42 6.37)")
    assert wkt == ewkt
    assert wkt is not None
    assert wkt.latitude == 6.37
    assert wkt.longitude == 2.42
    assert parse_point(None) is None


def test_default_radius_is_15_km() -> None:
    assert DEFAULT_RADIUS_METERS == 15_000


def test_o_negative_donates_only_o_negative() -> None:
    assert compatible_donor_groups(BloodGroup.O_NEGATIVE) == (BloodGroup.O_NEGATIVE,)


def test_ab_positive_receives_from_all() -> None:
    groups = compatible_donor_groups(BloodGroup.AB_POSITIVE)
    assert set(groups) == set(BloodGroup)


def test_o_positive_does_not_receive_a_positive() -> None:
    groups = compatible_donor_groups(BloodGroup.O_POSITIVE)
    assert BloodGroup.A_POSITIVE not in groups
    assert BloodGroup.O_NEGATIVE in groups
    assert BloodGroup.O_POSITIVE in groups


def test_gps_match_inside_radius() -> None:
    ok, method = donor_is_nearby(
        donor_has_location=True,
        hospital_has_location=True,
        distance_meters=4_000,
        cities_match=False,
        radius_meters=DEFAULT_RADIUS_METERS,
    )
    assert ok is True
    assert method is MatchMethod.GPS


def test_gps_rejects_outside_radius_even_if_same_city() -> None:
    ok, method = donor_is_nearby(
        donor_has_location=True,
        hospital_has_location=True,
        distance_meters=20_000,
        cities_match=True,
        radius_meters=DEFAULT_RADIUS_METERS,
    )
    assert ok is False
    assert method is None


def test_city_fallback_when_gps_missing() -> None:
    ok, method = donor_is_nearby(
        donor_has_location=False,
        hospital_has_location=True,
        distance_meters=None,
        cities_match=True,
    )
    assert ok is True
    assert method is MatchMethod.CITY


def test_no_match_when_no_gps_and_different_city() -> None:
    ok, method = donor_is_nearby(
        donor_has_location=False,
        hospital_has_location=False,
        distance_meters=None,
        cities_match=False,
    )
    assert ok is False
    assert method is None


def test_find_compatible_donors_gps_and_city_fallback(db_session: Session) -> None:
    hospital = Hospital(
        id=uuid4(),
        name="Hopital Demo",
        city="Zone Demo",
        is_recognized=True,
        location=geopoint_to_wkt(GeoPoint(latitude=6.37, longitude=2.42)),
    )
    gps_near = Donor(
        id=uuid4(),
        display_name="Donneur Demo GPS",
        blood_group=BloodGroup.O_NEGATIVE,
        phone="0190000021",
        city="Ville Demo",
        location=geopoint_to_wkt(GeoPoint(latitude=6.375, longitude=2.42)),
        is_available=True,
    )
    gps_far = Donor(
        id=uuid4(),
        display_name="Donneur Demo Hors Rayon",
        blood_group=BloodGroup.O_NEGATIVE,
        phone="0190000022",
        city="Zone Demo",
        location=geopoint_to_wkt(GeoPoint(latitude=6.60, longitude=2.42)),
        is_available=True,
    )
    city_only = Donor(
        id=uuid4(),
        display_name="Donneur Demo Ville",
        blood_group=BloodGroup.O_POSITIVE,
        phone="0190000023",
        city="zone demo",
        location=None,
        is_available=True,
    )
    db_session.add_all([hospital, gps_near, gps_far, city_only])
    db_session.commit()

    results = find_compatible_donors(
        db_session,
        hospital,
        BloodGroup.O_POSITIVE,
        radius_meters=DEFAULT_RADIUS_METERS,
    )
    by_id = {item.donor.id: item for item in results}
    assert set(by_id) == {gps_near.id, city_only.id}
    assert by_id[gps_near.id].method is MatchMethod.GPS
    assert by_id[city_only.id].method is MatchMethod.CITY
    assert gps_far.id not in by_id
