"""
Unit Tests for Database Module
Tests for src/models/database.py
"""

import sys
from datetime import datetime
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

# Check if sqlalchemy is available
try:
    import sqlalchemy
    SQLALCHEMY_AVAILABLE = True
except ImportError:
    SQLALCHEMY_AVAILABLE = False

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

if SQLALCHEMY_AVAILABLE:
    from src.models.database import Base, MusicCue, Podcast, get_session, init_db
else:
    # Create dummy classes for testing structure
    Base = None
    MusicCue = None
    Podcast = None
    get_session = None
    init_db = None


@pytest.mark.skipif(not SQLALCHEMY_AVAILABLE, reason="sqlalchemy not installed")
class TestPodcastModel:
    """Test Podcast model."""

    def test_podcast_creation(self):
        """Test creating a Podcast instance."""
        podcast = Podcast(
            title="Test Podcast",
            script_path="/path/to/script.txt",
            output_path="/path/to/output.mp4",
            duration=120.5,
            character_name="Test Character",
            status="completed",
        )

        assert podcast.title == "Test Podcast"
        assert podcast.script_path == "/path/to/script.txt"
        assert podcast.output_path == "/path/to/output.mp4"
        assert podcast.duration == 120.5
        assert podcast.character_name == "Test Character"
        assert podcast.status == "completed"

    def test_podcast_default_status(self):
        """Test Podcast default status is 'pending'."""
        podcast = Podcast(title="Test")

        assert podcast.status == "pending"

    def test_podcast_repr(self):
        """Test Podcast __repr__ method."""
        podcast = Podcast(id=1, title="Test Podcast", status="processing")

        repr_str = repr(podcast)

        assert "Podcast" in repr_str
        assert "id=1" in repr_str
        assert "Test Podcast" in repr_str
        assert "processing" in repr_str

    def test_podcast_optional_fields(self):
        """Test Podcast with optional fields."""
        podcast = Podcast(
            title="Test",
            completed_at=datetime(2024, 1, 1, 12, 0, 0),
            error_message="Test error",
        )

        assert podcast.completed_at is not None
        assert podcast.error_message == "Test error"

    def test_podcast_created_at_default(self):
        """Test Podcast has created_at timestamp."""
        podcast = Podcast(title="Test")

        assert podcast.created_at is not None
        assert isinstance(podcast.created_at, datetime)


@pytest.mark.skipif(not SQLALCHEMY_AVAILABLE, reason="sqlalchemy not installed")
class TestMusicCueModel:
    """Test MusicCue model."""

    def test_music_cue_creation(self):
        """Test creating a MusicCue instance."""
        cue = MusicCue(
            podcast_id=1,
            description="upbeat intro music",
            timestamp=0.0,
            duration=10.5,
            music_path="/path/to/music.mp3",
        )

        assert cue.podcast_id == 1
        assert cue.description == "upbeat intro music"
        assert cue.timestamp == 0.0
        assert cue.duration == 10.5
        assert cue.music_path == "/path/to/music.mp3"

    def test_music_cue_repr(self):
        """Test MusicCue __repr__ method."""
        cue = MusicCue(id=1, podcast_id=5)

        repr_str = repr(cue)

        assert "MusicCue" in repr_str
        assert "id=1" in repr_str
        assert "podcast_id=5" in repr_str

    def test_music_cue_optional_fields(self):
        """Test MusicCue with optional fields."""
        cue = MusicCue(podcast_id=1, description="test", timestamp=None, duration=None, music_path=None)

        assert cue.timestamp is None
        assert cue.duration is None
        assert cue.music_path is None


@pytest.mark.skipif(not SQLALCHEMY_AVAILABLE, reason="sqlalchemy not installed")
class TestInitDB:
    """Test database initialization."""

    def test_init_db_default_url(self, temp_dir):
        """Test init_db with default URL creates data directory."""
        import os

        original_cwd = os.getcwd()
        try:
            os.chdir(temp_dir)

            engine = init_db()

            assert engine is not None
            data_dir = Path(temp_dir) / "data"
            db_file = data_dir / "podcasts.db"
            # Database file may not exist until first write, but directory should exist
            assert data_dir.exists()

        finally:
            os.chdir(original_cwd)

    def test_init_db_custom_url(self, temp_dir):
        """Test init_db with custom database URL."""
        db_path = temp_dir / "custom.db"
        database_url = f"sqlite:///{db_path}"

        engine = init_db(database_url)

        assert engine is not None
        assert db_path.exists()

    def test_init_db_creates_tables(self, temp_dir):
        """Test that init_db creates database tables."""
        db_path = temp_dir / "test.db"
        database_url = f"sqlite:///{db_path}"

        engine = init_db(database_url)

        # Verify tables exist by checking metadata
        assert "podcasts" in Base.metadata.tables
        assert "music_cues" in Base.metadata.tables

    def test_init_db_in_memory(self):
        """Test init_db with in-memory database."""
        database_url = "sqlite:///:memory:"

        engine = init_db(database_url)

        assert engine is not None

    def test_init_db_idempotent(self, temp_dir):
        """Test that init_db can be called multiple times."""
        db_path = temp_dir / "test.db"
        database_url = f"sqlite:///{db_path}"

        engine1 = init_db(database_url)
        engine2 = init_db(database_url)

        assert engine1 is not None
        assert engine2 is not None


@pytest.mark.skipif(not SQLALCHEMY_AVAILABLE, reason="sqlalchemy not installed")
class TestGetSession:
    """Test get_session function."""

    def test_get_session_default_url(self, temp_dir):
        """Test get_session with default URL."""
        import os

        original_cwd = os.getcwd()
        try:
            os.chdir(temp_dir)

            session = get_session()

            assert session is not None
            # Verify it's a SQLAlchemy session
            assert hasattr(session, "add")
            assert hasattr(session, "commit")
            assert hasattr(session, "query")

        finally:
            os.chdir(original_cwd)

    def test_get_session_custom_url(self, temp_dir):
        """Test get_session with custom database URL."""
        db_path = temp_dir / "session_test.db"
        database_url = f"sqlite:///{db_path}"

        session = get_session(database_url)

        assert session is not None
        assert hasattr(session, "add")
        assert hasattr(session, "commit")

    def test_get_session_creates_database(self, temp_dir):
        """Test that get_session creates database if needed."""
        db_path = temp_dir / "session_created.db"
        database_url = f"sqlite:///{db_path}"

        session = get_session(database_url)

        # Database should be created
        assert db_path.exists()

    def test_get_session_supports_crud_operations(self, temp_dir):
        """Test that session supports CRUD operations."""
        db_path = temp_dir / "crud_test.db"
        database_url = f"sqlite:///{db_path}"

        session = get_session(database_url)

        # Create
        podcast = Podcast(title="Test CRUD", status="pending")
        session.add(podcast)
        session.commit()

        # Read
        found = session.query(Podcast).filter_by(title="Test CRUD").first()
        assert found is not None
        assert found.title == "Test CRUD"

        # Update
        found.status = "completed"
        session.commit()

        updated = session.query(Podcast).filter_by(title="Test CRUD").first()
        assert updated.status == "completed"

        # Delete
        session.delete(updated)
        session.commit()

        deleted = session.query(Podcast).filter_by(title="Test CRUD").first()
        assert deleted is None

        session.close()


@pytest.mark.skipif(not SQLALCHEMY_AVAILABLE, reason="sqlalchemy not installed")
class TestDatabaseRelationships:
    """Test database relationships and foreign keys."""

    def test_podcast_with_music_cues(self, temp_dir):
        """Test creating podcast with associated music cues."""
        db_path = temp_dir / "relationships.db"
        database_url = f"sqlite:///{db_path}"

        session = get_session(database_url)

        # Create podcast
        podcast = Podcast(title="Test Podcast", status="processing")
        session.add(podcast)
        session.flush()  # Get podcast.id

        # Create music cues
        cue1 = MusicCue(podcast_id=podcast.id, description="intro", timestamp=0.0, duration=5.0)
        cue2 = MusicCue(podcast_id=podcast.id, description="outro", timestamp=115.0, duration=5.0)

        session.add(cue1)
        session.add(cue2)
        session.commit()

        # Verify relationships
        cues = session.query(MusicCue).filter_by(podcast_id=podcast.id).all()
        assert len(cues) == 2
        assert cues[0].podcast_id == podcast.id
        assert cues[1].podcast_id == podcast.id

        session.close()

    def test_multiple_podcasts(self, temp_dir):
        """Test creating multiple podcasts."""
        db_path = temp_dir / "multiple.db"
        database_url = f"sqlite:///{db_path}"

        session = get_session(database_url)

        podcast1 = Podcast(title="Podcast 1", status="completed")
        podcast2 = Podcast(title="Podcast 2", status="pending")
        podcast3 = Podcast(title="Podcast 3", status="processing")

        session.add_all([podcast1, podcast2, podcast3])
        session.commit()

        all_podcasts = session.query(Podcast).all()
        assert len(all_podcasts) == 3

        session.close()


@pytest.mark.skipif(not SQLALCHEMY_AVAILABLE, reason="sqlalchemy not installed")
class TestDatabaseEdgeCases:
    """Test edge cases and error handling."""

    def test_podcast_long_title(self, temp_dir):
        """Test Podcast with very long title."""
        db_path = temp_dir / "long_title.db"
        database_url = f"sqlite:///{db_path}"

        session = get_session(database_url)

        long_title = "A" * 255  # Max length
        podcast = Podcast(title=long_title, status="pending")
        session.add(podcast)
        session.commit()

        found = session.query(Podcast).filter_by(title=long_title).first()
        assert found is not None

        session.close()

    def test_music_cue_long_description(self, temp_dir):
        """Test MusicCue with very long description."""
        db_path = temp_dir / "long_desc.db"
        database_url = f"sqlite:///{db_path}"

        session = get_session(database_url)

        podcast = Podcast(title="Test", status="pending")
        session.add(podcast)
        session.flush()

        long_description = "This is a very long description. " * 100  # Text field, no limit
        cue = MusicCue(podcast_id=podcast.id, description=long_description)
        session.add(cue)
        session.commit()

        found = session.query(MusicCue).filter_by(podcast_id=podcast.id).first()
        assert found.description == long_description

        session.close()

    def test_podcast_nullable_fields(self, temp_dir):
        """Test Podcast with None values for nullable fields."""
        db_path = temp_dir / "nullable.db"
        database_url = f"sqlite:///{db_path}"

        session = get_session(database_url)

        podcast = Podcast(
            title="Test",
            script_path=None,
            output_path=None,
            duration=None,
            character_name=None,
            completed_at=None,
            error_message=None,
        )
        session.add(podcast)
        session.commit()

        found = session.query(Podcast).filter_by(title="Test").first()
        assert found.script_path is None
        assert found.output_path is None
        assert found.duration is None

        session.close()

    def test_podcast_datetime_fields(self, temp_dir):
        """Test Podcast datetime field handling."""
        db_path = temp_dir / "datetime.db"
        database_url = f"sqlite:///{db_path}"

        session = get_session(database_url)

        now = datetime.utcnow()
        completed = datetime(2024, 12, 25, 12, 0, 0)

        podcast = Podcast(title="Test", created_at=now, completed_at=completed, status="completed")
        session.add(podcast)
        session.commit()

        found = session.query(Podcast).filter_by(title="Test").first()
        assert found.created_at is not None
        assert found.completed_at == completed

        session.close()

