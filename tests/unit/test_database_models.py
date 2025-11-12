from datetime import datetime

import pytest

pytest.importorskip("sqlalchemy")

from src.models.database import MusicCue, Podcast, get_session, init_db


def test_podcast_defaults_and_repr(tmp_path):
    podcast = Podcast(title="Episode 1")
    assert podcast.status == "pending"
    assert isinstance(podcast.created_at, datetime)
    assert "Episode 1" in repr(podcast)

    cue = MusicCue(podcast_id=1, description="Intro", timestamp=0.0)
    assert "MusicCue" in repr(cue)


def test_init_db_creates_sqlite_file(tmp_path):
    db_path = tmp_path / "podcasts.sqlite"
    engine = init_db(f"sqlite:///{db_path}")
    assert engine.url.database == str(db_path)
    assert db_path.exists()


def test_get_session_insert_and_query(tmp_path):
    db_path = tmp_path / "podcasts.sqlite"
    session = get_session(f"sqlite:///{db_path}")

    podcast = Podcast(title="Test Episode", script_path="script.txt")
    session.add(podcast)
    session.commit()

    saved = session.query(Podcast).first()
    assert saved.title == "Test Episode"

    cue = MusicCue(podcast_id=saved.id, description="Cue", timestamp=5.0, duration=3.0)
    session.add(cue)
    session.commit()

    saved_cue = session.query(MusicCue).first()
    assert saved_cue.description == "Cue"
    session.close()

