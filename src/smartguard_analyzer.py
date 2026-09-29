from pathlib import Path

import joblib
import numpy as np

from src.security_engine import analyze_email as analyze_security


MODEL_FILE = Path(
    "models/smartguard_tfidf_logistic_regression.joblib"
)


def get_ml_explanation(model, email_text, prediction):
    """Get the most important TF-IDF features."""

    vectorizer = model.named_steps["tfidf"]
    classifier = model.named_steps["classifier"]

    tfidf_vector = vectorizer.transform([email_text])

    feature_names = vectorizer.get_feature_names_out()

    class_index = list(
        classifier.classes_
    ).index(prediction)

    coefficients = classifier.coef_[class_index]

    contributions = (
        tfidf_vector.toarray()[0] * coefficients
    )

    feature_indices = np.where(
        tfidf_vector.toarray()[0] > 0
    )[0]

    features = []

    for index in feature_indices:
        features.append(
            (
                feature_names[index],
                contributions[index]
            )
        )

    features.sort(
        key=lambda item: item[1],
        reverse=True
    )

    return features[:10]


def analyze_email(email_text):
    """Perform complete SmartGuard analysis."""

    model = joblib.load(MODEL_FILE)

    # -------------------------
    # ML ANALYSIS
    # -------------------------

    prediction = model.predict(
        [email_text]
    )[0]

    probabilities = model.predict_proba(
        [email_text]
    )[0]

    classes = model.classes_

    probability_dict = {
        label: float(probability)
        for label, probability in zip(
            classes,
            probabilities
        )
    }

    ml_features = get_ml_explanation(
        model,
        email_text,
        prediction
    )

    # -------------------------
    # SECURITY ANALYSIS
    # -------------------------

    security_result = analyze_security(
    email_text
)

    # -------------------------
    # FINAL RESULT
    # -------------------------

    return {
        "prediction": prediction,
        "probabilities": probability_dict,
        "ml_features": ml_features,
        "risk_score": security_result["risk_score"],
        "risk_level": security_result["risk_level"],
        "security_findings": security_result["findings"],
        "urls_found": security_result["urls_found"],
    }


def main():

    print("=" * 65)
    print("SMARTGUARD EMAIL SECURITY ANALYZER")
    print("=" * 65)

    email = input(
        "\nEnter email text:\n"
    )

    result = analyze_email(email)

    print("\n" + "=" * 65)
    print("ML CLASSIFICATION")
    print("=" * 65)

    print(
        f"\nPrediction: {result['prediction']}"
    )

    print("\nProbabilities:")

    for label, probability in sorted(
        result["probabilities"].items(),
        key=lambda item: item[1],
        reverse=True
    ):
        print(
            f"  {label:<10}: "
            f"{probability * 100:.2f}%"
        )

    print("\nImportant ML Features:")

    for feature, contribution in result["ml_features"]:
        print(
            f"  {feature:<25} "
            f"{contribution:.4f}"
        )

    print("\n" + "=" * 65)
    print("CYBERSECURITY ANALYSIS")
    print("=" * 65)

    print(
        f"\nRisk Score: "
        f"{result['risk_score']}/100"
    )

    print(
        f"Risk Level: "
        f"{result['risk_level']}"
    )

    print("\nSecurity Findings:")

    if result["security_findings"]:

        for finding in result["security_findings"]:
            print(f"  - {finding}")

    else:

        print(
            "  No major security indicators detected."
        )

    print("\nURLs Detected:")

    if result["urls_found"]:

        for url in result["urls_found"]:
            print(f"  - {url}")

    else:

        print("  No URLs detected.")

    print("\n" + "=" * 65)
    print("SMARTGUARD ANALYSIS COMPLETE")
    print("=" * 65)


if __name__ == "__main__":
    main()