import matplotlib.pyplot as plt

# Example data from your tests
nodes = [1, 2, 3, 4, 5]
time_events = {
    # Node: [(start_time, end_time, "status")]
    1: [(0, 2, "running"), (2, 2.5, "crashed"), (2.5, 5, "running")],
    2: [(0, 5, "running")],
    3: [(0, 5, "running")],
    4: [(0, 5, "running")],
    5: [(0, 5, "running")],
}

# Proposals: (node, time, label)
proposals = [
    (1, 1, "grape"),
    (2, 3, "melon"),  # after Node 1 crash
]

fig, ax = plt.subplots(figsize=(10, 6))

# Plot node status bars
for node in nodes:
    for start, end, status in time_events[node]:
        color = "green" if status == "running" else "red"
        ax.barh(node, end - start, left=start, height=0.6, color=color, edgecolor="black")

# Plot proposal points
for node, t, label in proposals:
    ax.plot(t, node, marker="o", color="blue")
    ax.text(t + 0.05, node, label, verticalalignment="center", color="blue", fontsize=10)

# Labels and grid
ax.set_yticks(nodes)
ax.set_yticklabels([f"Node {n}" for n in nodes])
ax.set_xlabel("Time (s)")
ax.set_title("Paxos Cluster Timeline: Node Status and Proposals")
ax.grid(axis="x", linestyle="--", alpha=0.7)

# Legend
from matplotlib.patches import Patch
legend_elements = [
    Patch(facecolor="green", edgecolor="black", label="Running"),
    Patch(facecolor="red", edgecolor="black", label="Crashed"),
    Patch(facecolor="blue", label="Proposal")
]
ax.legend(handles=legend_elements, loc="upper right")

plt.tight_layout()
plt.savefig("paxos_timeline.png", dpi=300)
plt.show()

