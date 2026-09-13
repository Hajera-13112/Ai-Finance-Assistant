import datetime as dt
from typing import Optional, Dict, List


def month_bounds(month_str: str):
    """month_str is 'YYYY-MM'. Returns (first_day, last_day) as date objects."""
    year, month = (int(p) for p in month_str.split("-"))
    first_day = dt.date(year, month, 1)
    if month == 12:
        last_day = dt.date(year, 12, 31)
    else:
        last_day = dt.date(year, month + 1, 1) - dt.timedelta(days=1)
    return first_day, last_day


def spent_for_budget(transactions: List[dict], month: str, category: Optional[str]) -> float:
    first_day, last_day = month_bounds(month)
    total = 0.0
    for t in transactions:
        if t["type"] != "expense":
            continue
        t_date = dt.date.fromisoformat(t["date"])
        if not (first_day <= t_date <= last_day):
            continue
        if category and t.get("category") != category:
            continue
        total += t["amount"]
    return total


def budget_status(spent: float, limit_amount: float) -> str:
    if limit_amount <= 0:
        return "ok"
    pct = (spent / limit_amount) * 100
    if pct >= 100:
        return "exceeded"
    if pct >= 80:
        return "warning"
    return "ok"


def category_totals_for_month(transactions: List[dict], month: str) -> Dict[str, float]:
    first_day, last_day = month_bounds(month)
    totals: Dict[str, float] = {}
    for t in transactions:
        if t["type"] != "expense":
            continue
        t_date = dt.date.fromisoformat(t["date"])
        if not (first_day <= t_date <= last_day):
            continue
        cat = t.get("category") or "Other"
        totals[cat] = totals.get(cat, 0.0) + t["amount"]
    return totals


def previous_month_str(month: str) -> str:
    year, month_num = (int(p) for p in month.split("-"))
    first_day = dt.date(year, month_num, 1)
    prev_last_day = first_day - dt.timedelta(days=1)
    return prev_last_day.strftime("%Y-%m")


def current_month_str() -> str:
    return dt.date.today().strftime("%Y-%m")


def monthly_expense_series(transactions: List[dict]) -> List[Dict]:
    """Returns chronological list of {month, income, expense} across all history."""
    combined: Dict[str, Dict[str, float]] = {}
    for t in transactions:
        month_key = t["date"][:7]  # 'YYYY-MM' prefix of an ISO date string
        combined.setdefault(month_key, {"income": 0.0, "expense": 0.0})
        combined[month_key][t["type"]] += t["amount"]

    return [
        {"month": month, "income": vals["income"], "expense": vals["expense"]}
        for month, vals in sorted(combined.items())
    ]
