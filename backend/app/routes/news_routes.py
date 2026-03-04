from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.auth.deps import get_current_user, get_optional_user
from app.database.db import get_db
from app.database.models import Prediction, PredictionType, User
from app.services.news_service import news_classifier

router = APIRouter()

class NewsRequest(BaseModel):
    text: str

class NewsBulkRequest(BaseModel):
    texts: list[str]

class NewsResponse(BaseModel):
    label: str
    confidence: float
    id: int | None = None

class NewsBulkResponse(BaseModel):
    results: list[NewsResponse]
    total: int

@router.post("/predict", response_model=NewsResponse)
async def predict_news(
    request: NewsRequest,
    db: Session = Depends(get_db),
    user: User | None = Depends(get_optional_user),
):
    """
    Predict news category
    """
    try:
        if not request.text or len(request.text.strip()) == 0:
            raise HTTPException(status_code=400, detail="Text cannot be empty")
        
        # Get prediction
        result = news_classifier.predict(request.text)
        
        # Save to database (with error handling). If user is logged in, attach user_id.
        try:
            prediction = Prediction(
                text=request.text,
                type=PredictionType.NEWS,
                predicted_label=result["label"],
                confidence=result["confidence"],
                user_id=user.id if user else None,
                source="manual",
            )
            db.add(prediction)
            db.commit()
            db.refresh(prediction)
            prediction_id = prediction.id
        except Exception as db_error:
            # If DB fails, still return prediction but without ID
            db.rollback()
            prediction_id = None
        
        return NewsResponse(
            label=result["label"],
            confidence=result["confidence"],
            id=prediction_id
        )
    except FileNotFoundError as e:
        error_msg = str(e)
        print(f"❌ Model error: {error_msg}")
        raise HTTPException(
            status_code=503, 
            detail=f"Model not available. {error_msg}. Please train the model first by running: python train_model.py"
        )
    except Exception as e:
        error_msg = str(e)
        print(f"❌ Prediction error: {error_msg}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Prediction failed: {error_msg}")

@router.post("/predict/bulk", response_model=NewsBulkResponse)
async def predict_news_bulk(
    request: NewsBulkRequest,
    db: Session = Depends(get_db),
    user: User | None = Depends(get_optional_user),
):
    """
    Bulk news prediction. Saves each prediction to DB when available.
    """
    try:
        if not request.texts or len(request.texts) == 0:
            raise HTTPException(status_code=400, detail="texts cannot be empty")

        cleaned = [t for t in request.texts if isinstance(t, str) and t.strip()]
        if len(cleaned) == 0:
            raise HTTPException(status_code=400, detail="All texts are empty")

        results: list[NewsResponse] = []

        for text in cleaned:
            result = news_classifier.predict(text)

            prediction_id = None
            try:
                prediction = Prediction(
                    text=text,
                    type=PredictionType.NEWS,
                    predicted_label=result["label"],
                    confidence=result["confidence"],
                    user_id=user.id if user else None,
                    source="manual",
                )
                db.add(prediction)
                db.commit()
                db.refresh(prediction)
                prediction_id = prediction.id
            except Exception:
                db.rollback()

            results.append(
                NewsResponse(
                    label=result["label"],
                    confidence=result["confidence"],
                    id=prediction_id,
                )
            )

        return NewsBulkResponse(results=results, total=len(results))
    except FileNotFoundError as e:
        error_msg = str(e)
        raise HTTPException(
            status_code=503,
            detail=f"Model not available. {error_msg}. Please train the model first by running: python train_model.py",
        )
    except HTTPException:
        raise
    except Exception as e:
        error_msg = str(e)
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Bulk prediction failed: {error_msg}")

@router.get("/history")
async def get_news_history(
    db: Session = Depends(get_db),
    limit: int = 50,
    user: User = Depends(get_current_user),
):
    """
    Get news prediction history for the current authenticated user.
    """
    predictions = (
        db.query(Prediction)
        .filter(
            Prediction.type == PredictionType.NEWS,
            Prediction.user_id == user.id,
        )
        .order_by(Prediction.created_at.desc())
        .limit(limit)
        .all()
    )

    return [pred.to_dict() for pred in predictions]

@router.delete("/history")
async def clear_news_history(
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """
    Delete all news predictions for the current authenticated user.
    """
    deleted = (
        db.query(Prediction)
        .filter(
            Prediction.type == PredictionType.NEWS,
            Prediction.user_id == user.id,
        )
        .delete(synchronize_session=False)
    )
    db.commit()
    return {"deleted": int(deleted)}
