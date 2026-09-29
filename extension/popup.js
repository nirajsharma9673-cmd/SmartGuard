const API_URL = "http://127.0.0.1:5000";

const emailText = document.getElementById("emailText");
const analyzeBtn = document.getElementById("analyzeBtn");
const getEmailBtn = document.getElementById("getEmailBtn");
const reportBtn = document.getElementById("reportBtn");

const status = document.getElementById("status");
const result = document.getElementById("result");

const prediction = document.getElementById("prediction");
const riskScore = document.getElementById("riskScore");
const riskLevel = document.getElementById("riskLevel");
const riskIndicator = document.getElementById("riskIndicator");

const mlFeatures = document.getElementById("mlFeatures");
const securityFindings = document.getElementById("securityFindings");
const probabilities = document.getElementById("probabilities");


function setStatus(message, type = "") {
    status.textContent = message;
    status.className = `status-message ${type}`;
}


async function getCurrentTab() {
    const tabs = await chrome.tabs.query({
        active: true,
        currentWindow: true
    });

    return tabs[0];
}


/* =========================================================
   GET EMAIL FROM GMAIL
   ========================================================= */

getEmailBtn.addEventListener("click", async () => {

    setStatus("Reading the current Gmail email...");

    try {

        const tab = await getCurrentTab();

        if (!tab || !tab.id) {
            setStatus("No active tab found.", "error");
            return;
        }

        if (
            !tab.url ||
            !tab.url.startsWith("https://mail.google.com/")
        ) {
            setStatus(
                "Open Gmail and open an email first.",
                "error"
            );
            return;
        }

        chrome.tabs.sendMessage(
            tab.id,
            { action: "GET_EMAIL" },
            (response) => {

                if (chrome.runtime.lastError) {

                    console.error(
                        chrome.runtime.lastError
                    );

                    setStatus(
                        "Reload the Gmail tab, then try again.",
                        "error"
                    );

                    return;
                }

                if (
                    !response ||
                    !response.success ||
                    !response.text
                ) {

                    setStatus(
                        "No email body was found.",
                        "error"
                    );

                    return;
                }

                emailText.value = response.text;

                setStatus(
                    "Gmail email loaded successfully.",
                    "success"
                );
            }
        );

    } catch (error) {

        console.error(error);

        setStatus(
            "Failed to read Gmail email.",
            "error"
        );
    }
});

async function loadGmailEmailAutomatically() {
    try {
        const tab = await getCurrentTab();

        if (!tab || !tab.id) {
            return;
        }

        if (
            !tab.url ||
            !tab.url.startsWith("https://mail.google.com/")
        ) {
            setStatus(
                "Open a Gmail email to load it automatically."
            );
            return;
        }

        chrome.tabs.sendMessage(
            tab.id,
            { action: "GET_EMAIL" },
            (response) => {

                if (chrome.runtime.lastError) {
                    console.error(chrome.runtime.lastError);

                    setStatus(
                        "Reload Gmail once, then open SmartGuard.",
                        "error"
                    );

                    return;
                }

                if (
                    response &&
                    response.success &&
                    response.text
                ) {
                    emailText.value = response.text;

                    setStatus(
                        "Gmail email loaded automatically.",
                        "success"
                    );
                } else {
                    setStatus(
                        "No open email found in Gmail."
                    );
                }
            }
        );

    } catch (error) {
        console.error(error);

        setStatus(
            "Could not read Gmail.",
            "error"
        );
    }
}

/* =========================================================
   ANALYZE
   ========================================================= */

analyzeBtn.addEventListener("click", async () => {

    const text = emailText.value.trim();

    if (!text) {

        setStatus(
            "Please load an email or paste email content.",
            "error"
        );

        return;
    }

    analyzeBtn.disabled = true;
    analyzeBtn.classList.add("loading");

    const originalText = analyzeBtn.textContent;
    analyzeBtn.textContent = "Analyzing";

    result.hidden = true;

    setStatus("Checking email security...");

    try {

        const response = await fetch(
            `${API_URL}/analyze`,
            {
                method: "POST",

                headers: {
                    "Content-Type": "application/json"
                },

                body: JSON.stringify({
                    text
                })
            }
        );

        const data = await response.json();

        if (!response.ok) {
            throw new Error(
                data.error || "Analysis failed."
            );
        }

        if (!data.result) {
            throw new Error(
                "Backend returned no analysis result."
            );
        }

        displayResult(data.result);

        setStatus(
            "Analysis completed.",
            "success"
        );

    } catch (error) {

        console.error(error);

        setStatus(
            "Could not connect to SmartGuard backend.",
            "error"
        );

    } finally {

        analyzeBtn.disabled = false;
        analyzeBtn.classList.remove("loading");
        analyzeBtn.textContent = originalText;
    }
});


/* =========================================================
   DISPLAY RESULT
   ========================================================= */

function displayResult(data) {

    result.hidden = false;

    prediction.textContent =
        data.prediction || "UNKNOWN";

    riskScore.textContent =
        data.risk_score ?? 0;

    riskLevel.textContent =
        data.risk_level || "UNKNOWN";


    riskIndicator.className =
        `risk-indicator ${
            String(data.risk_level || "").toLowerCase()
        }`;


    /* -------------------------
       ML FEATURES
    ------------------------- */

    mlFeatures.innerHTML = "";

    if (
        Array.isArray(data.ml_features) &&
        data.ml_features.length
    ) {

        data.ml_features
            .slice(0, 5)
            .forEach((item, index) => {

                const li =
                    document.createElement("li");

                li.textContent =
                    item.feature || "Unknown feature";

                li.style.animationDelay =
                    `${index * 70}ms`;

                mlFeatures.appendChild(li);
            });

    } else {

        const li =
            document.createElement("li");

        li.textContent =
            "No AI evidence available.";

        mlFeatures.appendChild(li);
    }


    /* -------------------------
       SECURITY FINDINGS
    ------------------------- */

    securityFindings.innerHTML = "";

    if (
        Array.isArray(data.security_findings) &&
        data.security_findings.length
    ) {

        data.security_findings
            .slice(0, 5)
            .forEach((finding, index) => {

                const li =
                    document.createElement("li");

                li.textContent = finding;

                li.style.animationDelay =
                    `${index * 70}ms`;

                securityFindings.appendChild(li);
            });

    } else {

        const li =
            document.createElement("li");

        li.textContent =
            "No major security indicators detected.";

        securityFindings.appendChild(li);
    }


    /* -------------------------
       PROBABILITIES
    ------------------------- */

    probabilities.innerHTML = "";

    const probs =
        data.probabilities || {};

    Object.entries(probs).forEach(
        ([label, value], index) => {

            const percentage =
                Number(value) * 100;

            const row =
                document.createElement("div");

            row.className =
                "probability-row";

            row.style.animationDelay =
                `${index * 80}ms`;

            row.innerHTML = `
                <div class="probability-label">
                    <span>${label}</span>
                    <span>${percentage.toFixed(1)}%</span>
                </div>

                <div class="probability-bar">
                    <div
                        class="probability-fill"
                        style="width: ${percentage}%"
                    ></div>
                </div>
            `;

            probabilities.appendChild(row);
        }
    );
}


/* =========================================================
   REPORT
   ========================================================= */

reportBtn.addEventListener("click", async () => {

    const text = emailText.value.trim();

    if (!text) {
        setStatus(
            "No email is available to report.",
            "error"
        );
        return;
    }

    reportBtn.disabled = true;

    setStatus("Submitting report...");

    try {

        const response = await fetch(
            `${API_URL}/reports`,
            {
                method: "POST",

                headers: {
                    "Content-Type": "application/json"
                },

                body: JSON.stringify({
                    text: text,
                    prediction: prediction.textContent,
                    risk_score: Number(riskScore.textContent),
                    risk_level: riskLevel.textContent
                })
            }
        );

        const data = await response.json();

        if (!response.ok) {
            throw new Error(
                data.error || "Report failed."
            );
        }

        setStatus(
            `Report submitted. ID: ${data.report.id}`,
            "success"
        );

        reportBtn.textContent =
            "Report submitted";

    } catch (error) {

        console.error(error);

        setStatus(
            "Could not submit the report.",
            "error"
        );

    } finally {

        reportBtn.disabled = false;
    }
});

loadGmailEmailAutomatically();