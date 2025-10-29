"""
Database models and initialization
"""

from sqlalchemy import create_engine, Column, Integer, String, DateTime, Text, Float
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime
from pathlib import Path

Base = declarative_base()


class Podcast(Base):
    """Podcast episode model."""
    
    __tablename__ = 'podcasts'
    
    id = Column(Integer, primary_key=True)
    title = Column(String(255), nullable=False)
    script_path = Column(String(512))
    output_path = Column(String(512))
    duration = Column(Float)  # Duration in seconds
    character_name = Column(String(100))
    status = Column(String(50), default='pending')  # pending, processing, completed, failed
    created_at = Column(DateTime, default=datetime.utcnow)
    completed_at = Column(DateTime, nullable=True)
    error_message = Column(Text, nullable=True)
    
    def __repr__(self):
        return f"<Podcast(id={self.id}, title='{self.title}', status='{self.status}')>"


class MusicCue(Base):
    """Music cue model."""
    
    __tablename__ = 'music_cues'
    
    id = Column(Integer, primary_key=True)
    podcast_id = Column(Integer, nullable=False)
    description = Column(Text, nullable=False)
    timestamp = Column(Float)  # Timestamp in seconds
    duration = Column(Float)  # Duration in seconds
    music_path = Column(String(512))
    
    def __repr__(self):
        return f"<MusicCue(id={self.id}, podcast_id={self.podcast_id})>"


def init_db(database_url: str = None):
    """
    Initialize database and create tables.
    
    Args:
        database_url: Database URL (default: sqlite:///./data/podcasts.db)
    """
    if database_url is None:
        # Create data directory if it doesn't exist
        data_dir = Path('./data')
        data_dir.mkdir(exist_ok=True)
        database_url = 'sqlite:///./data/podcasts.db'
    
    engine = create_engine(database_url, echo=False)
    Base.metadata.create_all(engine)
    
    return engine


def get_session(database_url: str = None):
    """
    Get database session.
    
    Args:
        database_url: Database URL
        
    Returns:
        SQLAlchemy session
    """
    engine = init_db(database_url)
    Session = sessionmaker(bind=engine)
    return Session()

