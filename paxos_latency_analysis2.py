import pandas as pd
import glob
import os
import re
import matplotlib.pyplot as plt

LOG_DIR = "logs"


# ----------------------------
# Load logs
# ----------------------------

files = glob.glob(f"{LOG_DIR}/paxosresult_*.csv")

dfs = []

for f in files:
    df = pd.read_csv(f)

    node_id = int(re.search(r"paxosresult_(\d+)", os.path.basename(f)).group(1))

    df["node"] = node_id
    df["timestamp"] = df["Timestamp"].astype(float)

    df["proposal_id"] = df["Action Value"].str.extract(r"proposal_id=(\d+)").astype(float)
    df["msg_type"] = df["Action"].str.replace("SEND_", "").str.replace("RECEIVE_", "")

    df["direction"] = df["Action"].apply(
        lambda x: "SEND" if "SEND" in str(x)
        else "RECEIVE" if "RECEIVE" in str(x)
        else "OTHER"
    )

    dfs.append(df)

df = pd.concat(dfs, ignore_index=True)


# ----------------------------
# Match SEND -> RECEIVE
# ----------------------------

send = df[df["direction"] == "SEND"].copy()
recv = df[df["direction"] == "RECEIVE"].copy()

merged = pd.merge(
    send,
    recv,
    on=["proposal_id", "msg_type"],
    suffixes=("_send", "_recv")
)

merged["latency_ms"] = (merged["timestamp_recv"] - merged["timestamp_send"]) * 1000

# remove insane negatives / corruption
merged = merged[merged["latency_ms"] >= 0]


# ----------------------------
# 1. CLEAN LATENCY DISTRIBUTION
# ----------------------------

plt.figure()
plt.hist(merged["latency_ms"], bins=80)
plt.title("Paxos Latency Distribution (ms)")
plt.xlabel("Latency (ms)")
plt.ylabel("Count")
plt.show()


# ----------------------------
# 2. LATENCY OVER TIME (JITTER VIEW)
# ----------------------------

merged = merged.sort_values("timestamp_send")

plt.figure()
plt.plot(merged["timestamp_send"], merged["latency_ms"], linewidth=0.8)
plt.title("Latency Over Time (Jitter View)")
plt.xlabel("Time")
plt.ylabel("Latency (ms)")
plt.show()


# ----------------------------
# 3. ROLLING AVERAGE (SMOOTH VIEW)
# ----------------------------

merged["rolling_mean"] = merged["latency_ms"].rolling(50).mean()

plt.figure()
plt.plot(merged["timestamp_send"], merged["rolling_mean"])
plt.title("Rolling Mean Latency (window=50)")
plt.xlabel("Time")
plt.ylabel("Avg Latency (ms)")
plt.show()


# ----------------------------
# 4. NODE COMPARISON (BOX-LIKE VIEW)
# ----------------------------

plt.figure()

for node in sorted(merged["node_send"].unique()):
    subset = merged[merged["node_send"] == node]
    plt.scatter([node] * len(subset), subset["latency_ms"], alpha=0.4)

plt.title("Latency per Node (ms)")
plt.xlabel("Node")
plt.ylabel("Latency (ms)")
plt.show()


# ----------------------------
# 5. JITTER METRIC PER NODE
# ----------------------------

jitter = merged.groupby("node_send")["latency_ms"].std()

plt.figure()
plt.bar(jitter.index.astype(str), jitter.values)
plt.title("Network Jitter per Node (std dev ms)")
plt.xlabel("Node")
plt.ylabel("Jitter (ms)")
plt.show()


# ----------------------------
# STATS
# ----------------------------

print("\n=== LATENCY (ms) ===")
print(merged["latency_ms"].describe())

print("\n=== NODE MEAN LATENCY (ms) ===")
print(merged.groupby("node_send")["latency_ms"].mean().sort_values())

print("\n=== NODE JITTER (std ms) ===")
print(jitter.sort_values())
