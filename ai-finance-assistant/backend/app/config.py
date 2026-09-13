import os
from dotenv import load_dotenv

load_dotenv()

JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY", "dev-secret-change-me")
JWT_ALGORITHM = os.getenv("JWT_ALGORITHM", "HS256")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "120"))

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

MODEL_DIR = os.path.join(BASE_DIR, "models_store")
CLASSIFIER_PATH = os.path.join(MODEL_DIR, "expense_classifier.joblib")
VECTORIZER_PATH = os.path.join(MODEL_DIR, "tfidf_vectorizer.joblib")
DATASET_PATH = os.path.join(BASE_DIR, "data", "sample_transactions.csv")

# All application data (users, transactions, budgets, predictions, insights)
# is persisted to this single JSON file. No database server required.
DATA_DIR = os.path.join(BASE_DIR, "data_store")
DATA_FILE = os.path.join(DATA_DIR, "db.json")

CATEGORIES = [
    "Food",
    "Transport",
    "Shopping",
    "Bills",
    "Entertainment",
    "Health",
    "Education",
    "Other",
]
