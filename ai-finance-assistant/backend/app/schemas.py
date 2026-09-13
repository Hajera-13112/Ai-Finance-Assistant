import datetime as dt
from typing import Optional, List, Literal

from pydantic import BaseModel, EmailStr, Field, ConfigDict


# ---------- Auth ----------

class UserRegister(BaseModel):
    name: str = Field(min_length=1, max_length=120)
    email: EmailStr
    password: str = Field(min_length=6, max_length=128)


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class UserOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    user_id: int
    name: str
    email: EmailStr
    created_at: dt.datetime


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserOut


# ---------- Transactions ----------

class TransactionCreate(BaseModel):
    date: dt.date
    description: str = Field(min_length=1, max_length=255)
    amount: float = Field(gt=0)
    type: Literal["income", "expense"]
    category: Optional[str] = None  # if omitted for an expense, ML will predict it


class TransactionUpdate(BaseModel):
    date: Optional[dt.date] = None
    description: Optional[str] = Field(default=None, min_length=1, max_length=255)
    amount: Optional[float] = Field(default=None, gt=0)
    type: Optional[Literal["income", "expense"]] = None
    category: Optional[str] = None


class TransactionOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    transaction_id: int
    date: dt.date
    description: str
    amount: float
    type: str
    category: Optional[str]
    predicted_category: Optional[str] = None
    confidence: Optional[float] = None


# ---------- Budgets ----------

class BudgetCreate(BaseModel):
    month: str = Field(pattern=r"^\d{4}-\d{2}$", description="Format YYYY-MM")
    category: Optional[str] = None
    limit_amount: float = Field(gt=0)


class BudgetOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    budget_id: int
    month: str
    category: Optional[str]
    limit_amount: float
    spent: float = 0.0
    remaining: float = 0.0
    percent_used: float = 0.0
    status: str = "ok"  # ok | warning | exceeded


# ---------- Prediction ----------

class CategoryPredictRequest(BaseModel):
    description: str = Field(min_length=1, max_length=255)
    amount: Optional[float] = None
    type: Optional[Literal["income", "expense"]] = "expense"


class CategoryPredictResponse(BaseModel):
    predicted_category: str
    confidence: float
    probabilities: dict


# ---------- Dashboard ----------

class CategoryBreakdown(BaseModel):
    category: str
    total: float


class MonthlyTrendPoint(BaseModel):
    month: str
    income: float
    expense: float


class DashboardSummary(BaseModel):
    total_income: float
    total_expense: float
    balance: float
    category_breakdown: List[CategoryBreakdown]
    monthly_trend: List[MonthlyTrendPoint]
    forecast_next_month: Optional[float] = None
    forecast_note: Optional[str] = None


# ---------- Insights ----------

class InsightOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    insight_id: int
    insight_text: str
    created_at: dt.datetime


class InsightsResponse(BaseModel):
    insights: List[str]
    disclaimer: str = (
        "These insights are generated for educational purposes and are not "
        "professional financial advice."
    )
