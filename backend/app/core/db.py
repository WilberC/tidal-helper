import logging
from pathlib import Path
from sqlmodel import SQLModel, create_engine, Session
from app.core.config import settings

# Configure logging - reduce verbosity
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Reduce SQLAlchemy logging verbosity
logging.getLogger("sqlalchemy.engine").setLevel(logging.WARNING)

engine = create_engine(settings.DATABASE_URL, echo=False)


def init_db():
    """Create all database tables."""
    SQLModel.metadata.create_all(engine)


def validate_and_init_db():
    """
    Validate database existence and initialize if needed.

    For SQLite databases:
    - Checks if the database file exists
    - Creates tables if database is missing or empty

    For other databases:
    - Validates connectivity
    - Creates tables if needed
    """
    try:
        # Check if using SQLite
        if settings.DATABASE_URL.startswith("sqlite"):
            # Extract database file path from URL
            db_path = settings.DATABASE_URL.replace("sqlite:///", "")
            db_file = Path(db_path)

            if not db_file.exists():
                logger.info(f"Creating database at {db_path}")
                init_db()
                logger.info("✓ Database initialized")
            else:
                # Ensure all tables exist (in case of schema changes)
                init_db()
                logger.info("✓ Database ready")
        else:
            # For non-SQLite databases, just ensure tables exist
            init_db()
            logger.info("✓ Database ready")

    except Exception as e:
        logger.error(f"Error during database validation: {e}")
        raise


def get_session():
    """Get a database session."""
    with Session(engine) as session:
        yield session
