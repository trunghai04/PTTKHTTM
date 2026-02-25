from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.database.db import engine, Base
from app.routes import spam_routes, news_routes, stats_routes
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

@app.get("/")
async def root():
    return {"message": "Text Classification API", "version": "1.0.0"}

@app.get("/health")
async def health():
    return {"status": "healthy"}
