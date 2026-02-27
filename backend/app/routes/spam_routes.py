from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session
from app.database.db import get_db
from app.database.models import Prediction, PredictionType
from app.services.spam_service import spam_classifier

router = APIRouter()

class SpamRequest(BaseModel):
    text: str

class SpamBulkRequest(BaseModel):
    texts: list[str]

class SpamResponse(BaseModel):
    label: str
    confidence: float
    spam_probability: float | None = None
    not_spam_probability: float | None = None
    id: int | None = None
    warning: str | None = None  # Warning if confidence is low

class SpamBulkResponse(BaseModel):
    results: list[SpamResponse]
    total: int
    spam_count: int
    not_spam_count: int

@router.post("/predict", response_model=SpamResponse)
async def predict_spam(request: SpamRequest, db: Session = Depends(get_db)):
    """
    Predict if text is spam or not spam
    """
    try:
        if not request.text or len(request.text.strip()) == 0:
            raise HTTPException(status_code=400, detail="Text cannot be empty")
        
        # Get prediction
        result = spam_classifier.predict(request.text)
        
        # Add warning if confidence is low
        warning = None
        if result.get("confidence", 0) < 0.7:
            warning = f"Low confidence prediction ({result['confidence']:.1%}). Model may need more training data."
        
        # Save to database (with error handling)
        try:
            prediction = Prediction(
                text=request.text,
                type=PredictionType.SPAM,
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
        
        return SpamResponse(
            label=result["label"],
            confidence=result["confidence"],
            spam_probability=result.get("spam_probability"),
            not_spam_probability=result.get("not_spam_probability"),
            id=prediction_id,
            warning=warning
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

@router.post("/predict/bulk", response_model=SpamBulkResponse)
async def predict_spam_bulk(request: SpamBulkRequest, db: Session = Depends(get_db)):
    """
    Bulk spam prediction. Saves each prediction to DB when available.
    """
    try:
        if not request.texts or len(request.texts) == 0:
            raise HTTPException(status_code=400, detail="texts cannot be empty")

        cleaned = [t for t in request.texts if isinstance(t, str) and t.strip()]
        if len(cleaned) == 0:
            raise HTTPException(status_code=400, detail="All texts are empty")

        results: list[SpamResponse] = []
        spam_count = 0
        not_spam_count = 0

        for text in cleaned:
            result = spam_classifier.predict(text)

            warning = None
            if result.get("confidence", 0) < 0.7:
                warning = f"Low confidence prediction ({result['confidence']:.1%}). Model may need more training data."

            prediction_id = None
            try:
                prediction = Prediction(
                    text=text,
                    type=PredictionType.SPAM,
                    predicted_label=result["label"],
                    confidence=result["confidence"],
                )
                db.add(prediction)
                db.commit()
                db.refresh(prediction)
                prediction_id = prediction.id
            except Exception:
                db.rollback()

            label_lower = str(result.get("label", "")).lower()
            if label_lower == "spam":
                spam_count += 1
            else:
                not_spam_count += 1

            results.append(
                SpamResponse(
                    label=result["label"],
                    confidence=result["confidence"],
                    spam_probability=result.get("spam_probability"),
                    not_spam_probability=result.get("not_spam_probability"),
                    id=prediction_id,
                    warning=warning,
                )
            )

        return SpamBulkResponse(
            results=results,
            total=len(results),
            spam_count=spam_count,
            not_spam_count=not_spam_count,
        )
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
async def get_spam_history(db: Session = Depends(get_db), limit: int = 50):
    """
    Get spam prediction history
    """
    predictions = db.query(Prediction).filter(
        Prediction.type == PredictionType.SPAM
    ).order_by(Prediction.created_at.desc()).limit(limit).all()
    
    return [pred.to_dict() for pred in predictions]

@router.delete("/history")
async def clear_spam_history(db: Session = Depends(get_db)):
    """
    Delete all spam predictions.
    """
    deleted = (
        db.query(Prediction)
        .filter(Prediction.type == PredictionType.SPAM)
        .delete(synchronize_session=False)
    )
    db.commit()
    return {"deleted": int(deleted)}
