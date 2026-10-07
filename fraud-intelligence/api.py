from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from pathlib import Path
import json

# --------------------------------------------------
# PROJECT PATH
# --------------------------------------------------

BASE_DIR = Path(__file__).resolve().parent

DASHBOARD_DIR = BASE_DIR / "dashboard"
RESULTS_DIR = BASE_DIR / "results"
ANALYSIS_FILE = RESULTS_DIR / "analysis.json"


# --------------------------------------------------
# FASTAPI
# --------------------------------------------------

app = FastAPI(
    title="Real-Time Financial Fraud Intelligence API",
    description="Fraud detection and fraud-ring analysis API",
    version="1.0"
)


# --------------------------------------------------
# CORS
# --------------------------------------------------

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


# --------------------------------------------------
# LOAD ANALYSIS
# --------------------------------------------------

def load_analysis():

    if not ANALYSIS_FILE.exists():
        raise FileNotFoundError(
            "analysis.json not found. Run fraud_engine.py first."
        )

    with open(ANALYSIS_FILE, "r", encoding="utf-8") as file:
        return json.load(file)


# --------------------------------------------------
# HOME
# --------------------------------------------------

@app.get("/")
def home():

    return {
        "message": "Financial Fraud Intelligence API",
        "status": "running",
        "version": "1.0"
    }


# --------------------------------------------------
# HEALTH
# --------------------------------------------------

@app.get("/health")
def health():

    return {
        "status": "healthy"
    }


# --------------------------------------------------
# DASHBOARD
# --------------------------------------------------

@app.get("/dashboard/")
def dashboard():

    return FileResponse(
        DASHBOARD_DIR / "index.html"
    )


# --------------------------------------------------
# CSS
# --------------------------------------------------

@app.get("/dashboard/style.css")
def dashboard_css():

    return FileResponse(
        DASHBOARD_DIR / "style.css",
        media_type="text/css"
    )


# --------------------------------------------------
# JAVASCRIPT
# --------------------------------------------------

@app.get("/dashboard/script.js")
def dashboard_js():

    return FileResponse(
        DASHBOARD_DIR / "script.js",
        media_type="application/javascript"
    )


# --------------------------------------------------
# FRAUD NETWORK IMAGE
# --------------------------------------------------

@app.get("/results/fraud_ring_FR001.png")
def fraud_network_image():

    return FileResponse(
        RESULTS_DIR / "fraud_ring_FR001.png",
        media_type="image/png"
    )


# --------------------------------------------------
# ANALYSIS
# --------------------------------------------------

@app.get("/analysis")
def get_analysis():

    try:
        return load_analysis()

    except FileNotFoundError as error:

        raise HTTPException(
            status_code=404,
            detail=str(error)
        )


# --------------------------------------------------
# FRAUD RING
# --------------------------------------------------

@app.get("/fraud-ring")
def get_fraud_ring():

    try:

        data = load_analysis()

        return data["fraud_ring"]

    except FileNotFoundError as error:

        raise HTTPException(
            status_code=404,
            detail=str(error)
        )


# --------------------------------------------------
# ACCOUNTS
# --------------------------------------------------

@app.get("/accounts")
def get_accounts():

    try:

        data = load_analysis()

        return {
            "accounts": data["accounts"]
        }

    except FileNotFoundError as error:

        raise HTTPException(
            status_code=404,
            detail=str(error)
        )


# --------------------------------------------------
# TRANSACTIONS
# --------------------------------------------------

@app.get("/transactions")
def get_transactions():

    try:

        data = load_analysis()

        return {
            "transactions": data["transactions"]
        }

    except FileNotFoundError as error:

        raise HTTPException(
            status_code=404,
            detail=str(error)
        )


# --------------------------------------------------
# TRANSACTION INPUT
# --------------------------------------------------

class TransactionInput(BaseModel):

    transaction_id: str
    account_id: str
    amount: float
    device_id: str
    ip_address: str
    location: str
    merchant_id: str
    destination_account: str
    payment_channel: str


# --------------------------------------------------
# CHECK TRANSACTION
# --------------------------------------------------

@app.post("/check-transaction")
def check_transaction(
    transaction: TransactionInput
):

    try:

        data = load_analysis()

    except FileNotFoundError as error:

        raise HTTPException(
            status_code=404,
            detail=str(error)
        )

    existing_transactions = data["transactions"]

    fraud_ring = data["fraud_ring"]

    suspicious_accounts = set(
        fraud_ring.get("accounts", [])
    )

    score = 0

    reasons = []

    # ----------------------------------------------
    # SUSPICIOUS ACCOUNT
    # ----------------------------------------------

    if transaction.account_id in suspicious_accounts:

        score += 30

        reasons.append(
            "Account is already associated with a suspicious fraud ring"
        )

    # ----------------------------------------------
    # SHARED DEVICE
    # ----------------------------------------------

    matching_device_accounts = []

    for tx in existing_transactions:

        if (
            tx["device_id"] == transaction.device_id
            and tx["account_id"] != transaction.account_id
        ):

            matching_device_accounts.append(
                tx["account_id"]
            )

    if matching_device_accounts:

        score += 25

        reasons.append(
            "Device is shared with other accounts: "
            + ", ".join(
                sorted(
                    set(matching_device_accounts)
                )
            )
        )

    # ----------------------------------------------
    # SHARED IP
    # ----------------------------------------------

    matching_ip_accounts = []

    for tx in existing_transactions:

        if (
            tx["ip_address"] == transaction.ip_address
            and tx["account_id"] != transaction.account_id
        ):

            matching_ip_accounts.append(
                tx["account_id"]
            )

    if matching_ip_accounts:

        score += 20

        reasons.append(
            "IP address is shared with other accounts: "
            + ", ".join(
                sorted(
                    set(matching_ip_accounts)
                )
            )
        )

    # ----------------------------------------------
    # SHARED MERCHANT
    # ----------------------------------------------

    matching_merchant_accounts = []

    for tx in existing_transactions:

        if (
            tx["merchant_id"] == transaction.merchant_id
            and tx["account_id"] != transaction.account_id
        ):

            matching_merchant_accounts.append(
                tx["account_id"]
            )

    if matching_merchant_accounts:

        score += 15

        reasons.append(
            "Merchant is associated with other accounts"
        )

    # ----------------------------------------------
    # SHARED DESTINATION
    # ----------------------------------------------

    matching_destination_accounts = []

    for tx in existing_transactions:

        if (
            tx["destination_account"]
            == transaction.destination_account
            and tx["account_id"] != transaction.account_id
        ):

            matching_destination_accounts.append(
                tx["account_id"]
            )

    if matching_destination_accounts:

        score += 15

        reasons.append(
            "Destination account is shared with other accounts"
        )

    # ----------------------------------------------
    # HIGH AMOUNT
    # ----------------------------------------------

    if transaction.amount >= 5000:

        score += 5

        reasons.append(
            "Transaction amount is relatively high"
        )

    # ----------------------------------------------
    # LIMIT SCORE
    # ----------------------------------------------

    score = min(score, 100)

    # ----------------------------------------------
    # RISK LEVEL
    # ----------------------------------------------

    if score >= 80:

        risk_level = "CRITICAL"
        decision = "BLOCK"

    elif score >= 60:

        risk_level = "HIGH"
        decision = "REVIEW"

    elif score >= 30:

        risk_level = "MEDIUM"
        decision = "REVIEW"

    else:

        risk_level = "LOW"
        decision = "ALLOW"

    # ----------------------------------------------
    # NO REASONS
    # ----------------------------------------------

    if not reasons:

        reasons.append(
            "No suspicious relationship detected"
        )

    # ----------------------------------------------
    # RESULT
    # ----------------------------------------------

    return {

        "transaction_id": transaction.transaction_id,

        "account_id": transaction.account_id,

        "risk_score": score,

        "risk_level": risk_level,

        "decision": decision,

        "fraud_ring": (
            "FR001"
            if score >= 60
            else None
        ),

        "reasons": reasons
    }