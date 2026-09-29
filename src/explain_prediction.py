from pathlib import Path

import joblib
import numpy as np


MODEL_FILE = Path(
    "models/smartguard_tfidf_logistic_regression.joblib"
)


def explain_prediction(email_text: str):
    # Load trained pipeline
    model = joblib.load(MODEL_FILE)

    # Prediction
    prediction = model.predict([email_text])[0]

    # Probability
    probabilities = model.predict_proba([email_text])[0]
    classes = model.classes_

    probability_dict = {
        label: float(probability)
        for label, probability in zip(classes, probabilities)
    }

    # Get TF-IDF vectorizer and classifier
    vectorizer = model.named_steps["tfidf"]
    classifier = model.named_steps["classifier"]

    # Convert email into TF-IDF features
    tfidf_vector = vectorizer.transform([email_text])

    feature_names = vectorizer.get_feature_names_out()

    # Find the classifier coefficients for predicted class
    class_index = list(classifier.classes_).index(prediction)

    coefficients = classifier.coef_[class_index]

    # Calculate contribution of each feature
    contributions = tfidf_vector.toarray()[0] * coefficients

    # Get non-zero features
    feature_indices = np.where(tfidf_vector.toarray()[0] > 0)[0]

    feature_contributions = []

    for index in feature_indices:
        feature_contributions.append(
            (
                feature_names[index],
                contributions[index]
            )
        )

    # Sort by strongest positive contribution
    feature_contributions.sort(
        key=lambda item: item[1],
        reverse=True
    )

    top_features = feature_contributions[:10]

    return prediction, probability_dict, top_features


def main():
    print("=" * 60)
    print("SMARTGUARD EXPLAINABLE AI")
    print("=" * 60)

    email = input("\nEnter email text:\n")

    prediction, probabilities, features = explain_prediction(email)

    print("\nPrediction:")
    print(f"  {prediction}")

    print("\nClass probabilities:")

    for label, probability in sorted(
        probabilities.items(),
        key=lambda item: item[1],
        reverse=True
    ):
        print(
            f"  {label:<10}: {probability * 100:.2f}%"
        )

    print("\nTop contributing features:")

    for feature, contribution in features:
        print(
            f"  {feature:<25} {contribution:.4f}"
        )


if __name__ == "__main__":
    main()