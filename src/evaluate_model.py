from pathlib import Path

import joblib
import pandas as pd

from sklearn.metrics import (
    accuracy_score,
    classification_report,
    confusion_matrix
)


MODEL_FILE = Path(
    "models/smartguard_tfidf_logistic_regression.joblib"
)

TEST_FILE = Path(
    "data/processed/test.csv"
)


def main():
    print("Loading trained model...")

    model = joblib.load(MODEL_FILE)

    print("Loading test dataset...")

    test_df = pd.read_csv(TEST_FILE)

    X_test = test_df["text"]
    y_test = test_df["label"]

    print(f"Test samples: {len(test_df)}")

    print("\nMaking predictions...")

    predictions = model.predict(X_test)

    accuracy = accuracy_score(
        y_test,
        predictions
    )

    print("\n" + "=" * 50)
    print("FINAL TEST RESULTS")
    print("=" * 50)

    print(f"\nTest Accuracy: {accuracy:.4f}")
    print(f"Test Accuracy: {accuracy * 100:.2f}%")

    print("\nClassification Report:")

    print(
        classification_report(
            y_test,
            predictions,
            digits=4
        )
    )

    print("\nConfusion Matrix:")

    labels = ["HAM", "SPAM", "PHISHING"]

    matrix = confusion_matrix(
        y_test,
        predictions,
        labels=labels
    )

    print("             " + "  ".join(f"{label:>10}" for label in labels))

    for label, row in zip(labels, matrix):
        print(
            f"{label:>10}  "
            + "  ".join(f"{value:>10}" for value in row)
        )


if __name__ == "__main__":
    main()