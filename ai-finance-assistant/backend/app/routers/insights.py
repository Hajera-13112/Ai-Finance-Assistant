import datetime as dt

from fastapi import APIRouter, Depends

from app import schemas
from app.deps import get_current_user
from app.storage import json_db, next_id
from app.utils import category_totals_for_month, current_month_str, previous_month_str
from app.routers.budgets import _serialize as serialize_budget
from app.ml.insights_engine import generate_insights

router = APIRouter(tags=["Insights"])


@router.get("/insights", response_model=schemas.InsightsResponse)
def get_insights(current_user: dict = Depends(get_current_user)):
    month = current_month_str()
    prev_month = previous_month_str(month)

    with json_db() as db:
        txs = [t for t in db["transactions"] if t["user_id"] == current_user["user_id"]]
        month_budgets = [
            b for b in db["budgets"] if b["user_id"] == current_user["user_id"] and b["month"] == month
        ]
        serialized_budgets = [serialize_budget(b, txs).model_dump() for b in month_budgets]

        this_month_totals = category_totals_for_month(txs, month)
        last_month_totals = category_totals_for_month(txs, prev_month)
        total_income = sum(t["amount"] for t in txs if t["type"] == "income")
        total_expense = sum(this_month_totals.values())

        insight_strings = generate_insights(
            category_totals_this_month=this_month_totals,
            category_totals_last_month=last_month_totals,
            budgets=serialized_budgets,
            total_income=float(total_income),
            total_expense=float(total_expense),
        )

        for text in insight_strings:
            db["insights"].append(
                {
                    "insight_id": next_id(db, "insights"),
                    "user_id": current_user["user_id"],
                    "insight_text": text,
                    "created_at": dt.datetime.utcnow().isoformat(),
                }
            )

    return schemas.InsightsResponse(insights=insight_strings)
