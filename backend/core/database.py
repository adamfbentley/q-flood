from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from fastapi import HTTPException
import logging

logger = logging.getLogger(__name__)

try:
    from app.core.config import settings
    SQLALCHEMY_DATABASE_URL = settings.DATABASE_URL
    engine = create_engine(SQLALCHEMY_DATABASE_URL)
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    DB_AVAILABLE = True
except Exception as e:
    logger.warning(f"Database configuration failed: {e}")
    # Create a dummy engine for development without database
    engine = None
    SessionLocal = None
    SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"
    DB_AVAILABLE = False

Base = declarative_base()

def get_db():
    """Dependency function that provides a database session."""
    if not DB_AVAILABLE or SessionLocal is None:
        raise HTTPException(status_code=503, detail="Database not available")
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def init_db():
    """Initializes the database by creating all tables defined in Base."""
    if not DB_AVAILABLE or engine is None:
        logger.warning("Database not available, skipping table creation")
        return
    
    try:
        # Import all models here to ensure they are registered with Base
        from app.models.api_key import APIKey # noqa
        from app.models.job import Job # noqa
        from app.models.performance_log import PerformanceLog # New: Import PerformanceLog # noqa
        Base.metadata.create_all(bind=engine)
    except Exception as e:
        logger.error(f"Failed to initialize database: {e}")
        raise
