import pandas as pd
import glob
import os
import re
import matplotlib.pyplot as plt

LOG_DIR = "logs"


# ----------------------------
# Helpers
# ----------------------------

def extract_node_id(filename: str):
    # paxosresult_3_3538947.csv -> node 3
    match = re.search(r"paxosresult_(\d+)", os.path.basename(filename))
    return int(match.group(1)) if match else -1


def extract_proposal_id(action_value):
    if pd.isna(action_value):
        return None
    match = re.search(r"proposal_id=(\d+)", str(action_value))
    return int(match.group(1)) if match else None


def extract_msg_type(action):
    # SEND_PREPARE -> PREPARE
    # RECEIVE_ACCEPT -> ACCEPT
    if pd.isna(action):
        return None
    return str(action).replace("SEND_", "").replace("RECEIVE_", "")


# ----------------------------
# Load + unify logs
# ----------------------------

files = glob.glob(f"{LOG_DIR}/paxosresult_*.csv")

dfs = []

for f in files:
    df = pd.read_csv(f)

    df["node_file"] = extract_node_id(f)
    df["timestamp"] = df["Timestamp"].astype(float)
    df["proposal_id"] = df["Action Value"].apply(extract_proposal_id)
    df["msg_type"] = df["Action"].apply(extract_msg_type)
    df["direction"] = df["Action"].apply(
        lambda x: "SEND" if isinstance(x, str) and x.startswith("SEND") else
                  "RECEIVE" if isinstance(x, str) and x.startswith("RECEIVE") else "OTHER"
    )

    dfs.append(df)

df = pd.concat(dfs, ignore_index=True)


# ----------------------------
# Split SEND / RECEIVE
# ----------------------------

send = df[df["direction"] == "SEND"].copy()
recv = df[df["direction"] == "RECEIVE"].copy()


# ----------------------------
# Match SEND -> RECEIVE
# (proposal_id + msg_type)
# ----------------------------

merged = pd.merge(
    send,
    recv,
    on=["proposal_id", "msg_type"],
    suffixes=("_send", "_recv")
)

merged["latency"] = merged["timestamp_recv"] - merged["timestamp_send"]

# filter junk / negative due to logging ordering issues
merged = merged[merged["latency"] >= 0]


# ----------------------------
# 1. Latency distribution
# ----------------------------

plt.figure()
plt.hist(merged["latency"], bins=40)
plt.title("Paxos Message Latency Distribution")
plt.xlabel("Latency (seconds)")
plt.ylabel("Count")
plt.tight_layout()
plt.show()


# ----------------------------
# 2. Latency over time
# ----------------------------

plt.figure()
plt.scatter(merged["timestamp_send"], merged["latency"], alpha=0.5)
plt.title("Paxos Latency Over Time")
plt.xlabel("Send Timestamp")
plt.ylabel("Latency (seconds)")
plt.tight_layout()
plt.show()


# ----------------------------
# 3. Per-node latency comparison
# (based on sender node)
# ----------------------------

plt.figure()

nodes = sorted(merged["node_file_send"].unique())

for n in nodes:
    subset = merged[merged["node_file_send"] == n]
    plt.scatter([n] * len(subset), subset["latency"], alpha=0.4)

plt.title("Latency Distribution per Node (Sender)")
plt.xlabel("Node ID")
plt.ylabel("Latency (seconds)")
plt.xticks(nodes)
plt.tight_layout()
plt.show()


# ----------------------------
# Summary stats
# ----------------------------

print("\n=== LATENCY STATS ===")
print(merged["latency"].describe())

print("\n=== PER NODE MEAN LATENCY ===")
print(
    merged.groupby("node_file_send")["latency"]
    .mean()
    .sort_values()
)
