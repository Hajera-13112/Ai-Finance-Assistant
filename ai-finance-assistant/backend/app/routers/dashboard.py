from fastapi import APIRouter, Depends

from app import schemas
from app.deps import get_current_user
from app.storage import json_db
from app.utils import monthly_expense_series
from app.ml.forecast import forecast_next_month

router = APIRouter(tags=["Dashboard"])


@router.get("/dashboard", response_model=schemas.DashboardSummary)
def get_dashboard(current_user: dict = Depends(get_current_user)):
    with json_db() as db:
        txs = [t for t in db["transactions"] if t["user_id"] == current_user["user_id"]]

    income_total = sum(t["amount"] for t in txs if t["type"] == "income")
    expense_total = sum(t["amount"] for t in txs if t["type"] == "expense")

    category_totals: dict = {}
    for t in txs:
        if t["type"] != "expense":
            continue
        cat = t.get("category") or "Other"
        category_totals[cat] = category_totals.get(cat, 0.0) + t["amount"]

    category_breakdown = [
        schemas.CategoryBreakdown(category=cat, total=round(total, 2))
        for cat, total in sorted(category_totals.items(), key=lambda kv: kv[1], reverse=True)
    ]

    trend_rows = monthly_expense_series(txs)
    monthly_trend = [schemas.MonthlyTrendPoint(**row) for row in trend_rows]

    expense_series = [row["expense"] for row in trend_rows]
    forecast_value, forecast_note = forecast_next_month(expense_series)

    return schemas.DashboardSummary(
        total_income=round(income_total, 2),
        total_expense=round(expense_total, 2),
        balance=round(income_total - expense_total, 2),
        category_breakdown=category_breakdown,
        monthly_trend=monthly_trend,
        forecast_next_month=forecast_value,
        forecast_note=forecast_note,
    )
