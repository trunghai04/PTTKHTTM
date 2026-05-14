from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session
from sqlalchemy import func, case
from app.auth.deps import get_current_user
from app.database.db import get_db
from app.database.models import Prediction, PredictionType, User, UserRole


class ReviewDecision(BaseModel):
    reviewed_label: str | None = None
    approve: bool = True

router = APIRouter()

@router.get("/overview")
async def get_stats_overview(db: Session = Depends(get_db)):
    """
    Get overall statistics
    """
    # Total predictions
    total = db.query(func.count(Prediction.id)).scalar() or 0
    
    # Spam predictions
    spam_total = db.query(func.count(Prediction.id)).filter(
        Prediction.type == PredictionType.SPAM
    ).scalar() or 0
    
    # News predictions
    news_total = db.query(func.count(Prediction.id)).filter(
        Prediction.type == PredictionType.NEWS
    ).scalar() or 0
    
    # Spam label distribution
    spam_labels = db.query(
        Prediction.predicted_label,
        func.count(Prediction.id).label('count')
    ).filter(
        Prediction.type == PredictionType.SPAM
    ).group_by(Prediction.predicted_label).all()
    
    spam_distribution = {label: count for label, count in spam_labels}
    
    # News category distribution
    news_labels = db.query(
        Prediction.predicted_label,
        func.count(Prediction.id).label('count')
    ).filter(
        Prediction.type == PredictionType.NEWS
    ).group_by(Prediction.predicted_label).all()
    
    news_distribution = {label: count for label, count in news_labels}
    
    # Average confidence
    avg_confidence = db.query(func.avg(Prediction.confidence)).scalar() or 0
    
    return {
        "total_predictions": total,
        "spam_total": spam_total,
        "news_total": news_total,
        "spam_distribution": spam_distribution,
        "news_distribution": news_distribution,
        "average_confidence": round(float(avg_confidence), 4) if avg_confidence else 0
    }

@router.get("/news/categories")
async def get_news_category_stats(db: Session = Depends(get_db)):
    """
    Get news category statistics for pie chart
    """
    categories = db.query(
        Prediction.predicted_label,
        func.count(Prediction.id).label('count')
    ).filter(
        Prediction.type == PredictionType.NEWS
    ).group_by(Prediction.predicted_label).all()
    
    return [
        {"category": label, "count": count}
        for label, count in categories
    ]

@router.get("/timeline/monthly")
async def get_monthly_timeline(db: Session = Depends(get_db)):
    """
    Get monthly prediction statistics for dashboard charts.
    Groups all predictions by month and returns total and spam counts.
    Database-agnostic: works for both PostgreSQL and SQLite.
    """
    # Detect database dialect
    bind = db.get_bind()
    dialect = bind.dialect.name if bind is not None else ""

    # Use date_trunc for Postgres, strftime for SQLite
    if dialect == "sqlite":
        # SQLite: strftime returns string "YYYY-MM-01"
        month_column = func.strftime("%Y-%m-01", Prediction.created_at).label("month")
    else:
        # PostgreSQL (and others that support date_trunc)
        month_column = func.date_trunc("month", Prediction.created_at).label("month")

    rows = (
        db.query(
            month_column,
            func.count(Prediction.id).label("total"),
            func.sum(
                case((Prediction.type == PredictionType.SPAM, 1), else_=0)
            ).label("spam_total"),
        )
        .group_by(month_column)
        .order_by(month_column)
        .all()
    )

    result = []
    for row in rows:
        month_value = row.month
        # For Postgres, month_value is a datetime from date_trunc.
        # For SQLite, month_value is already a string from strftime.
        if dialect == "sqlite":
            month_str = month_value or ""
        else:
            month_str = month_value.strftime("%Y-%m-01") if month_value is not None else ""
        result.append(
            {
                "month": month_str,
                "total": int(row.total or 0),
                "spam_total": int(row.spam_total or 0),
            }
        )

    return result

@router.get("/reviews")
async def get_reviews(
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
    status: str = "pending",
    limit: int = 100,
):
    if user.role != UserRole.ADMIN:
        raise HTTPException(status_code=403, detail="Admin only")

    review_status = status.strip().lower()
    query = db.query(Prediction)
    if review_status != "all":
        if review_status not in {"pending", "approved", "rejected"}:
            raise HTTPException(status_code=400, detail="status must be one of: pending, approved, rejected, all")
        query = query.filter(Prediction.review_status == review_status)

    rows = query.order_by(Prediction.created_at.desc()).limit(limit).all()
    return [row.to_dict() for row in rows]


@router.post("/predictions/{prediction_id}/review")
async def review_prediction(
    prediction_id: int,
    payload: ReviewDecision,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    if user.role != UserRole.ADMIN:
        raise HTTPException(status_code=403, detail="Admin only")

    prediction = db.query(Prediction).filter(Prediction.id == prediction_id).first()
    if not prediction:
        raise HTTPException(status_code=404, detail="Prediction not found")

    prediction.review_status = "approved" if payload.approve else "rejected"
    prediction.reviewed_label = payload.reviewed_label if payload.approve else None
    prediction.reviewed_at = func.now()
    if payload.approve and payload.reviewed_label:
        prediction.predicted_label = payload.reviewed_label
    db.commit()
    db.refresh(prediction)
    return prediction.to_dict()


@router.get("/timeline")
async def get_timeline(db: Session = Depends(get_db), range: str = "month", limit: int = 12):
    """
    Generic timeline endpoint for dashboard.
    range: day | month | year
    Returns counts grouped by bucket, including news_total and spam_total.
    """
    unit = range.lower().strip()
    if unit not in {"day", "month", "year"}:
        raise HTTPException(status_code=400, detail="range must be one of: day, month, year")
    if limit < 1 or limit > 365:
        raise HTTPException(status_code=400, detail="limit must be between 1 and 365")

    # Detect database dialect
    bind = db.get_bind()
    dialect = bind.dialect.name if bind is not None else ""

    # Build bucket column depending on database
    if dialect == "sqlite":
        # SQLite: use strftime (returns string)
        if unit == "day":
            bucket_col = func.strftime("%Y-%m-%d", Prediction.created_at).label("bucket")
        elif unit == "year":
            bucket_col = func.strftime("%Y", Prediction.created_at).label("bucket")
        else:  # month
            bucket_col = func.strftime("%Y-%m", Prediction.created_at).label("bucket")
    else:
        # PostgreSQL (and others that support date_trunc)
        bucket_col = func.date_trunc(unit, Prediction.created_at).label("bucket")

    rows = (
        db.query(
            bucket_col,
            func.count(Prediction.id).label("total"),
            func.sum(case((Prediction.type == PredictionType.SPAM, 1), else_=0)).label("spam_total"),
            func.sum(case((Prediction.type == PredictionType.NEWS, 1), else_=0)).label("news_total"),
        )
        .group_by(bucket_col)
        .order_by(bucket_col.desc())
        .limit(limit)
        .all()
    )

    # Return ascending for charts
    rows = list(reversed(rows))

    out = []
    for r in rows:
        dt = r.bucket
        # For SQLite, dt is already string from strftime; for Postgres it's datetime
        if dialect == "sqlite":
            label = dt or ""
        else:
            if unit == "day":
                label = dt.strftime("%Y-%m-%d") if dt else ""
            elif unit == "year":
                label = dt.strftime("%Y") if dt else ""
            else:
                label = dt.strftime("%Y-%m") if dt else ""

        out.append(
            {
                "bucket": label,
                "total": int(r.total or 0),
                "spam_total": int(r.spam_total or 0),
                "news_total": int(r.news_total or 0),
            }
        )

    return out
