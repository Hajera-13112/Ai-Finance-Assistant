import datetime as dt
from typing import Optional, List, Dict

from fastapi import APIRouter, Depends, HTTPException, Query

from app import schemas
from app.deps import get_current_user
from app.storage import json_db, next_id
from app.ml.classifier import expense_classifier

router = APIRouter(prefix="/transactions", tags=["Transactions"])


def _serialize(tx: dict, predictions_by_tx: Dict[int, dict]) -> schemas.TransactionOut:
    out = schemas.TransactionOut(
        transaction_id=tx["transaction_id"],
        date=tx["date"],
        description=tx["description"],
        amount=tx["amount"],
        type=tx["type"],
        category=tx.get("category"),
    )
    pred = predictions_by_tx.get(tx["transaction_id"])
    if pred:
        out.predicted_category = pred["predicted_category"]
        out.confidence = pred["confidence"]
    return out


@router.post("", response_model=schemas.TransactionOut, status_code=201)
def create_transaction(
    payload: schemas.TransactionCreate,
    current_user: dict = Depends(get_current_user),
):
    category = payload.category
    predicted_category = None
    confidence = None

    # Auto-categorize expenses when the user hasn't already chosen a category.
    if payload.type == "expense" and not category and expense_classifier.is_ready():
        try:
            predicted_category, confidence, _ = expense_classifier.predict(payload.description)
            category = predicted_category
        except RuntimeError:
            category = "Other"
    elif payload.type == "expense" and not category:
        category = "Other"

    with json_db() as db:
        tx_id = next_id(db, "transactions")
        tx = {
            "transaction_id": tx_id,
            "user_id": current_user["user_id"],
            "date": payload.date.isoformat(),
            "description": payload.description,
            "amount": payload.amount,
            "type": payload.type,
            "category": category,
            "created_at": dt.datetime.utcnow().isoformat(),
        }
        db["transactions"].append(tx)

        predictions_by_tx: Dict[int, dict] = {}
        if predicted_category is not None:
            prediction = {
                "prediction_id": next_id(db, "predictions"),
                "transaction_id": tx_id,
                "predicted_category": predicted_category,
                "confidence": confidence,
                "created_at": dt.datetime.utcnow().isoformat(),
            }
            db["predictions"].append(prediction)
            predictions_by_tx[tx_id] = prediction

    return _serialize(tx, predictions_by_tx)


@router.get("", response_model=List[schemas.TransactionOut])
def list_transactions(
    current_user: dict = Depends(get_current_user),
    type: Optional[str] = Query(default=None, pattern="^(income|expense)$"),
    category: Optional[str] = None,
    search: Optional[str] = Query(default=None, description="Search in description"),
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
):
    with json_db() as db:
        txs = [t for t in db["transactions"] if t["user_id"] == current_user["user_id"]]
        predictions_by_tx = {p["transaction_id"]: p for p in db["predictions"]}

    if type:
        txs = [t for t in txs if t["type"] == type]
    if category:
        txs = [t for t in txs if t.get("category") == category]
    if search:
        needle = search.lower()
        txs = [t for t in txs if needle in t["description"].lower()]
    if start_date:
        txs = [t for t in txs if t["date"] >= start_date]
    if end_date:
        txs = [t for t in txs if t["date"] <= end_date]

    txs.sort(key=lambda t: (t["date"], t["transaction_id"]), reverse=True)
    return [_serialize(t, predictions_by_tx) for t in txs]


def _find_owned_transaction(db: dict, current_user: dict, transaction_id: int) -> dict:
    tx = next(
        (
            t
            for t in db["transactions"]
            if t["transaction_id"] == transaction_id and t["user_id"] == current_user["user_id"]
        ),
        None,
    )
    if not tx:
        raise HTTPException(status_code=404, detail="Transaction not found.")
    return tx


@router.put("/{transaction_id}", response_model=schemas.TransactionOut)
def update_transaction(
    transaction_id: int,
    payload: schemas.TransactionUpdate,
    current_user: dict = Depends(get_current_user),
):
    with json_db() as db:
        tx = _find_owned_transaction(db, current_user, transaction_id)

        updates = payload.model_dump(exclude_unset=True)
        for field, value in updates.items():
            if field == "date" and value is not None:
                value = value.isoformat()
            tx[field] = value

        predictions_by_tx = {p["transaction_id"]: p for p in db["predictions"]}

    return _serialize(tx, predictions_by_tx)


@router.delete("/{transaction_id}", status_code=204)
def delete_transaction(
    transaction_id: int,
    current_user: dict = Depends(get_current_user),
):
    with json_db() as db:
        _find_owned_transaction(db, current_user, transaction_id)  # raises 404 if missing/not owned
        db["transactions"] = [t for t in db["transactions"] if t["transaction_id"] != transaction_id]
        db["predictions"] = [p for p in db["predictions"] if p["transaction_id"] != transaction_id]
    return None
