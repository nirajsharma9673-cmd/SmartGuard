import re
from urllib.parse import urlparse


# Risk points for different security indicators
RISK_POINTS = {
    "suspicious_url": 25,
    "ip_url": 20,
    "long_url": 10,
    "credential_request": 20,
    "financial_request": 15,
    "urgency_language": 10,
    "account_threat": 15,
    "suspicious_attachment": 15,
}


def extract_urls(text):
    """Extract URLs from email text."""
    pattern = r"https?://[^\s]+|www\.[^\s]+"
    return re.findall(pattern, text, re.IGNORECASE)


def check_suspicious_urls(urls):
    """Check URLs for suspicious characteristics."""
    findings = []
    score = 0

    for url in urls:
        clean_url = url.rstrip(".,!?;:)")

        try:
            parsed = urlparse(
                clean_url if clean_url.startswith("http") else "http://" + clean_url
            )

            domain = parsed.netloc.lower()

            # Check for IP address instead of domain name
            if re.match(
                r"^\d{1,3}(\.\d{1,3}){3}$",
                domain
            ):
                findings.append(
                    f"URL uses an IP address: {clean_url}"
                )
                score += RISK_POINTS["ip_url"]

            # Check for very long URL
            if len(clean_url) > 100:
                findings.append(
                    f"Unusually long URL detected: {clean_url[:80]}..."
                )
                score += RISK_POINTS["long_url"]

            # Suspicious URL patterns
            suspicious_patterns = [
                "login",
                "verify",
                "account",
                "secure",
                "update",
                "password",
                "confirm",
                "signin",
            ]

            if any(
                pattern in clean_url.lower()
                for pattern in suspicious_patterns
            ):
                findings.append(
                    f"URL contains a sensitive-action keyword: {clean_url}"
                )
                score += RISK_POINTS["suspicious_url"]

        except Exception:
            findings.append(
                f"Could not safely parse URL: {clean_url}"
            )

    return score, findings


def check_credential_request(text):
    """Check whether the email requests sensitive credentials."""
    patterns = [
        r"\botp\b",
        r"\bpassword\b",
        r"\bpin\b",
        r"\bcvv\b",
        r"\bcard number\b",
        r"\bcredit card\b",
        r"\bdebit card\b",
        r"\blogin details\b",
        r"\bcredentials\b",
    ]

    if any(re.search(pattern, text, re.IGNORECASE) for pattern in patterns):
        return RISK_POINTS["credential_request"], [
            "Email requests sensitive credentials or authentication information."
        ]

    return 0, []


def check_financial_request(text):
    """Check for financial/payment-related requests."""
    patterns = [
        r"\bupi\b",
        r"\bbank transfer\b",
        r"\bpayment\b",
        r"\bpay\b",
        r"\bprocessing fee\b",
        r"\brefund\b",
        r"\btransaction\b",
        r"\bcredit card\b",
        r"\bdebit card\b",
    ]

    matches = [
        pattern
        for pattern in patterns
        if re.search(pattern, text, re.IGNORECASE)
    ]

    if matches:
        return RISK_POINTS["financial_request"], [
            "Email contains financial or payment-related language."
        ]

    return 0, []


def check_urgency(text):
    """Check for urgent or pressure-based language."""
    patterns = [
        r"\burgent\b",
        r"\bimmediately\b",
        r"\baction required\b",
        r"\bact now\b",
        r"\btoday\b",
        r"\bwithin 24 hours\b",
        r"\blast warning\b",
        r"\bexpires\b",
    ]

    matches = [
        pattern
        for pattern in patterns
        if re.search(pattern, text, re.IGNORECASE)
    ]

    if matches:
        return RISK_POINTS["urgency_language"], [
            "Email uses urgent or pressure-based language."
        ]

    return 0, []


def check_account_threat(text):
    """Check for account suspension/blocking threats."""
    patterns = [
        r"\baccount.*blocked\b",
        r"\baccount.*suspended\b",
        r"\baccount.*closed\b",
        r"\baccount.*deactivated\b",
        r"\bwill be blocked\b",
        r"\bwill be suspended\b",
    ]

    if any(re.search(pattern, text, re.IGNORECASE) for pattern in patterns):
        return RISK_POINTS["account_threat"], [
            "Email contains a possible account suspensionor blocking threat."
        ]

    return 0, []


def check_suspicious_attachment(text):
    """Check for potentially risky attachment types."""
    patterns = [
        r"\.exe\b",
        r"\.scr\b",
        r"\.bat\b",
        r"\.cmd\b",
        r"\.js\b",
        r"\.vbs\b",
        r"\.msi\b",
    ]

    if any(re.search(pattern, text, re.IGNORECASE) for pattern in patterns):
        return RISK_POINTS["suspicious_attachment"], [
            "Email references a potentially risky executable attachment."
        ]

    return 0, []


def get_risk_level(score):
    """Convert numeric risk score to a risk level."""
    if score <= 30:
        return "LOW"

    if score <= 60:
        return "MEDIUM"

    if score <= 80:
        return "HIGH"

    return "CRITICAL"


def analyze_email(text):
    """Run all cybersecurity checks on an email."""

    total_score = 0
    findings = []

    # URL analysis
    urls = extract_urls(text)

    url_score, url_findings = check_suspicious_urls(urls)
    total_score += url_score
    findings.extend(url_findings)

    # Credential analysis
    score, result = check_credential_request(text)
    total_score += score
    findings.extend(result)

    # Financial analysis
    score, result = check_financial_request(text)
    total_score += score
    findings.extend(result)

    # Urgency analysis
    score, result = check_urgency(text)
    total_score += score
    findings.extend(result)

    # Account threat analysis
    score, result = check_account_threat(text)
    total_score += score
    findings.extend(result)

    # Attachment analysis
    score, result = check_suspicious_attachment(text)
    total_score += score
    findings.extend(result)

    # Keep score within 0–100
    total_score = min(total_score, 100)

    return {
        "risk_score": total_score,
        "risk_level": get_risk_level(total_score),
        "urls_found": urls,
        "findings": findings,
    }


def main():
    print("=" * 60)
    print("SMARTGUARD CYBERSECURITY RISK ENGINE")
    print("=" * 60)

    email = input("\nEnter email text:\n")

    result = analyze_email(email)

    print("\nRisk Score:")
    print(f"  {result['risk_score']}/100")

    print("\nRisk Level:")
    print(f"  {result['risk_level']}")

    print("\nURLs Found:")
    for url in result["urls_found"]:
        print(f"  - {url}")

    print("\nSecurity Findings:")

    if result["findings"]:
        for finding in result["findings"]:
            print(f"  - {finding}")
    else:
        print("  No major security indicators detected.")


if __name__ == "__main__":
    main()