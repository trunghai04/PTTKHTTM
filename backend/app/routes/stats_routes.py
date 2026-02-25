from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func
from app.database.db import get_db
from app.database.models import Prediction, PredictionType

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
