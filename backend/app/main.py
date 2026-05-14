import os
try:
    from dotenv import load_dotenv
    load_dotenv()
except Exception:
    # Keep app bootable even if python-dotenv is missing.
    pass

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.database.db import engine, Base
from app.routes import spam_routes, news_routes, stats_routes, auth_routes, gmail_routes
import logging
import threading
import time
from pathlib import Path

# Cấu hình logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Tạo bảng database (có xử lý lỗi)
try:
    Base.metadata.create_all(bind=engine)
    logger.info("Đã tạo bảng database thành công")
except Exception as e:
    logger.warning(f"Không thể tạo bảng database (vẫn ổn nếu DB chưa sẵn sàng): {e}")

# Migration: add new columns if tables existed before schema update
def _run_migrations():
    from sqlalchemy import text

    with engine.connect() as conn:
        dialect = engine.dialect.name

        # 1) Bảng predictions: user_id + source + metadata email + luồng duyệt
        for col_name, col_type in [
            ("user_id", "INTEGER"),
            ("source", "VARCHAR(50)"),
            ("email_subject", "VARCHAR(500)"),
            ("email_snippet", "VARCHAR(500)"),
            ("review_status", "VARCHAR(50)"),
            ("reviewed_label", "VARCHAR(255)"),
            ("reviewed_at", "TIMESTAMP"),
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

        # 2) Bảng users: cột Google OAuth + avatar
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


def _normalize_user_roles():
    from sqlalchemy import text

    with engine.begin() as conn:
        dialect = engine.dialect.name
        try:
            if dialect == "postgresql":
                conn.execute(
                    text("UPDATE users SET role = lower(role) WHERE role IN ('USER', 'ADMIN')")
                )
            else:
                conn.execute(
                    text("UPDATE users SET role = LOWER(role) WHERE role IN ('USER', 'ADMIN')")
                )
        except Exception as role_err:
            logger.warning(f"Could not normalize user roles (OK if already normalized): {role_err}")


try:
    _normalize_user_roles()
    logger.info("User roles normalized")
except Exception as e:
    logger.warning(f"Role normalization skipped: {e}")

app = FastAPI(
    title="BloopAI API",
    description="API for Spam and News Classification",
    version="1.0.0"
)

# CORS middleware
# Keep localhost dev ports and any comma-separated origins from env.
allowed_origins = [
    "http://localhost:3000",
    "http://localhost:3004",
    "http://localhost:5173",
    "http://127.0.0.1:3000",
    "http://127.0.0.1:3004",
    "http://127.0.0.1:5173",
    "http://localhost:8080",
    "http://127.0.0.1:8080",
    "https://bloopai.bloop.io.vn",
]
extra_cors_origins = os.getenv("CORS_ALLOW_ORIGINS", "").strip()
if extra_cors_origins:
    allowed_origins.extend(
        [origin.strip() for origin in extra_cors_origins.split(",") if origin.strip()]
    )

# Allow local dev by regex too so alternate ports don't cause CORS failures.
app.add_middleware(
    CORSMiddleware,
    allow_origin_regex=r"https?://(localhost|127\.0\.0\.1)(:\\d+)?$",
    allow_origins=allowed_origins,
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


# ====== Auto-training background job (self-learning) ======

def _env_bool(name: str, default: bool) -> bool:
    value = os.getenv(name)
    if value is None:
        return default
    return value.strip().lower() in {"1", "true", "yes", "on"}


# Disable by default to avoid retraining side-effects on every API start.
ENABLE_AUTO_TRAIN = _env_bool("ENABLE_AUTO_TRAIN", False)
AUTO_TRAIN_INTERVAL_SECONDS = int(os.getenv("AUTO_TRAIN_INTERVAL_SECONDS", str(6 * 60 * 60)))


def _auto_train_loop():
    """
    Simple background loop:
    - Mỗi chu kỳ: load dữ liệu gốc (Excel nếu có) + dữ liệu người dùng (trong train_model)
    - Gọi train_spam_model và train_news_model
    - Ngủ AUTO_TRAIN_INTERVAL_SECONDS rồi lặp lại

    Chạy trong thread daemon để không block main event loop.
    """
    while True:
        try:
            logger.info("🔁 Auto-training cycle started")
            # Import lazily so API still boots when training deps are absent.
            from train_model import (
                train_spam_model,
                train_news_model,
                load_data_from_excel,
                load_data_from_csv,
                DATASET_PATH,
                CSV_DATASET_PATH,
                USE_EXCEL,
                USE_CSV,
            )

            base_data = None
            if USE_EXCEL and isinstance(DATASET_PATH, Path) and DATASET_PATH.exists():
                base_data = load_data_from_excel(DATASET_PATH)

            # Merge thêm dữ liệu CSV nếu được bật
            if USE_CSV and isinstance(CSV_DATASET_PATH, Path) and CSV_DATASET_PATH.exists():
                csv_data = load_data_from_csv(CSV_DATASET_PATH)
                if csv_data is not None:
                    if base_data is None:
                        base_data = csv_data
                    else:
                        logger.info("🔗 Auto-train: merging Excel + CSV base data")
                        import pandas as pd
                        base_data = pd.concat([base_data, csv_data], ignore_index=True)

            # Chỉ train từ dữ liệu đã xác nhận để tránh học sai từ prediction chưa duyệt.
            train_spam_model(base_data)
            train_news_model(base_data)

            logger.info("✅ Auto-training cycle completed")
        except Exception as e:
            logger.exception(f"⚠️  Auto-training failed: {e}")

        # Đợi tới chu kỳ tiếp theo
        time.sleep(AUTO_TRAIN_INTERVAL_SECONDS)


@app.on_event("startup")
async def start_auto_training():
    """
    Khởi động thread auto-train khi API server start.
    """
    if not ENABLE_AUTO_TRAIN:
        logger.info("Auto-training is disabled (set ENABLE_AUTO_TRAIN=true to enable).")
        return
    try:
        thread = threading.Thread(target=_auto_train_loop, daemon=True)
        thread.start()
        logger.info(
            f"🚀 Auto-training background thread started (interval={AUTO_TRAIN_INTERVAL_SECONDS}s)"
        )
    except Exception as e:
        logger.warning(f"Could not start auto-training thread: {e}")

@app.get("/")
async def root():
    return {"message": "BloopAI API", "version": "1.0.0"}

@app.get("/health")
async def health():
    return {"status": "healthy"}
