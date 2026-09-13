"""
Train the expense classification model and save it to models_store/.

Usage:
    python train_model.py [path_to_csv]

If no path is given, uses data/sample_transactions.csv. Prints evaluation
metrics (accuracy, precision, recall, F1, confusion matrix) per SRS 11.3.
"""
import sys
import json

from app.ml.classifier import ExpenseClassifier
from app.config import DATASET_PATH


def main():
    csv_path = sys.argv[1] if len(sys.argv) > 1 else DATASET_PATH
    print(f"Training expense classifier on: {csv_path}")

    classifier = ExpenseClassifier()
    metrics = classifier.train(csv_path)

    print("\n=== Evaluation Metrics ===")
    print(json.dumps(metrics, indent=2))
    print("\nModel and vectorizer saved to models_store/.")


if __name__ == "__main__":
    main()
