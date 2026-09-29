from pathlib import Path

import joblib
import pandas as pd

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline
from sklearn.metrics import classification_report, accuracy_score


DATA_DIR = Path("data/processed")
MODEL_DIR = Path("models")

TRAIN_FILE = DATA_DIR / "train.csv"
VALIDATION_FILE = DATA_DIR / "validation.csv"
MODEL_FILE = MODEL_DIR / "smartguard_tfidf_logistic_regression.joblib"


def main():
    print("Loading datasets...")

    train_df = pd.read_csv(TRAIN_FILE)
    validation_df = pd.read_csv(VALIDATION_FILE)

    X_train = train_df["text"]
    y_train = train_df["label"]

    X_validation = validation_df["text"]
    y_validation = validation_df["label"]

    print(f"Training samples: {len(X_train)}")
    print(f"Validation samples: {len(X_validation)}")

    print("\nBuilding TF-IDF + Logistic Regression pipeline...")

    model = Pipeline([
        (
            "tfidf",
            TfidfVectorizer(
                lowercase=True,
                stop_words="english",
                ngram_range=(1, 2),
                min_df=2,
                max_df=0.95,
                sublinear_tf=True
            )
        ),
        (
            "classifier",
            LogisticRegression(
                max_iter=1000,
                class_weight="balanced",
                random_state=42
            )
        )
    ])

    print("\nTraining model...")

    model.fit(X_train, y_train)

    print("Training completed.")

    print("\nEvaluating on validation dataset...")

    predictions = model.predict(X_validation)

    accuracy = accuracy_score(
        y_validation,
        predictions
    )

    print(f"\nValidation Accuracy: {accuracy:.4f}")

    print("\nClassification Report:")
    print(
        classification_report(
            y_validation,
            predictions,
            digits=4
        )
    )

    MODEL_DIR.mkdir(
        parents=True,
        exist_ok=True
    )

    joblib.dump(
        model,
        MODEL_FILE
    )

    print(f"\nModel saved to:")
    print(MODEL_FILE)


if __name__ == "__main__":
    main()