import pandas as pd
import networkx as nx

# ==========================================
# 1. LOAD TRANSACTION DATA
# ==========================================

df = pd.read_csv("data/transactions.csv")

print("=" * 60)
print("       FRAUD NETWORK ANALYSIS")
print("=" * 60)


# ==========================================
# 2. CREATE NETWORK
# ==========================================

G = nx.Graph()


# ==========================================
# 3. ADD ACCOUNTS AND CONNECTIONS
# ==========================================

for _, row in df.iterrows():

    account = row["account_id"]
    device = row["device_id"]
    ip = row["ip_address"]
    merchant = row["merchant_id"]
    location = row["location"]
    destination = row["destination_account"]

    # Add nodes
    G.add_node(account, type="account")
    G.add_node(device, type="device")
    G.add_node(ip, type="ip")
    G.add_node(merchant, type="merchant")
    G.add_node(location, type="location")
    G.add_node(destination, type="account")

    # Add relationships
    G.add_edge(
        account,
        device,
        relation="uses_device"
    )

    G.add_edge(
        account,
        ip,
        relation="uses_ip"
    )

    G.add_edge(
        account,
        merchant,
        relation="uses_merchant"
    )

    G.add_edge(
        account,
        location,
        relation="located_at"
    )

    G.add_edge(
        account,
        destination,
        relation="transfers_to"
    )


# ==========================================
# 4. DISPLAY NETWORK INFORMATION
# ==========================================

print("\nNETWORK INFORMATION")
print("-" * 60)

print("Total nodes:", G.number_of_nodes())
print("Total connections:", G.number_of_edges())


# ==========================================
# 5. DISPLAY CONNECTIONS
# ==========================================

print("\nACCOUNT CONNECTIONS")
print("-" * 60)

for source, target, data in G.edges(data=True):

    if data["relation"] == "uses_device":

        print(
            f"{source} --> Device {target}"
        )

    elif data["relation"] == "uses_ip":

        print(
            f"{source} --> IP {target}"
        )

    elif data["relation"] == "uses_merchant":

        print(
            f"{source} --> Merchant {target}"
        )

    elif data["relation"] == "located_at":

        print(
            f"{source} --> Location {target}"
        )

    elif data["relation"] == "transfers_to":

        print(
            f"{source} --> Destination {target}"
        )


# ==========================================
# 6. FIND SHARED DEVICES
# ==========================================

print("\nSHARED DEVICES")
print("-" * 60)

device_groups = df.groupby("device_id")["account_id"].unique()

for device, accounts in device_groups.items():

    if len(accounts) > 1:

        print(
            f"Device {device} is shared by: "
            f"{', '.join(accounts)}"
        )


# ==========================================
# 7. FIND SHARED IP ADDRESSES
# ==========================================

print("\nSHARED IP ADDRESSES")
print("-" * 60)

ip_groups = df.groupby("ip_address")["account_id"].unique()

for ip, accounts in ip_groups.items():

    if len(accounts) > 1:

        print(
            f"IP {ip} is shared by: "
            f"{', '.join(accounts)}"
        )


# ==========================================
# 8. FIND COMMON DESTINATIONS
# ==========================================

print("\nCOMMON DESTINATIONS")
print("-" * 60)

destination_groups = (
    df.groupby("destination_account")["account_id"]
    .unique()
)

for destination, accounts in destination_groups.items():

    if len(accounts) > 1:

        print(
            f"Destination {destination} receives "
            f"transactions from: "
            f"{', '.join(accounts)}"
        )


print("\n" + "=" * 60)
print("Network analysis completed.")
print("=" * 60)
# ==========================================
# 9. FRAUD RING RISK SCORING
# ==========================================

print("\n" + "=" * 60)
print("             FRAUD RING RISK SCORING")
print("=" * 60)


# Risk score for each account
risk_scores = {}

# Reasons for each account
risk_reasons = {}


# Initialize all accounts
for account in df["account_id"].unique():

    risk_scores[account] = 0
    risk_reasons[account] = []


# ==========================================
# RULE 1 - SHARED DEVICE
# ==========================================

device_groups = df.groupby("device_id")["account_id"].unique()

for device, accounts in device_groups.items():

    if len(accounts) > 1:

        for account in accounts:

            risk_scores[account] += 25

            risk_reasons[account].append(
                f"Shares device {device} with other accounts"
            )


# ==========================================
# RULE 2 - SHARED IP
# ==========================================

ip_groups = df.groupby("ip_address")["account_id"].unique()

for ip, accounts in ip_groups.items():

    if len(accounts) > 1:

        for account in accounts:

            risk_scores[account] += 20

            risk_reasons[account].append(
                f"Shares IP address {ip} with other accounts"
            )


# ==========================================
# RULE 3 - SHARED MERCHANT
# ==========================================

merchant_groups = df.groupby(
    "merchant_id"
)["account_id"].unique()

for merchant, accounts in merchant_groups.items():

    if len(accounts) > 1:

        for account in accounts:

            risk_scores[account] += 15

            risk_reasons[account].append(
                f"Uses merchant {merchant} shared with other accounts"
            )


# ==========================================
# RULE 4 - SHARED LOCATION
# ==========================================

location_groups = df.groupby(
    "location"
)["account_id"].unique()

for location, accounts in location_groups.items():

    if len(accounts) > 1:

        for account in accounts:

            risk_scores[account] += 10

            risk_reasons[account].append(
                f"Shares location {location} with other accounts"
            )


# ==========================================
# RULE 5 - COMMON DESTINATION
# ==========================================

destination_groups = df.groupby(
    "destination_account"
)["account_id"].unique()

for destination, accounts in destination_groups.items():

    if len(accounts) > 1:

        for account in accounts:

            risk_scores[account] += 15

            risk_reasons[account].append(
                f"Transfers to common destination {destination}"
            )


# ==========================================
# LIMIT SCORE TO 100
# ==========================================

for account in risk_scores:

    risk_scores[account] = min(
        risk_scores[account],
        100
    )


# ==========================================
# RISK LEVEL
# ==========================================

def get_risk_level(score):

    if score >= 80:
        return "CRITICAL"

    elif score >= 60:
        return "HIGH"

    elif score >= 30:
        return "MEDIUM"

    else:
        return "LOW"


# ==========================================
# DISPLAY ACCOUNT RISK
# ==========================================

print("\nACCOUNT RISK SCORES")
print("-" * 60)

for account, score in risk_scores.items():

    level = get_risk_level(score)

    print(f"\nAccount: {account}")
    print(f"Risk Score: {score}/100")
    print(f"Risk Level: {level}")

    if risk_reasons[account]:

        print("Reasons:")

        for reason in risk_reasons[account]:

            print(f"  - {reason}")

    else:

        print("Reasons: No suspicious connections")


# ==========================================
# FIND FRAUD RING
# ==========================================

print("\n" + "=" * 60)
print("              FRAUD RING DETECTION")
print("=" * 60)


fraud_accounts = []

for account, score in risk_scores.items():

    if score >= 60:

        fraud_accounts.append(account)


if fraud_accounts:

    print("\n🚨 POSSIBLE FRAUD RING DETECTED")

    print("\nSuspicious accounts:")

    for account in fraud_accounts:

        print(
            f"  {account} "
            f"({risk_scores[account]}/100)"
        )

else:

    print("\nNo major fraud ring detected.")


print("\n" + "=" * 60)


# ==========================================
# 10. TRANSACTION-LEVEL RISK SCORING
# ==========================================

print("\n" + "=" * 60)
print("          TRANSACTION RISK ANALYSIS")
print("=" * 60)


# Convert timestamp into datetime
df["timestamp"] = pd.to_datetime(df["timestamp"])


transaction_scores = {}
transaction_reasons = {}


# Initialize
for transaction in df["transaction_id"]:

    transaction_scores[transaction] = 0
    transaction_reasons[transaction] = []


# ==========================================
# RULE 1 - LARGE TRANSACTION
# ==========================================

for index, row in df.iterrows():

    transaction = row["transaction_id"]
    amount = row["amount"]

    if amount >= 5000:

        transaction_scores[transaction] += 20

        transaction_reasons[transaction].append(
            f"Large transaction amount: ₹{amount}"
        )


# ==========================================
# RULE 2 - SHARED DEVICE
# ==========================================

device_counts = df["device_id"].value_counts()

for index, row in df.iterrows():

    transaction = row["transaction_id"]
    device = row["device_id"]

    if device_counts[device] > 1:

        transaction_scores[transaction] += 25

        transaction_reasons[transaction].append(
            f"Device {device} is shared by multiple accounts"
        )


# ==========================================
# RULE 3 - SHARED IP
# ==========================================

ip_counts = df["ip_address"].value_counts()

for index, row in df.iterrows():

    transaction = row["transaction_id"]
    ip = row["ip_address"]

    if ip_counts[ip] > 1:

        transaction_scores[transaction] += 20

        transaction_reasons[transaction].append(
            f"IP {ip} is shared by multiple accounts"
        )


# ==========================================
# RULE 4 - COMMON DESTINATION
# ==========================================

destination_counts = (
    df["destination_account"].value_counts()
)

for index, row in df.iterrows():

    transaction = row["transaction_id"]
    destination = row["destination_account"]

    if destination_counts[destination] > 1:

        transaction_scores[transaction] += 15

        transaction_reasons[transaction].append(
            f"Destination {destination} receives money from multiple accounts"
        )


# ==========================================
# RULE 5 - RAPID TRANSACTIONS
# ==========================================

# Sort transactions by time
df = df.sort_values("timestamp")


for i in range(len(df)):

    current_transaction = df.iloc[i]

    current_id = current_transaction["transaction_id"]
    current_time = current_transaction["timestamp"]

    # Compare with previous transactions
    for j in range(i):

        previous_transaction = df.iloc[j]

        previous_time = previous_transaction["timestamp"]

        time_difference = (
            current_time - previous_time
        ).total_seconds() / 60

        # Transactions within 5 minutes
        if time_difference <= 5:

            # Only count transactions from different accounts
            if (
                current_transaction["account_id"]
                != previous_transaction["account_id"]
            ):

                transaction_scores[current_id] += 15

                transaction_reasons[current_id].append(
                    "Occurs within 5 minutes of another account's transaction"
                )

                break


# ==========================================
# LIMIT SCORE TO 100
# ==========================================

for transaction in transaction_scores:

    transaction_scores[transaction] = min(
        transaction_scores[transaction],
        100
    )


# ==========================================
# TRANSACTION RISK LEVEL
# ==========================================

def get_transaction_risk(score):

    if score >= 80:
        return "CRITICAL"

    elif score >= 60:
        return "HIGH"

    elif score >= 30:
        return "MEDIUM"

    else:
        return "LOW"


# ==========================================
# DISPLAY TRANSACTION SCORES
# ==========================================

print("\nTRANSACTION SCORES")
print("-" * 60)


for transaction, score in transaction_scores.items():

    level = get_transaction_risk(score)

    print(f"\nTransaction: {transaction}")
    print(f"Risk Score : {score}/100")
    print(f"Risk Level : {level}")

    if transaction_reasons[transaction]:

        print("Reasons:")

        for reason in transaction_reasons[transaction]:

            print(f"  - {reason}")

    else:

        print("Reasons: No suspicious behavior")


print("\n" + "=" * 60)
print("Transaction analysis completed.")
print("=" * 60)

# ==========================================
# 11. GENERATE JSON OUTPUT
# ==========================================

import json
from pathlib import Path

print("\n" + "=" * 60)
print("             GENERATING JSON OUTPUT")
print("=" * 60)


# ==========================================
# CREATE RESULTS FOLDER
# ==========================================

results_folder = Path("results")

results_folder.mkdir(exist_ok=True)


# ==========================================
# TRANSACTION RESULTS
# ==========================================

transaction_results = []

for _, row in df.iterrows():

    transaction_id = row["transaction_id"]
    account_id = row["account_id"]

    score = transaction_scores.get(
        transaction_id,
        0
    )

    risk_level = get_transaction_risk(score)

    transaction_result = {

        "transaction_id": transaction_id,

        "account_id": account_id,

        "amount": float(row["amount"]),

        "timestamp": str(row["timestamp"]),

        "device_id": row["device_id"],

        "ip_address": row["ip_address"],

        "location": row["location"],

        "merchant_id": row["merchant_id"],

        "destination_account":
            row["destination_account"],

        "payment_channel":
            row["payment_channel"],

        "risk_score": int(score),

        "risk_level": risk_level,

        "reasons":
            transaction_reasons.get(
                transaction_id,
                []
            )
    }

    transaction_results.append(
        transaction_result
    )


# ==========================================
# ACCOUNT RESULTS
# ==========================================

account_results = []

for account, score in risk_scores.items():

    account_result = {

        "account_id": account,

        "risk_score": int(score),

        "risk_level":
            get_risk_level(score),

        "reasons":
            risk_reasons.get(
                account,
                []
            )
    }

    account_results.append(
        account_result
    )


# ==========================================
# FRAUD RING INFORMATION
# ==========================================

fraud_ring = {

    "ring_id": "FR001",

    "detected": len(fraud_accounts) > 0,

    "accounts": fraud_accounts,

    "risk_score": (
        max(
            [
                risk_scores[a]
                for a in fraud_accounts
            ],
            default=0
        )
    ),

    "evidence": []
}


# ==========================================
# ADD FRAUD RING EVIDENCE
# ==========================================

if fraud_accounts:

    suspicious_df = df[
        df["account_id"].isin(
            fraud_accounts
        )
    ]

    # Shared devices
    for device, accounts in (
        suspicious_df
        .groupby("device_id")["account_id"]
        .unique()
        .items()
    ):

        if len(accounts) > 1:

            fraud_ring["evidence"].append(
                f"Accounts share device {device}"
            )


    # Shared IPs
    for ip, accounts in (
        suspicious_df
        .groupby("ip_address")["account_id"]
        .unique()
        .items()
    ):

        if len(accounts) > 1:

            fraud_ring["evidence"].append(
                f"Accounts share IP address {ip}"
            )


    # Common destinations
    for destination, accounts in (
        suspicious_df
        .groupby(
            "destination_account"
        )["account_id"]
        .unique()
        .items()
    ):

        if len(accounts) > 1:

            fraud_ring["evidence"].append(
                f"Accounts transfer to common destination {destination}"
            )


# ==========================================
# COMPLETE PROJECT RESULT
# ==========================================

final_result = {

    "project":
        "Real-Time Financial Fraud Intelligence",

    "status":
        "analysis_completed",

    "summary": {

        "total_transactions":
            len(df),

        "total_accounts":
            int(df["account_id"].nunique()),

        "suspicious_accounts":
            len(fraud_accounts),

        "fraud_ring_detected":
            len(fraud_accounts) > 0
    },

    "fraud_ring":
        fraud_ring,

    "accounts":
        account_results,

    "transactions":
        transaction_results
}


# ==========================================
# SAVE JSON
# ==========================================

output_file = (
    results_folder /
    "analysis.json"
)


with open(
    output_file,
    "w",
    encoding="utf-8"
) as file:

    json.dump(
        final_result,
        file,
        indent=4
    )


print(
    f"\nJSON saved to: {output_file}"
)

print("\nJSON generation completed.")

print("=" * 60)


# ==========================================
# 12. FRAUD NETWORK VISUALIZATION
# ==========================================

import matplotlib.pyplot as plt


print("\n" + "=" * 60)
print("          CREATING FRAUD NETWORK GRAPH")
print("=" * 60)


# ==========================================
# CREATE A NEW GRAPH FOR VISUALIZATION
# ==========================================

visual_graph = nx.Graph()


# ==========================================
# ADD TRANSACTION RELATIONSHIPS
# ==========================================

for _, row in df.iterrows():

    account = row["account_id"]
    device = row["device_id"]
    ip = row["ip_address"]
    merchant = row["merchant_id"]
    destination = row["destination_account"]

    # Account
    visual_graph.add_node(
        account,
        node_type="account"
    )

    # Device
    visual_graph.add_node(
        device,
        node_type="device"
    )

    # IP
    visual_graph.add_node(
        ip,
        node_type="ip"
    )

    # Merchant
    visual_graph.add_node(
        merchant,
        node_type="merchant"
    )

    # Destination
    visual_graph.add_node(
        destination,
        node_type="destination"
    )

    # Connections
    visual_graph.add_edge(
        account,
        device
    )

    visual_graph.add_edge(
        account,
        ip
    )

    visual_graph.add_edge(
        account,
        merchant
    )

    visual_graph.add_edge(
        account,
        destination
    )


# ==========================================
# CREATE GRAPH LAYOUT
# ==========================================

plt.figure(figsize=(14, 10))

position = nx.spring_layout(
    visual_graph,
    seed=42,
    k=1.5
)


# ==========================================
# DRAW GRAPH
# ==========================================

nx.draw_networkx_edges(
    visual_graph,
    position,
    width=1.5
)


nx.draw_networkx_nodes(
    visual_graph,
    position,
    node_size=1200
)


nx.draw_networkx_labels(
    visual_graph,
    position,
    font_size=9,
    font_weight="bold"
)


# ==========================================
# TITLE
# ==========================================

plt.title(
    "Financial Fraud Network",
    fontsize=18,
    fontweight="bold"
)


plt.axis("off")


# ==========================================
# SAVE GRAPH
# ==========================================

graph_file = (
    results_folder /
    "fraud_network.png"
)

plt.savefig(
    graph_file,
    dpi=200,
    bbox_inches="tight"
)


print(
    f"\nFraud network saved to: {graph_file}"
)


plt.show()


print("\n" + "=" * 60)
print("Network visualization completed.")
print("=" * 60)


# ==========================================
# 13. CLEAN FRAUD RING VISUALIZATION
# ==========================================

print("\n" + "=" * 60)
print("        CREATING CLEAN FRAUD RING GRAPH")
print("=" * 60)


# Create a new graph
fraud_graph = nx.Graph()


# Only use suspicious accounts
suspicious_accounts = fraud_accounts


for _, row in df.iterrows():

    account = row["account_id"]

    # Ignore normal accounts
    if account not in suspicious_accounts:
        continue

    device = row["device_id"]
    ip = row["ip_address"]
    merchant = row["merchant_id"]
    destination = row["destination_account"]

    # Add nodes
    fraud_graph.add_node(
        account,
        type="account"
    )

    fraud_graph.add_node(
        device,
        type="device"
    )

    fraud_graph.add_node(
        ip,
        type="ip"
    )

    fraud_graph.add_node(
        merchant,
        type="merchant"
    )

    fraud_graph.add_node(
        destination,
        type="destination"
    )

    # Add important connections

    fraud_graph.add_edge(
        account,
        device
    )

    fraud_graph.add_edge(
        account,
        ip
    )

    fraud_graph.add_edge(
        account,
        merchant
    )

    fraud_graph.add_edge(
        account,
        destination
    )


# ==========================================
# DRAW CLEAN GRAPH
# ==========================================

plt.figure(figsize=(14, 10))


position = nx.spring_layout(
    fraud_graph,
    seed=42,
    k=2
)


# Draw edges
nx.draw_networkx_edges(
    fraud_graph,
    position,
    width=2
)


# Separate node types
account_nodes = []
device_nodes = []
ip_nodes = []
merchant_nodes = []
destination_nodes = []


for node, data in fraud_graph.nodes(
    data=True
):

    if data["type"] == "account":

        account_nodes.append(node)

    elif data["type"] == "device":

        device_nodes.append(node)

    elif data["type"] == "ip":

        ip_nodes.append(node)

    elif data["type"] == "merchant":

        merchant_nodes.append(node)

    elif data["type"] == "destination":

        destination_nodes.append(node)


# Draw accounts
nx.draw_networkx_nodes(
    fraud_graph,
    position,
    nodelist=account_nodes,
    node_size=1800
)


# Draw devices
nx.draw_networkx_nodes(
    fraud_graph,
    position,
    nodelist=device_nodes,
    node_size=1400
)


# Draw IP addresses
nx.draw_networkx_nodes(
    fraud_graph,
    position,
    nodelist=ip_nodes,
    node_size=1400
)


# Draw merchants
nx.draw_networkx_nodes(
    fraud_graph,
    position,
    nodelist=merchant_nodes,
    node_size=1400
)


# Draw destinations
nx.draw_networkx_nodes(
    fraud_graph,
    position,
    nodelist=destination_nodes,
    node_size=1800
)


# Labels
nx.draw_networkx_labels(
    fraud_graph,
    position,
    font_size=10,
    font_weight="bold"
)


# ==========================================
# TITLE
# ==========================================

plt.title(
    "Detected Fraud Ring - FR001",
    fontsize=20,
    fontweight="bold"
)

plt.axis("off")


# ==========================================
# SAVE
# ==========================================

clean_graph_file = (
    results_folder /
    "fraud_ring_FR001.png"
)


plt.savefig(
    clean_graph_file,
    dpi=200,
    bbox_inches="tight"
)


print(
    f"\nClean fraud ring saved to: "
    f"{clean_graph_file}"
)


plt.show()