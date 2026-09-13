from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query

from app import schemas
from app.deps import get_current_user
from app.storage import json_db, next_id
from app.utils import spent_for_budget, budget_status

router = APIRouter(prefix="/budgets", tags=["Budgets"])


def _serialize(budget: dict, user_transactions: List[dict]) -> schemas.BudgetOut:
    spent = spent_for_budget(user_transactions, budget["month"], budget.get("category"))
    limit_amount = budget["limit_amount"]
    remaining = limit_amount - spent
    percent_used = (spent / limit_amount * 100) if limit_amount else 0.0
    return schemas.BudgetOut(
        budget_id=budget["budget_id"],
        month=budget["month"],
        category=budget.get("category"),
        limit_amount=limit_amount,
        spent=round(spent, 2),
        remaining=round(remaining, 2),
        percent_used=round(percent_used, 2),
        status=budget_status(spent, limit_amount),
    )


@router.post("", response_model=schemas.BudgetOut, status_code=201)
def create_budget(
    payload: schemas.BudgetCreate,
    current_user: dict = Depends(get_current_user),
):
    with json_db() as db:
        existing = next(
            (
                b
                for b in db["budgets"]
                if b["user_id"] == current_user["user_id"]
                and b["month"] == payload.month
                and b.get("category") == payload.category
            ),
            None,
        )
        if existing:
            raise HTTPException(
                status_code=400,
                detail="A budget for this month/category already exists. Update it instead.",
            )

        budget = {
            "budget_id": next_id(db, "budgets"),
            "user_id": current_user["user_id"],
            "month": payload.month,
            "category": payload.category,
            "limit_amount": payload.limit_amount,
        }
        db["budgets"].append(budget)
        user_transactions = [t for t in db["transactions"] if t["user_id"] == current_user["user_id"]]

    return _serialize(budget, user_transactions)


@router.get("", response_model=List[schemas.BudgetOut])
def list_budgets(
    month: Optional[str] = Query(default=None, pattern=r"^\d{4}-\d{2}$"),
    current_user: dict = Depends(get_current_user),
):
    with json_db() as db:
        budgets = [b for b in db["budgets"] if b["user_id"] == current_user["user_id"]]
        if month:
            budgets = [b for b in budgets if b["month"] == month]
        user_transactions = [t for t in db["transactions"] if t["user_id"] == current_user["user_id"]]

    budgets.sort(key=lambda b: b["month"], reverse=True)
    return [_serialize(b, user_transactions) for b in budgets]


@router.delete("/{budget_id}", status_code=204)
def delete_budget(
    budget_id: int,
    current_user: dict = Depends(get_current_user),
):
    with json_db() as db:
        budget = next(
            (b for b in db["budgets"] if b["budget_id"] == budget_id and b["user_id"] == current_user["user_id"]),
            None,
        )
        if not budget:
            raise HTTPException(status_code=404, detail="Budget not found.")
        db["budgets"] = [b for b in db["budgets"] if b["budget_id"] != budget_id]
    return None
