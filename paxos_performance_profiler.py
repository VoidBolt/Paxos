import pandas as pd
import glob
import os
import re
import matplotlib.pyplot as plt
import numpy as np
import seaborn as sns
LOG_DIR = "logs"


# =========================================================
# LOAD + NORMALIZE
# =========================================================

files = glob.glob(f"{LOG_DIR}/paxosresult_*.csv")

dfs = []

for f in files:
    df = pd.read_csv(f)

    node = int(re.search(r"paxosresult_(\d+)", os.path.basename(f)).group(1))

    df["node"] = node
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


# =========================================================
# MESSAGE LATENCY (SEND → RECEIVE)
# =========================================================

send = df[df["direction"] == "SEND"].copy()
recv = df[df["direction"] == "RECEIVE"].copy()

merged = pd.merge(
    send,
    recv,
    on=["proposal_id", "msg_type"],
    suffixes=("_send", "_recv")
)

merged["latency_ms"] = (merged["timestamp_recv"] - merged["timestamp_send"]) * 1000
merged = merged[merged["latency_ms"] >= 0]


# =========================================================
# BASIC STATS
# =========================================================

print("\n=== LATENCY SUMMARY (ms) ===")
print(merged["latency_ms"].describe())

print("\n=== NODE MEAN LATENCY (ms) ===")
print(merged.groupby("node_send")["latency_ms"].mean().sort_values())

print("\n=== NODE JITTER (std ms) ===")
print(merged.groupby("node_send")["latency_ms"].std().sort_values())


# =========================================================
# PHASE ANALYSIS (Paxos-aware)
# =========================================================

def phase(row):
    if "PREPARE" in row:
        return "PREPARE"
    if "PROMISE" in row:
        return "PROMISE"
    if "ACCEPT" in row and "ACCEPTED" not in row:
        return "ACCEPT"
    if "ACCEPTED" in row:
        return "ACCEPTED"
    return "OTHER"

merged["phase"] = merged["msg_type"].apply(phase)

phase_stats = merged.groupby("phase")["latency_ms"].mean().sort_values()


plt.figure()
phase_stats.plot(kind="bar")
plt.title("Average Latency per Paxos Phase (ms)")
plt.ylabel("Latency (ms)")
plt.tight_layout()
plt.show()


# =========================================================
# TIME SERIES + JITTER VIEW
# =========================================================

merged = merged.sort_values("timestamp_send")

plt.figure()
plt.plot(merged["timestamp_send"], merged["latency_ms"], linewidth=0.7)
plt.title("Latency Over Time (Jitter View)")
plt.xlabel("Time")
plt.ylabel("Latency (ms)")
plt.tight_layout()
plt.show()


# rolling mean (system stability)
merged["rolling"] = merged["latency_ms"].rolling(30).mean()

plt.figure()
plt.plot(merged["timestamp_send"], merged["rolling"])
plt.title("Rolling Mean Latency (window=30)")
plt.xlabel("Time")
plt.ylabel("Latency (ms)")
plt.tight_layout()
plt.show()


# =========================================================
# TAIL LATENCY ANALYSIS (top 5%)
# =========================================================

threshold = merged["latency_ms"].quantile(0.95)
tail = merged[merged["latency_ms"] >= threshold]

plt.figure()
plt.hist(tail["latency_ms"], bins=30)
plt.title("Tail Latency (Top 5%)")
plt.xlabel("Latency (ms)")
plt.ylabel("Count")
plt.tight_layout()
plt.show()

print("\n=== TAIL ANALYSIS (p95+) ===")
print(tail.groupby("node_send")["latency_ms"].agg(["count", "mean", "max"]).sort_values("mean", ascending=False))


# =========================================================
# END-TO-END PROPOSAL LATENCY
# =========================================================

proposal_latency = merged.groupby("proposal_id")["latency_ms"].sum()

plt.figure()
plt.hist(proposal_latency, bins=40)
plt.title("End-to-End Proposal Latency (approx ms)")
plt.xlabel("Latency (ms)")
plt.ylabel("Count")
plt.tight_layout()
plt.show()


print("\n=== PROPOSAL LATENCY ===")
print(proposal_latency.describe())

# assumes merged dataframe already exists
df = merged.copy()
df = df.sort_values("timestamp_send")


# =========================================================
# 1. LATENCY DISTRIBUTION (with percentiles)
# =========================================================

plt.figure()

plt.hist(df["latency_ms"], bins=60, alpha=0.6, label="All latencies")

for p in [50, 90, 95, 99]:
    val = np.percentile(df["latency_ms"], p)
    plt.axvline(val, linestyle="--", label=f"p{p}: {val:.1f} ms")

plt.title("Paxos Latency Distribution with Percentiles")
plt.xlabel("Latency (ms)")
plt.ylabel("Frequency")
plt.legend()
plt.tight_layout()
plt.show()


# =========================================================
# 2. LOG SCALE TAIL VISUALIZATION (VERY IMPORTANT)
# =========================================================

plt.figure()
plt.hist(df["latency_ms"], bins=60)
plt.yscale("log")
plt.title("Latency Distribution (log scale view)")
plt.xlabel("Latency (ms)")
plt.ylabel("Log frequency")
plt.tight_layout()
plt.show()


# =========================================================
# 3. LATENCY OVER TIME (SMOOTHED)
# =========================================================

df["rolling"] = df["latency_ms"].rolling(20).mean()

plt.figure()
plt.plot(df["timestamp_send"], df["latency_ms"], alpha=0.3, label="raw")
plt.plot(df["timestamp_send"], df["rolling"], linewidth=2, label="rolling mean")

plt.title("Latency Over Time (Raw vs Smoothed)")
plt.xlabel("Time")
plt.ylabel("Latency (ms)")
plt.legend()
plt.tight_layout()
plt.show()


# =========================================================
# 4. JITTER (VIOLIN PLOT - MUCH BETTER THAN SCATTER)
# =========================================================

import seaborn as sns

plt.figure()
sns.violinplot(x="node_send", y="latency_ms", data=df, inner="quartile")
plt.title("Per-Node Latency Distribution (Jitter View)")
plt.xlabel("Node")
plt.ylabel("Latency (ms)")
plt.tight_layout()
plt.show()


# =========================================================
# 5. TAIL EVENTS ONLY (TOP 5%)
# =========================================================

threshold = np.percentile(df["latency_ms"], 95)
tail = df[df["latency_ms"] >= threshold]

plt.figure()
plt.scatter(tail["timestamp_send"], tail["latency_ms"], alpha=0.7)
plt.title("Tail Latency Events (Top 5%)")
plt.xlabel("Time")
plt.ylabel("Latency (ms)")
plt.tight_layout()
plt.show()


# =========================================================
# 6. NODE PERFORMANCE SUMMARY (BAR CHART)
# =========================================================

node_stats = df.groupby("node_send")["latency_ms"].agg(["mean", "std", "max"])

plt.figure()
node_stats["mean"].plot(kind="bar", yerr=node_stats["std"], capsize=5)
plt.title("Node Mean Latency (with jitter error bars)")
plt.ylabel("Latency (ms)")
plt.tight_layout()
plt.show()
