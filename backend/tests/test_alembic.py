"""Alembic revision chain is linear and matches the committed files."""

from pathlib import Path

from alembic.config import Config
from alembic.script import ScriptDirectory

BACKEND_DIR = Path(__file__).resolve().parents[1]


def test_alembic_single_head_linear_chain() -> None:
    config = Config(str(BACKEND_DIR / "alembic.ini"))
    config.set_main_option("script_location", str(BACKEND_DIR / "alembic"))
    script = ScriptDirectory.from_config(config)

    heads = script.get_heads()
    assert heads == ["011_admin"]

    chain = [revision.revision for revision in script.walk_revisions()]
    assert chain == [
        "011_admin",
        "010_listings",
        "009_creator_flags",
        "008_actions",
        "007_hub_events",
        "006_messaging_communities",
        "005_social_light",
        "004_users",
        "003_urgency_matches",
        "002_hospital_recognized",
        "001_mvp_schema",
    ]
    assert script.get_revision("011_admin").down_revision == "010_listings"
    assert script.get_revision("010_listings").down_revision == "009_creator_flags"
    assert script.get_revision("009_creator_flags").down_revision == "008_actions"
    assert script.get_revision("008_actions").down_revision == "007_hub_events"
    assert script.get_revision("007_hub_events").down_revision == (
        "006_messaging_communities"
    )
    assert script.get_revision("006_messaging_communities").down_revision == (
        "005_social_light"
    )
    assert script.get_revision("005_social_light").down_revision == "004_users"
    assert script.get_revision("004_users").down_revision == "003_urgency_matches"
    assert script.get_revision("003_urgency_matches").down_revision == (
        "002_hospital_recognized"
    )
    assert script.get_revision("002_hospital_recognized").down_revision == (
        "001_mvp_schema"
    )
    assert script.get_revision("001_mvp_schema").down_revision is None
