from pathlib import Path
import sys

from flask import Flask, request, jsonify
from flask_cors import CORS


# =========================================================
# PROJECT PATH
# =========================================================

PROJECT_ROOT = Path(__file__).resolve().parent.parent

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(
        0,
        str(PROJECT_ROOT)
    )


# =========================================================
# SMARTGUARD IMPORTS
# =========================================================

from src.smartguard_analyzer import analyze_email

from database import (
    initialize_database,
    create_report,
    get_reports,
    get_report
)


# =========================================================
# FLASK APP
# =========================================================

app = Flask(__name__)

# Development CORS
CORS(app)

# Initialize SQLite database
initialize_database()


# =========================================================
# HEALTH CHECK
# =========================================================

@app.route(
    "/health",
    methods=["GET"]
)
def health():

    return jsonify({
        "status": "ok",
        "service": "SmartGuard API"
    })


# =========================================================
# ANALYZE EMAIL
# =========================================================

@app.route(
    "/analyze",
    methods=["POST"]
)
def analyze():

    data = request.get_json(
        silent=True
    )

    if not data:

        return jsonify({
            "error": "Request body must be JSON."
        }), 400


    email_text = data.get(
        "text"
    )


    if not email_text:

        return jsonify({
            "error": "Email text is required."
        }), 400


    if not isinstance(
        email_text,
        str
    ):

        return jsonify({
            "error": "Email text must be a string."
        }), 400


    # Request size protection
    if len(email_text) > 100000:

        return jsonify({
            "error": "Email text is too large."
        }), 413


    try:

        result = analyze_email(
            email_text
        )


        return jsonify({

            "success": True,

            "result": {

                "prediction":
                    result["prediction"],

                "probabilities":
                    result["probabilities"],

                "ml_features": [
                    {
                        "feature": feature,
                        "contribution": float(
                            contribution
                        )
                    }

                    for feature, contribution
                    in result["ml_features"]
                ],

                "risk_score":
                    result["risk_score"],

                "risk_level":
                    result["risk_level"],

                "security_findings":
                    result["security_findings"],

                "urls_found":
                    result["urls_found"]

            }

        })


    except Exception as error:

        return jsonify({

            "error":
                "Analysis failed.",

            "details":
                str(error)

        }), 500


# =========================================================
# CREATE REPORT
# =========================================================

@app.route(
    "/reports",
    methods=["POST"]
)
def report_email():

    data = request.get_json(
        silent=True
    )


    if not data:

        return jsonify({
            "error": "Request body must be JSON."
        }), 400


    email_text = data.get(
        "text"
    )

    prediction = data.get(
        "prediction"
    )

    risk_score = data.get(
        "risk_score"
    )

    risk_level = data.get(
        "risk_level"
    )


    # -----------------------------------------------------
    # VALIDATION
    # -----------------------------------------------------

    if (
        not isinstance(
            email_text,
            str
        )
        or not email_text.strip()
    ):

        return jsonify({
            "error": "Email text is required."
        }), 400


    if len(email_text) > 100000:

        return jsonify({
            "error": "Email text is too large."
        }), 413


    if not isinstance(
        prediction,
        str
    ):

        return jsonify({
            "error": "Prediction is required."
        }), 400


    if not isinstance(
        risk_score,
        int
    ):

        return jsonify({
            "error":
                "Risk score must be an integer."
        }), 400


    if not isinstance(
        risk_level,
        str
    ):

        return jsonify({
            "error":
                "Risk level is required."
        }), 400


    # -----------------------------------------------------
    # SAVE REPORT
    # -----------------------------------------------------

    try:

        report = create_report(

            email_text=email_text,

            prediction=prediction,

            risk_score=risk_score,

            risk_level=risk_level

        )


        return jsonify({

            "success": True,

            "message":
                "Email reported successfully.",

            "report":
                report

        }), 201


    except Exception as error:

        return jsonify({

            "error":
                "Could not create report.",

            "details":
                str(error)

        }), 500


# =========================================================
# GET ALL REPORTS
# =========================================================

@app.route(
    "/reports",
    methods=["GET"]
)
def reports():

    try:

        reports_data = get_reports()


        return jsonify({

            "success": True,

            "reports":
                reports_data

        })


    except Exception as error:

        return jsonify({

            "error":
                "Could not load reports.",

            "details":
                str(error)

        }), 500


# =========================================================
# GET SINGLE REPORT
# =========================================================

@app.route(
    "/reports/<report_id>",
    methods=["GET"]
)
def single_report(
    report_id
):

    try:

        report = get_report(
            report_id
        )


        if report is None:

            return jsonify({

                "error":
                    "Report not found."

            }), 404


        return jsonify({

            "success": True,

            "report":
                report

        })


    except Exception as error:

        return jsonify({

            "error":
                "Could not load report.",

            "details":
                str(error)

        }), 500


# =========================================================
# ADMIN DASHBOARD STATISTICS
# =========================================================

@app.route(
    "/admin/stats",
    methods=["GET"]
)
def admin_stats():

    try:

        reports_data = get_reports()


        total_reports = len(
            reports_data
        )


        phishing_reports = sum(
            1
            for report in reports_data
            if report["prediction"] == "PHISHING"
        )


        spam_reports = sum(
            1
            for report in reports_data
            if report["prediction"] == "SPAM"
        )


        ham_reports = sum(
            1
            for report in reports_data
            if report["prediction"] == "HAM"
        )


        pending_reports = sum(
            1
            for report in reports_data
            if report["status"] == "PENDING"
        )


        if total_reports > 0:

            average_risk = round(

                sum(
                    report["risk_score"]
                    for report in reports_data
                )
                / total_reports,

                1

            )

        else:

            average_risk = 0


        return jsonify({

            "success": True,

            "stats": {

                "total_reports":
                    total_reports,

                "phishing_reports":
                    phishing_reports,

                "spam_reports":
                    spam_reports,

                "ham_reports":
                    ham_reports,

                "pending_reports":
                    pending_reports,

                "average_risk_score":
                    average_risk

            },

            "recent_reports":
                reports_data[:10]

        })


    except Exception as error:

        return jsonify({

            "error":
                "Could not load admin statistics.",

            "details":
                str(error)

        }), 500


# =========================================================
# START SERVER
# =========================================================

if __name__ == "__main__":

    app.run(

        host="127.0.0.1",

        port=5000,

        debug=True

    )