from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from pathlib import Path
import os

# Database URL from environment variable or default
# Priority:
# 1) DATABASE_URL (recommended: MySQL local)
# 2) PostgreSQL local default
# 3) SQLite fallback
database_url = os.getenv("DATABASE_URL")

if not database_url:
    database_url = "postgresql://postgres:postgres@localhost:5432/text_classification"
    print("📦 DATABASE_URL not set. Falling back to local PostgreSQL.")


def _create_engine_with_fallback(url: str):
    if url.startswith("sqlite"):
        return create_engine(
            url,
            connect_args={"check_same_thread": False},
            echo=False,
        )

    # MySQL-specific connection args
    if url.startswith("mysql"):
        return create_engine(
            url,
            pool_pre_ping=True,
            connect_args={"connect_timeout": 10},
            pool_timeout=10,
            pool_recycle=300,
        )

    # PostgreSQL / other SQLAlchemy-supported DBs
    return create_engine(
        url,
        pool_pre_ping=True,
        connect_args={
            "connect_timeout": 5,
            "options": "-c statement_timeout=5000",
        },
        pool_timeout=5,
        pool_recycle=300,
    )


try:
    engine = _create_engine_with_fallback(database_url)
    if database_url.startswith("mysql"):
        print("✅ MySQL database engine created")
    elif database_url.startswith("sqlite"):
        print("✅ SQLite database engine created")
    else:
        print("✅ PostgreSQL database engine created")
except Exception as e:
    print(f"⚠️  Database connection failed for DATABASE_URL='{database_url}': {e}")
    print("   Falling back to SQLite...")
    db_path = Path(__file__).parent.parent.parent / "database.db"
    database_url = f"sqlite:///{db_path}"
    engine = create_engine(
        database_url,
        connect_args={"check_same_thread": False},
        echo=False,
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
