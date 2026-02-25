from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from pathlib import Path
import os

# Database URL from environment variable or default
# Priority: 1. Environment variable, 2. PostgreSQL (if available), 3. SQLite (fallback)
database_url = os.getenv("DATABASE_URL")

if not database_url:
    # Try PostgreSQL first (if psycopg2 is installed)
    try:
        import psycopg2
        # Try to connect to PostgreSQL
        database_url = "postgresql://postgres:postgres@localhost:5432/text_classification"
        print("📦 Attempting to use PostgreSQL...")
    except (ImportError, Exception):
        # Fallback to SQLite (no installation needed)
        db_path = Path(__file__).parent.parent.parent / "database.db"
        database_url = f"sqlite:///{db_path}"
        print(f"📦 Using SQLite database at: {db_path}")
        print("   (SQLite doesn't require installation - perfect for development!)")

# Create engine with appropriate settings
if database_url.startswith("sqlite"):
    # SQLite settings
    engine = create_engine(
        database_url,
        connect_args={"check_same_thread": False},  # SQLite specific
        echo=False
    )
    print("✅ SQLite database engine created")
else:
    # PostgreSQL settings
    try:
        engine = create_engine(
            database_url,
            pool_pre_ping=True,
            connect_args={
                "connect_timeout": 5,
                "options": "-c statement_timeout=5000"
            },
            pool_timeout=5,
            pool_recycle=300
        )
        print("✅ PostgreSQL database engine created")
    except Exception as e:
        # If PostgreSQL fails, fallback to SQLite
        print(f"⚠️  PostgreSQL connection failed: {e}")
        print("   Falling back to SQLite...")
        db_path = Path(__file__).parent.parent.parent / "database.db"
        database_url = f"sqlite:///{db_path}"
        engine = create_engine(
            database_url,
            connect_args={"check_same_thread": False},
            echo=False
        )
        print(f"✅ Using SQLite database at: {db_path}")

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

def get_db():
    """Dependency for getting database session"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
