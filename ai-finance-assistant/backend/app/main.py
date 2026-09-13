from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.storage import init_db
from app.ml.classifier import expense_classifier
from app.routers import auth, transactions, budgets, predict, dashboard, insights, chatbot

app = FastAPI(
    title="AI Finance Assistant API",
    description=(
        "Backend for a beginner-friendly personal finance app with AI-based "
        "expense categorization, budgeting, dashboards, spending forecasts, "
        "and rule-based financial insights. Data is stored in a local JSON "
        "file -- no database server required. Educational project -- not "
        "professional financial advice."
    ),
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # relax for the bundled static frontend; tighten in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
def on_startup():
    init_db()
    expense_classifier.load()


@app.get("/health", tags=["System"])
def health_check():
    return {
        "status": "ok",
        "ml_model_loaded": expense_classifier.is_ready(),
    }


app.include_router(auth.router)
app.include_router(transactions.router)
app.include_router(budgets.router)
app.include_router(predict.router)
app.include_router(dashboard.router)
app.include_router(insights.router)
app.include_router(chatbot.router)
