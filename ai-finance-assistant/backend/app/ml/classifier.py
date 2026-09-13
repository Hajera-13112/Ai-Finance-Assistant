"""
Expense category classifier.

Input features: transaction description (text), amount, transaction type.
Target: expense category (Food, Transport, Shopping, Bills, Entertainment,
Health, Education, Other).

Approach (per SRS 11.1): TF-IDF over the cleaned description text, fed into
a Logistic Regression classifier. This is intentionally a simple, explainable
"beginner-friendly" pipeline as called out in the SRS non-functional
requirement on explainability.
"""
import os
import re
import joblib
import numpy as np
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, precision_recall_fscore_support, confusion_matrix

from app.config import CLASSIFIER_PATH, VECTORIZER_PATH, MODEL_DIR


def clean_text(text: str) -> str:
    text = text.lower()
    text = re.sub(r"[^a-z0-9\s]", " ", text)
    text = re.sub(r"\s+", " ", text).strip()
    return text


class ExpenseClassifier:
    """Wraps a fitted TF-IDF vectorizer + Logistic Regression model."""

    def __init__(self):
        self.vectorizer: TfidfVectorizer | None = None
        self.model: LogisticRegression | None = None

    def is_ready(self) -> bool:
        return self.vectorizer is not None and self.model is not None

    def load(self):
        if os.path.exists(VECTORIZER_PATH) and os.path.exists(CLASSIFIER_PATH):
            self.vectorizer = joblib.load(VECTORIZER_PATH)
            self.model = joblib.load(CLASSIFIER_PATH)
        return self

    def save(self):
        os.makedirs(MODEL_DIR, exist_ok=True)
        joblib.dump(self.vectorizer, VECTORIZER_PATH)
        joblib.dump(self.model, CLASSIFIER_PATH)

    def train(self, csv_path: str, test_size: float = 0.2, random_state: int = 42) -> dict:
        df = pd.read_csv(csv_path)
        df = df.dropna(subset=["description", "category"]).drop_duplicates()
        df["clean_description"] = df["description"].astype(str).map(clean_text)

        X_text = df["clean_description"]
        y = df["category"]

        X_train, X_test, y_train, y_test = train_test_split(
            X_text, y, test_size=test_size, random_state=random_state, stratify=y
        )

        self.vectorizer = TfidfVectorizer(ngram_range=(1, 2), min_df=1)
        X_train_vec = self.vectorizer.fit_transform(X_train)
        X_test_vec = self.vectorizer.transform(X_test)

        self.model = LogisticRegression(max_iter=1000, class_weight="balanced")
        self.model.fit(X_train_vec, y_train)

        y_pred = self.model.predict(X_test_vec)
        accuracy = accuracy_score(y_test, y_pred)
        precision, recall, f1, _ = precision_recall_fscore_support(
            y_test, y_pred, average="weighted", zero_division=0
        )
        cm = confusion_matrix(y_test, y_pred, labels=self.model.classes_).tolist()

        self.save()

        return {
            "accuracy": round(float(accuracy), 4),
            "precision": round(float(precision), 4),
            "recall": round(float(recall), 4),
            "f1_score": round(float(f1), 4),
            "labels": list(self.model.classes_),
            "confusion_matrix": cm,
            "train_size": len(X_train),
            "test_size": len(X_test),
        }

    def predict(self, description: str) -> tuple[str, float, dict]:
        if not self.is_ready():
            raise RuntimeError("Classifier is not trained/loaded yet.")

        cleaned = clean_text(description)
        vec = self.vectorizer.transform([cleaned])
        proba = self.model.predict_proba(vec)[0]
        classes = self.model.classes_

        best_idx = int(np.argmax(proba))
        predicted_category = classes[best_idx]
        confidence = float(proba[best_idx])
        probabilities = {cls: round(float(p), 4) for cls, p in zip(classes, proba)}

        return predicted_category, confidence, probabilities


# Module-level singleton, loaded once at app startup.
expense_classifier = ExpenseClassifier()
