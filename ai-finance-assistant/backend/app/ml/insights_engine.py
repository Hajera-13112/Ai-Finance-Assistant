"""
Rule-based financial insights.

Per SRS 9.7: identify high-spending categories, compare actual spending with
budgets, and provide simple, understandable suggestions. This module never
produces professional financial advice -- callers should always surface the
disclaimer alongside these strings.
"""
from typing import List, Dict


def generate_insights(
    category_totals_this_month: Dict[str, float],
    category_totals_last_month: Dict[str, float],
    budgets: List[dict],
    total_income: float,
    total_expense: float,
) -> List[str]:
    insights: List[str] = []

    # 1. Highest spending category this month.
    if category_totals_this_month:
        top_category = max(category_totals_this_month, key=category_totals_this_month.get)
        top_amount = category_totals_this_month[top_category]
        if top_amount > 0:
            insights.append(
                f"Your highest spending category this month is {top_category} "
                f"at \u20b9{top_amount:,.2f}."
            )

    # 2. Month-over-month category comparisons.
    for category, current in category_totals_this_month.items():
        previous = category_totals_last_month.get(category, 0.0)
        if previous <= 0:
            continue
        change_pct = ((current - previous) / previous) * 100
        if change_pct >= 20:
            insights.append(
                f"Your {category} expenses increased by {change_pct:.0f}% "
                f"compared with last month."
            )
        elif change_pct <= -20:
            insights.append(
                f"Your {category} expenses decreased by {abs(change_pct):.0f}% "
                f"compared with last month. Nice work."
            )

    # 3. Budget comparisons.
    for budget in budgets:
        pct = budget.get("percent_used", 0)
        label = budget.get("category") or "overall"
        if pct >= 100:
            insights.append(
                f"You have exceeded your {label} budget for {budget.get('month')} "
                f"by \u20b9{budget.get('spent', 0) - budget.get('limit_amount', 0):,.2f}."
            )
        elif pct >= 80:
            insights.append(
                f"You have used {pct:.0f}% of your {label} budget for "
                f"{budget.get('month')}. Consider slowing down spending in this area."
            )

    # 4. Savings rate.
    if total_income > 0:
        savings_rate = ((total_income - total_expense) / total_income) * 100
        if savings_rate < 0:
            insights.append(
                "Your expenses this month exceed your income. Review your "
                "spending to avoid a growing shortfall."
            )
        elif savings_rate < 10:
            insights.append(
                f"You're saving about {savings_rate:.0f}% of your income this "
                f"month, which is on the lower side. Small cuts in your top "
                f"spending category could help."
            )

    if not insights:
        insights.append(
            "Not enough data yet to generate meaningful insights. Keep logging "
            "transactions and check back soon."
        )

    return insights
