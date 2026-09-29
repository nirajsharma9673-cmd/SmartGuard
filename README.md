# SmartGuard

SmartGuard is an explainable AI-based browser extension for detecting **HAM, SPAM, and PHISHING** emails. It combines a TF-IDF + Logistic Regression text classifier with a rule-based cybersecurity risk engine and presents the result through a browser extension and an admin dashboard.

## Features

- Gmail email text extraction through a browser extension
- Three-class email classification: HAM, SPAM, PHISHING
- TF-IDF + Logistic Regression machine-learning pipeline
- Explainable model evidence using important TF-IDF features
- Rule-based security checks for suspicious URLs, credentials, urgency, account threats, financial requests, and suspicious attachments
- Risk score from 0–100 with LOW, MEDIUM, HIGH, and CRITICAL levels
- Email reporting with SQLite storage
- Admin dashboard for report statistics and viewing reported email content
- Local Flask API for analysis and reporting

## System Architecture

```text
Gmail / Webmail
      |
      v
Browser Extension
      |
      v
Flask API
      |
      +----------------------+
      |                      |
      v                      v
TF-IDF + Logistic       Security Risk
Regression              Engine
      |                      |
      +----------+-----------+
                 |
                 v
          SmartGuard Result
      (class + risk + evidence)
                 |
                 v
            Report Email
                 |
                 v
              SQLite
                 |
                 v
          Admin Dashboard
```

## Machine Learning

The project uses a single machine-learning approach:

**TF-IDF + Logistic Regression**

TF-IDF converts email text into numerical features based on term importance. Logistic Regression then predicts one of three classes:

- HAM
- SPAM
- PHISHING

On the project's held-out test set of 1,106 samples, the trained model achieved **98.19% accuracy**.

This metric describes performance on the included test split and should not be interpreted as real-world or representative Indian-email accuracy.

## Dataset

The dataset combines:

- SpamAssassin email data
- Nazario phishing email data
- A small set of synthetic Indian-context examples for additional context such as UPI, KYC, PAN, Aadhaar, college fees, and similar scenarios

The synthetic examples are not intended to represent the distribution of real Indian email traffic.

## Project Structure

```text
SmartGuard/
├── admin/
│   └── index.html
├── backend/
│   ├── app.py
│   └── database.py
├── data/
│   ├── raw/
│   └── processed/
├── extension/
│   ├── manifest.json
│   ├── content.js
│   ├── popup.html
│   ├── popup.css
│   └── popup.js
├── models/
│   └── smartguard_tfidf_logistic_regression.joblib
├── src/
│   ├── train_model.py
│   ├── evaluate_model.py
│   ├── explain_prediction.py
│   ├── security_engine.py
│   ├── smartguard_analyzer.py
│   ├── prepare_dataset.py
│   ├── split_dataset.py
│   └── merge_indian_samples.py
├── tests/
├── requirements.txt
└── README.md
```

## Setup on Windows

### 1. Create and activate the virtual environment

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
```

If PowerShell blocks activation for the current session:

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
.venv\Scripts\Activate.ps1
```

### 2. Install dependencies

```powershell
pip install -r requirements.txt
```

## Run SmartGuard

### Start the backend

```powershell
python backend\app.py
```

The API runs at:

```text
http://127.0.0.1:5000
```

### Start the admin dashboard

Open another terminal:

```powershell
python -m http.server 8000 --directory admin
```

Open:

```text
http://127.0.0.1:8000
```

### Load the browser extension

In Chrome or Brave:

1. Open `chrome://extensions/` or `brave://extensions/`
2. Turn on **Developer mode**
3. Select **Load unpacked**
4. Choose the project's `extension` folder
5. Open Gmail and open an email
6. Click the SmartGuard extension icon
7. Use **Get Gmail email** and **Analyze email**

## Demo Flow

```text
Open Gmail email
      ↓
SmartGuard extracts email text
      ↓
Analyze email
      ↓
HAM / SPAM / PHISHING
      ↓
Risk score + AI evidence + security indicators
      ↓
Report email
      ↓
Admin dashboard
      ↓
View reported email
```

## Security Notes

- SmartGuard does not automatically open suspicious URLs.
- Raw reported email content is stored locally in SQLite during the demo.
- Do not commit personal email data or the local SQLite database to a public repository.
- Do not place API keys, passwords, private tokens, or other secrets in the repository.

## Limitations

- The current browser integration is focused on Gmail.
- The backend is designed for local PBL/demo use, not production deployment.
- The security engine is rule-based and can produce false positives or false negatives.
- The test accuracy is based on the project's held-out dataset and does not guarantee real-world performance.

## Future Work

Potential future improvements include stronger sender/header analysis, threat-intelligence integration, broader webmail support, multilingual detection, better attachment analysis, and privacy-preserving or on-device inference.

## License / Dataset Notice

Review the licenses and redistribution terms of all third-party datasets and libraries before publishing a public repository.
