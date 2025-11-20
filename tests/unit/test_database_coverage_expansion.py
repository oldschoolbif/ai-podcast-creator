"""
Expanded coverage tests for database.py
Tests to increase coverage from 6.67% to 80%+
"""

import sys
from datetime import datetime
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

# Check if sqlalchemy is available
try:
    import sqlalchemy
    SQLALCHEMY_AVAILABLE = True
except ImportError:
    SQLALCHEMY_AVAILABLE = False


@pytest.mark.skipif(not SQLALCHEMY_AVAILABLE, reason="sqlalchemy not installed")
class TestDatabaseCoverageExpansion:
    """Tests to expand database.py coverage."""

    def test_podcast_init_with_no_kwargs(self):
        """Test Podcast.__init__ with no kwargs (uses all defaults)."""
        from src.models.database import Podcast
        
        # Create with minimal args - should trigger default status and created_at
        podcast = Podcast()
        podcast.title = "Test"  # Set after to avoid kwargs
        
        assert podcast.status == "pending"
        assert podcast.created_at is not None
        assert isinstance(podcast.created_at, datetime)

    def test_podcast_init_status_none_becomes_pending(self):
        """Test Podcast.__init__ when status is explicitly None (line 31-33)."""
        from src.models.database import Podcast
        
        podcast = Podcast(title="Test", status=None)
        
        assert podcast.status == "pending"

    def test_podcast_init_status_provided_not_none(self):
        """Test Podcast.__init__ when status is provided and not None (line 32 branch)."""
        from src.models.database import Podcast
        
        podcast = Podcast(title="Test", status="processing")
        
        assert podcast.status == "processing"

    def test_podcast_init_created_at_none_becomes_utcnow(self):
        """Test Podcast.__init__ when created_at is None (line 35-37)."""
        from src.models.database import Podcast
        
        podcast = Podcast(title="Test", created_at=None)
        
        assert podcast.created_at is not None
        assert isinstance(podcast.created_at, datetime)

    def test_podcast_init_created_at_provided_not_none(self):
        """Test Podcast.__init__ when created_at is provided and not None (line 36 branch)."""
        from src.models.database import Podcast
        
        custom_time = datetime(2023, 1, 1, 12, 0, 0)
        podcast = Podcast(title="Test", created_at=custom_time)
        
        assert podcast.created_at == custom_time

    def test_podcast_init_both_defaults_needed(self):
        """Test Podcast.__init__ when both status and created_at are None."""
        from src.models.database import Podcast
        
        podcast = Podcast(title="Test", status=None, created_at=None)
        
        assert podcast.status == "pending"
        assert podcast.created_at is not None

    def test_podcast_repr_with_all_fields(self):
        """Test Podcast.__repr__ with all fields populated (line 41-42)."""
        from src.models.database import Podcast
        
        podcast = Podcast(
            id=42,
            title="My Test Podcast",
            status="completed"
        )
        
        repr_str = repr(podcast)
        
        assert "Podcast" in repr_str
        assert "id=42" in repr_str
        assert "My Test Podcast" in repr_str
        assert "completed" in repr_str

    def test_music_cue_repr_with_all_fields(self):
        """Test MusicCue.__repr__ with all fields (line 57-58)."""
        from src.models.database import MusicCue
        
        cue = MusicCue(id=10, podcast_id=5)
        
        repr_str = repr(cue)
        
        assert "MusicCue" in repr_str
        assert "id=10" in repr_str
        assert "podcast_id=5" in repr_str

    def test_init_db_with_none_url_creates_data_dir(self, tmp_path):
        """Test init_db with None creates ./data directory (lines 68-72)."""
        from src.models.database import init_db
        import os
        
        original_cwd = os.getcwd()
        try:
            os.chdir(tmp_path)
            
            engine = init_db(None)
            
            assert engine is not None
            data_dir = Path(tmp_path) / "data"
            assert data_dir.exists()
            assert data_dir.is_dir()
            
        finally:
            os.chdir(original_cwd)

    def test_init_db_with_none_url_uses_default_path(self, tmp_path):
        """Test init_db with None uses default database path (line 72)."""
        from src.models.database import init_db
        import os
        
        original_cwd = os.getcwd()
        try:
            os.chdir(tmp_path)
            
            engine = init_db(None)
            
            assert engine.url.database is not None
            # Should use sqlite:///./data/podcasts.db
            assert "podcasts.db" in str(engine.url.database)
            
        finally:
            os.chdir(original_cwd)

    def test_init_db_with_custom_url(self, tmp_path):
        """Test init_db with custom database URL (lines 61, 68 branch)."""
        from src.models.database import init_db
        
        db_path = tmp_path / "custom.db"
        database_url = f"sqlite:///{db_path}"
        
        engine = init_db(database_url)
        
        assert engine is not None
        assert engine.url.database == str(db_path)

    def test_init_db_creates_tables(self, tmp_path):
        """Test init_db creates all tables (line 75)."""
        from src.models.database import Base, init_db
        
        db_path = tmp_path / "tables.db"
        database_url = f"sqlite:///{db_path}"
        
        engine = init_db(database_url)
        
        # Verify tables exist
        assert "podcasts" in Base.metadata.tables
        assert "music_cues" in Base.metadata.tables

    def test_get_session_with_none_url(self, tmp_path):
        """Test get_session with None URL (lines 80-92)."""
        from src.models.database import get_session
        import os
        
        original_cwd = os.getcwd()
        try:
            os.chdir(tmp_path)
            
            session = get_session(None)
            
            assert session is not None
            assert hasattr(session, "add")
            assert hasattr(session, "commit")
            assert hasattr(session, "query")
            
            session.close()
            
        finally:
            os.chdir(original_cwd)

    def test_get_session_with_custom_url(self, tmp_path):
        """Test get_session with custom URL (lines 80, 90)."""
        from src.models.database import get_session
        
        db_path = tmp_path / "session.db"
        database_url = f"sqlite:///{db_path}"
        
        session = get_session(database_url)
        
        assert session is not None
        assert hasattr(session, "add")
        assert hasattr(session, "commit")
        
        session.close()

    def test_get_session_calls_init_db(self, tmp_path):
        """Test get_session calls init_db (line 90)."""
        from src.models.database import get_session, init_db
        
        db_path = tmp_path / "verify.db"
        database_url = f"sqlite:///{db_path}"
        
        with patch("src.models.database.init_db") as mock_init:
            mock_engine = MagicMock()
            mock_init.return_value = mock_engine
            
            session = get_session(database_url)
            
            # Verify init_db was called
            mock_init.assert_called_once_with(database_url)

    def test_podcast_all_columns_settable(self, tmp_path):
        """Test all Podcast columns can be set."""
        from src.models.database import Podcast, get_session
        
        database_url = f"sqlite:///{tmp_path / 'all_columns.db'}"
        session = get_session(database_url)
        
        podcast = Podcast(
            title="Full Test",
            script_path="/path/to/script.txt",
            output_path="/path/to/output.mp4",
            duration=300.5,
            character_name="Test Character",
            status="processing",
            created_at=datetime(2024, 1, 1, 12, 0, 0),
            completed_at=datetime(2024, 1, 1, 13, 0, 0),
            error_message="No errors"
        )
        
        session.add(podcast)
        session.commit()
        
        found = session.query(Podcast).filter_by(title="Full Test").first()
        assert found is not None
        assert found.script_path == "/path/to/script.txt"
        assert found.output_path == "/path/to/output.mp4"
        assert found.duration == 300.5
        assert found.character_name == "Test Character"
        assert found.completed_at is not None
        assert found.error_message == "No errors"
        
        session.close()

    def test_music_cue_all_columns_settable(self, tmp_path):
        """Test all MusicCue columns can be set."""
        from src.models.database import MusicCue, Podcast, get_session
        
        database_url = f"sqlite:///{tmp_path / 'music_cue.db'}"
        session = get_session(database_url)
        
        # Create podcast first
        podcast = Podcast(title="Music Test")
        session.add(podcast)
        session.flush()
        
        cue = MusicCue(
            podcast_id=podcast.id,
            description="Upbeat background music",
            timestamp=10.5,
            duration=30.0,
            music_path="/path/to/music.mp3"
        )
        
        session.add(cue)
        session.commit()
        
        found = session.query(MusicCue).filter_by(podcast_id=podcast.id).first()
        assert found is not None
        assert found.description == "Upbeat background music"
        assert found.timestamp == 10.5
        assert found.duration == 30.0
        assert found.music_path == "/path/to/music.mp3"
        
        session.close()

