from fastapi import APIRouter, Depends
from pydantic import BaseModel, Field

from app.deps import get_current_user
from app.storage import json_db
from app.utils import monthly_expense_series, category_totals_for_month, current_month_str
from app.ml.forecast import forecast_next_month
from app.ml.insights_engine import generate_insights
from app.routers.budgets import _serialize as serialize_budget
from app.chatbot import generate_reply

router = APIRouter(tags=["Chatbot"])


class ChatRequest(BaseModel):
    message: str = Field(min_length=1, max_length=500)


class ChatResponse(BaseModel):
    reply: str


@router.post("/chatbot", response_model=ChatResponse)
def chat(payload: ChatRequest, current_user: dict = Depends(get_current_user)):
    month = current_month_str()

    with json_db() as db:
        txs = [t for t in db["transactions"] if t["user_id"] == current_user["user_id"]]
        month_budgets = [
            b for b in db["budgets"] if b["user_id"] == current_user["user_id"] and b["month"] == month
        ]
        serialized_budgets = [serialize_budget(b, txs).model_dump() for b in month_budgets]

    total_income = sum(t["amount"] for t in txs if t["type"] == "income")
    total_expense = sum(t["amount"] for t in txs if t["type"] == "expense")

    category_totals: dict = {}
    for t in txs:
        if t["type"] != "expense":
            continue
        cat = t.get("category") or "Other"
        category_totals[cat] = category_totals.get(cat, 0.0) + t["amount"]
    category_breakdown = [
        {"category": cat, "total": round(total, 2)}
        for cat, total in sorted(category_totals.items(), key=lambda kv: kv[1], reverse=True)
    ]

    trend_rows = monthly_expense_series(txs)
    expense_series = [row["expense"] for row in trend_rows]
    forecast_value, forecast_note = forecast_next_month(expense_series)

    this_month_totals = category_totals_for_month(txs, month)
    insights = generate_insights(
        category_totals_this_month=this_month_totals,
        category_totals_last_month={},
        budgets=serialized_budgets,
        total_income=float(total_income),
        total_expense=float(sum(this_month_totals.values())),
    )

    context = {
        "user_name": current_user["name"],
        "total_income": round(total_income, 2),
        "total_expense": round(total_expense, 2),
        "balance": round(total_income - total_expense, 2),
        "category_breakdown": category_breakdown,
        "budgets": serialized_budgets,
        "forecast_next_month": forecast_value,
        "forecast_note": forecast_note,
        "insights": insights,
    }

    reply = generate_reply(payload.message, context)
    return ChatResponse(reply=reply)
