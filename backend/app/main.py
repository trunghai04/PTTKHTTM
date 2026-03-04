from dotenv import load_dotenv
load_dotenv()

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.database.db import engine, Base
from app.routes import spam_routes, news_routes, stats_routes, auth_routes, gmail_routes
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create database tables (with error handling)
try:
    Base.metadata.create_all(bind=engine)
    logger.info("Database tables created successfully")
except Exception as e:
    logger.warning(f"Could not create database tables (this is OK if DB is not available): {e}")

# Migration: add new columns if tables existed before schema update
def _run_migrations():
    from sqlalchemy import text

    with engine.connect() as conn:
        dialect = engine.dialect.name

        # 1) predictions table: user_id + source + email metadata
        for col_name, col_type in [
            ("user_id", "INTEGER"),
            ("source", "VARCHAR(50)"),
            ("email_subject", "VARCHAR(500)"),
            ("email_snippet", "VARCHAR(500)"),
        ]:
            try:
                if dialect == "postgresql":
                    conn.execute(
                        text(
                            f"ALTER TABLE predictions "
                            f"ADD COLUMN IF NOT EXISTS {col_name} {col_type}"
                        )
                    )
                else:
                    conn.execute(
                        text(f"ALTER TABLE predictions ADD COLUMN {col_name} {col_type}")
                    )
            except Exception as col_err:
                err_str = str(col_err).lower()
                if "already exists" not in err_str and "duplicate" not in err_str:
                    raise

        # 2) users table: Google OAuth columns + avatar
        for col_name, col_type in [
            ("google_id", "VARCHAR(255)"),
            ("google_refresh_token", "TEXT"),
            ("avatar_url", "VARCHAR(500)"),
        ]:
            try:
                if dialect == "postgresql":
                    conn.execute(
                        text(
                            f"ALTER TABLE users "
                            f"ADD COLUMN IF NOT EXISTS {col_name} {col_type}"
                        )
                    )
                else:
                    conn.execute(
                        text(f"ALTER TABLE users ADD COLUMN {col_name} {col_type}")
                    )
            except Exception as col_err:
                err_str = str(col_err).lower()
                if "already exists" not in err_str and "duplicate" not in err_str:
                    raise

        conn.commit()

try:
    _run_migrations()
    logger.info("Database migrations applied")
except Exception as e:
    logger.warning(f"Migration skipped (OK if columns exist): {e}")

app = FastAPI(
    title="Text Classification API",
    description="API for Spam and News Classification",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(spam_routes.router, prefix="/api/spam", tags=["Spam"])
app.include_router(news_routes.router, prefix="/api/news", tags=["News"])
app.include_router(stats_routes.router, prefix="/api/stats", tags=["Statistics"])
app.include_router(auth_routes.router, prefix="/api/auth", tags=["Auth"])
app.include_router(gmail_routes.router, prefix="/api/gmail", tags=["Gmail"])

@app.get("/")
async def root():
    return {"message": "Text Classification API", "version": "1.0.0"}

@app.get("/health")
async def health():
    return {"status": "healthy"}
