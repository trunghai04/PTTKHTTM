from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session
from app.database.db import get_db
from app.database.models import Prediction, PredictionType
from app.services.news_service import news_classifier

router = APIRouter()

class NewsRequest(BaseModel):
    text: str

class NewsResponse(BaseModel):
    label: str
    confidence: float
    id: int = None

@router.post("/predict", response_model=NewsResponse)
async def predict_news(request: NewsRequest, db: Session = Depends(get_db)):
    """
    Predict news category
    """
    try:
        if not request.text or len(request.text.strip()) == 0:
            raise HTTPException(status_code=400, detail="Text cannot be empty")
        
        # Get prediction
        result = news_classifier.predict(request.text)
        
        # Save to database (with error handling)
        try:
            prediction = Prediction(
                text=request.text,
                type=PredictionType.NEWS,
                predicted_label=result["label"],
                confidence=result["confidence"]
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

@router.get("/history")
async def get_news_history(db: Session = Depends(get_db), limit: int = 50):
    """
    Get news prediction history
    """
    predictions = db.query(Prediction).filter(
        Prediction.type == PredictionType.NEWS
    ).order_by(Prediction.created_at.desc()).limit(limit).all()
    
    return [pred.to_dict() for pred in predictions]
