"""
Rule-based finance chatbot (SRS System Module 8): answers general
finance-application questions using simple keyword/intent matching, plus
live answers pulled from the user's own transaction/budget data. This is
intentionally a simple, explainable pattern-matcher -- not an LLM -- to
match the "beginner-friendly, explainable" spirit of the rest of the SRS.
"""
from typing import Dict, Any, Optional


def _currency(value: float) -> str:
    return f"\u20b9{value:,.2f}"


GREETINGS = ["hi", "hello", "hey", "good morning", "good afternoon", "good evening"]
THANKS = ["thank", "thanks", "thx"]

HELP_ADD_TX = [
    "add transaction", "add expense", "add income", "log expense",
    "log a transaction", "how do i add", "record a transaction", "new transaction",
]
HELP_EDIT_DELETE = ["edit transaction", "delete transaction", "update transaction", "remove transaction"]
HELP_BUDGET = ["set a budget", "set budget", "create budget", "how do i budget", "budget limit"]
HELP_CATEGORY = ["categor"]  # catches category / categorize / categories / categorized
HELP_FORECAST = ["forecast", "predict", "estimate my spending", "future spending"]

BALANCE_KEYWORDS = ["balance", "how much do i have", "money left", "left over"]
INCOME_KEYWORDS = ["income", "earned", "salary total", "how much did i earn"]
EXPENSE_KEYWORDS = ["total expense", "how much did i spend", "spending total", "total spent"]
TOP_CATEGORY_KEYWORDS = ["top category", "highest spending", "where did my money go", "biggest expense"]
BUDGET_STATUS_KEYWORDS = ["budget status", "over budget", "am i over", "budget usage", "how much budget"]
INSIGHT_KEYWORDS = ["insight", "advice", "tip", "suggestion", "recommend"]


def _matches(message: str, keywords) -> bool:
    return any(k in message for k in keywords)


def generate_reply(message: str, context: Dict[str, Any]) -> str:
    """
    context expects keys: user_name, total_income, total_expense, balance,
    category_breakdown (list of {category,total}, highest first), budgets
    (list of dicts with category/limit_amount/spent/percent_used/status),
    forecast_next_month, forecast_note, insights (list[str]).
    """
    text = message.lower().strip()

    if not text:
        return "I didn't catch that -- could you type your question?"

    if _matches(text, GREETINGS):
        name = (context.get("user_name") or "").split(" ")[0]
        greet = f"Hi {name}!" if name else "Hi there!"
        return (
            f"{greet} I can tell you your balance, spending by category, "
            f"budget status, or the next-month forecast -- or walk you "
            f"through adding a transaction or setting a budget. What do "
            f"you need?"
        )

    if _matches(text, THANKS):
        return "You're welcome! Anything else you'd like to check?"

    if _matches(text, HELP_ADD_TX):
        return (
            "Go to the Transactions page, fill in the date, description, "
            "and amount, choose Income or Expense, and click Add. For "
            "expenses, leave the category on \u201cAuto-detect\u201d and the AI "
            "model will suggest one based on the description."
        )

    if _matches(text, HELP_EDIT_DELETE):
        return (
            "On the Transactions page, each row has a Delete button on the "
            "right. There's no inline edit yet -- delete the entry and add "
            "a corrected one."
        )

    if _matches(text, HELP_BUDGET):
        return (
            "Go to the Budgets page, pick a month, choose a category (or "
            "leave it as \u201cOverall\u201d for a total monthly limit), enter the "
            "limit amount, and click \u201cSet budget\u201d. The progress bar "
            "updates automatically as you log expenses."
        )

    if _matches(text, HELP_CATEGORY):
        return (
            "Expenses are grouped into Food, Transport, Shopping, Bills, "
            "Entertainment, Health, Education, or Other. When you add an "
            "expense without picking a category, the AI model reads the "
            "description and predicts one -- you can always override it "
            "by choosing a category yourself."
        )

    if _matches(text, HELP_FORECAST):
        forecast: Optional[float] = context.get("forecast_next_month")
        note = context.get("forecast_note", "")
        if forecast is None:
            return (
                "The forecast estimates next month's spending from your "
                "history using a simple trend model. You don't have "
                "enough transactions yet for an estimate -- add some and "
                "check back."
            )
        return f"Based on your history, next month's spending is estimated at about {_currency(forecast)}. {note}"

    if _matches(text, BALANCE_KEYWORDS):
        return f"Your current balance is {_currency(context.get('balance', 0))}."

    if _matches(text, INCOME_KEYWORDS):
        return f"Your total recorded income is {_currency(context.get('total_income', 0))}."

    if _matches(text, EXPENSE_KEYWORDS):
        return f"Your total recorded expenses are {_currency(context.get('total_expense', 0))}."

    if _matches(text, TOP_CATEGORY_KEYWORDS):
        breakdown = context.get("category_breakdown") or []
        if not breakdown:
            return "You don't have any expenses logged yet, so there's no category breakdown to show."
        top = breakdown[0]
        return f"Your highest spending category is {top['category']} at {_currency(top['total'])}."

    if _matches(text, BUDGET_STATUS_KEYWORDS):
        budgets = context.get("budgets") or []
        if not budgets:
            return "You haven't set any budgets for this month yet. Head to the Budgets page to create one."
        lines = []
        for b in budgets:
            label = b.get("category") or "Overall"
            lines.append(
                f"{label}: {_currency(b['spent'])} of {_currency(b['limit_amount'])} "
                f"({b['percent_used']:.0f}%, {b['status']})"
            )
        return "Here's your budget status for this month:\n" + "\n".join(lines)

    if _matches(text, INSIGHT_KEYWORDS):
        insights = context.get("insights") or []
        if not insights:
            return "No particular insights yet -- log a few more transactions and check back."
        return "Here's what I've noticed:\n" + "\n".join(f"- {i}" for i in insights)

    return (
        "I'm not sure about that one. I can help with your balance, "
        "income/expense totals, top spending category, budget status, "
        "the spending forecast, or how to use this app (adding "
        "transactions, setting budgets, categories). Try asking one of those."
    )
