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
    assert heads == ["006_messaging_communities"]

    chain = [revision.revision for revision in script.walk_revisions()]
    assert chain == [
        "006_messaging_communities",
        "005_social_light",
        "004_users",
        "003_urgency_matches",
        "002_hospital_recognized",
        "001_mvp_schema",
    ]
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
