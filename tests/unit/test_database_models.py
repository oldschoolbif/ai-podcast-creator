from datetime import datetime
from pathlib import Path

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


# Check if sqlalchemy is available
try:
    import sqlalchemy
    SQLALCHEMY_AVAILABLE = True
except ImportError:
    SQLALCHEMY_AVAILABLE = False

@pytest.mark.skipif(not SQLALCHEMY_AVAILABLE, reason="sqlalchemy not installed")
class TestPodcastInitBranches:
    """Test Podcast __init__ method branches."""

    def test_podcast_init_with_status_provided(self):
        """Test Podcast __init__ when status is explicitly provided."""
        podcast = Podcast(title="Test", status="processing")
        
        assert podcast.status == "processing"
        assert podcast.title == "Test"

    def test_podcast_init_with_created_at_provided(self):
        """Test Podcast __init__ when created_at is explicitly provided."""
        custom_time = datetime(2023, 1, 1, 12, 0, 0)
        podcast = Podcast(title="Test", created_at=custom_time)
        
        assert podcast.created_at == custom_time
        assert podcast.status == "pending"  # Should still default

    def test_podcast_init_with_both_provided(self):
        """Test Podcast __init__ when both status and created_at are provided."""
        custom_time = datetime(2023, 1, 1, 12, 0, 0)
        podcast = Podcast(title="Test", status="completed", created_at=custom_time)
        
        assert podcast.status == "completed"
        assert podcast.created_at == custom_time


@pytest.mark.skipif(not SQLALCHEMY_AVAILABLE, reason="sqlalchemy not installed")
class TestInitDBBranches:
    """Test init_db branches."""

    def test_init_db_with_none_url_creates_data_dir(self, temp_dir):
        """Test init_db with None URL creates data directory."""
        import os
        original_cwd = os.getcwd()
        try:
            os.chdir(temp_dir)
            
            # Call init_db with None (default)
            engine = init_db(None)
            
            assert engine is not None
            data_dir = Path(temp_dir) / "data"
            assert data_dir.exists()
            assert data_dir.is_dir()
        finally:
            os.chdir(original_cwd)

    def test_init_db_with_none_url_creates_default_db_path(self, temp_dir):
        """Test init_db with None URL uses default database path."""
        import os
        original_cwd = os.getcwd()
        try:
            os.chdir(temp_dir)
            
            engine = init_db(None)
            
            # Verify it uses the default path (may be relative or absolute)
            db_path = engine.url.database
            expected_path = str(Path(temp_dir) / "data" / "podcasts.db")
            # SQLAlchemy may return relative path, so resolve both
            assert Path(db_path).resolve() == Path(expected_path).resolve()
        finally:
            os.chdir(original_cwd)


@pytest.mark.skipif(not SQLALCHEMY_AVAILABLE, reason="sqlalchemy not installed")
class TestGetSessionBranches:
    """Test get_session branches."""

    def test_get_session_with_none_url(self, temp_dir):
        """Test get_session with None URL uses default database."""
        import os
        original_cwd = os.getcwd()
        try:
            os.chdir(temp_dir)
            
            session = get_session(None)
            
            assert session is not None
            assert hasattr(session, "add")
            assert hasattr(session, "commit")
            assert hasattr(session, "query")
            
            # Verify it created the default database
            data_dir = Path(temp_dir) / "data"
            assert data_dir.exists()
            
            session.close()
        finally:
            os.chdir(original_cwd)

    def test_get_session_with_none_url_creates_default_db(self, temp_dir):
        """Test get_session with None URL creates default database file."""
        import os
        original_cwd = os.getcwd()
        try:
            os.chdir(temp_dir)
            
            session = get_session(None)
            
            # Add and commit something to ensure DB file is created
            podcast = Podcast(title="Test Session")
            session.add(podcast)
            session.commit()
            
            db_file = Path(temp_dir) / "data" / "podcasts.db"
            # Database file should exist after first write
            assert db_file.exists()
            
            session.close()
        finally:
            os.chdir(original_cwd)
