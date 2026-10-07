const API_URL = "";

async function checkTransaction() {

    const button = document.getElementById("checkButton");

    button.disabled = true;
    button.innerText = "ANALYZING...";

    const transaction = {
        transaction_id: document.getElementById("transaction_id").value,
        account_id: document.getElementById("account_id").value,
        amount: Number(document.getElementById("amount").value),
        device_id: document.getElementById("device_id").value,
        ip_address: document.getElementById("ip_address").value,
        location: document.getElementById("location").value,
        merchant_id: document.getElementById("merchant_id").value,
        destination_account: document.getElementById("destination_account").value,
        payment_channel: document.getElementById("payment_channel").value
    };

    try {

        const response = await fetch(
            `${API_URL}/check-transaction`,
            {
                method: "POST",
                headers: {
                    "Content-Type": "application/json"
                },
                body: JSON.stringify(transaction)
            }
        );

        if (!response.ok) {
            throw new Error("API request failed");
        }

        const result = await response.json();

        displayResult(result);

    } catch (error) {

        alert(
            "Could not connect to the Fraud Detection API.\n\n" +
            "Make sure FastAPI is running."
        );

        console.error(error);

    } finally {

        button.disabled = false;
        button.innerText = "CHECK TRANSACTION";
    }
}


function displayResult(result) {

    const riskScore = document.getElementById("riskScore");
    const riskLevel = document.getElementById("riskLevel");
    const decision = document.getElementById("decision");
    const fraudRing = document.getElementById("fraudRing");
    const reasonsList = document.getElementById("reasonsList");

    riskScore.innerText = result.risk_score;

    riskLevel.innerText = result.risk_level;
    decision.innerText = result.decision;

    if (result.fraud_ring) {
        fraudRing.innerText = result.fraud_ring;
    } else {
        fraudRing.innerText = "None";
    }

    /* Remove old risk colors */

    riskLevel.className = "";
    decision.className = "";
    riskScore.className = "";

    /* Apply risk color */

    if (result.risk_level === "CRITICAL") {

        riskLevel.classList.add("risk-critical");
        riskScore.classList.add("risk-critical");

    } else if (result.risk_level === "HIGH") {

        riskLevel.classList.add("risk-high");
        riskScore.classList.add("risk-high");

    } else if (result.risk_level === "MEDIUM") {

        riskLevel.classList.add("risk-medium");
        riskScore.classList.add("risk-medium");

    } else {

        riskLevel.classList.add("risk-low");
        riskScore.classList.add("risk-low");
    }

    /* Display reasons */

    reasonsList.innerHTML = "";

    result.reasons.forEach(function(reason) {

        const li = document.createElement("li");

        li.innerText = reason;

        reasonsList.appendChild(li);
    });
}


async function loadFraudRing() {

    const container = document.getElementById("fraudRingInfo");

    try {

        const response = await fetch(
            `${API_URL}/fraud-ring`
        );

        if (!response.ok) {
            throw new Error("Could not load fraud ring");
        }

        const ring = await response.json();

        if (!ring.detected) {

            container.innerHTML = `
                <p>No fraud ring detected.</p>
            `;

            return;
        }

        let accountsHTML = "";

        ring.accounts.forEach(function(account) {

            accountsHTML += `
                <span class="account-tag">
                    ${account}
                </span>
            `;
        });

        container.innerHTML = `
            <p>
                <strong>Ring ID:</strong>
                ${ring.ring_id}
            </p>

            <p>
                <strong>Risk Score:</strong>
                ${ring.risk_score}
            </p>

            <p>
                <strong>Suspicious Accounts:</strong>
            </p>

            <div class="account-list">
                ${accountsHTML}
            </div>
        `;

    } catch (error) {

        container.innerHTML = `
            <p>
                Unable to load fraud-ring information.
                Make sure the API is running.
            </p>
        `;

        console.error(error);
    }
}


/* Load fraud-ring information when dashboard opens */

window.addEventListener("DOMContentLoaded", function() {

    loadFraudRing();

});