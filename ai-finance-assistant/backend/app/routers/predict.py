from fastapi import APIRouter, Depends, HTTPException

from app import schemas
from app.deps import get_current_user
from app.ml.classifier import expense_classifier

router = APIRouter(tags=["Prediction"])


@router.post("/predict-category", response_model=schemas.CategoryPredictResponse)
def predict_category(
    payload: schemas.CategoryPredictRequest,
    current_user: dict = Depends(get_current_user),
):
    if not expense_classifier.is_ready():
        raise HTTPException(
            status_code=503,
            detail="The classification model has not been trained yet. Run train_model.py first.",
        )

    predicted_category, confidence, probabilities = expense_classifier.predict(payload.description)
    return schemas.CategoryPredictResponse(
        predicted_category=predicted_category,
        confidence=confidence,
        probabilities=probabilities,
    )
