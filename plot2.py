import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
import datetime

# Load and combine CSVs
files = [f"paxosresult_{i}.csv" for i in range(1, 4)]
dfs = [pd.read_csv(f) for f in files]
df = pd.concat(dfs, ignore_index=True)

# Use float timestamps directly
df['Timestamp'] = df['Timestamp'].astype(float)

# All nodes
nodes = sorted(df['From Node ID'].unique())

# Action to marker/color mapping
action_map = {
    'SEND_PREPARE': ('o', 'blue'),
    'RECEIVE_PREPARE': ('*', 'brown'),
    'SEND_PROMISE': ('*', 'magenta'),
    'RECEIVE_PROMISE': ('^', 'orange'),
    'SEND_ACCEPT': ('s', 'green'),
    'RECEIVE_ACCEPT': ('v', 'red'),
    'SEND_LEARN': ('D', 'purple'),
    'RECEIVE_LEARN_OK': ('*', 'brown'),
    'SEND_LEARN_OK': ('P', 'pink')
}

# Create plot
fig, ax = plt.subplots(figsize=(14, 6))

# Plot events
for _, row in df.iterrows():
    action = str(row['Action'])
    if action in action_map:
        marker, color = action_map[action]
        # Plot the symbol at the sender
        ax.plot(row['Timestamp'], row['From Node ID'], marker=marker, color=color, markersize=8)
        # Draw a line/arrow to the recipient
        ax.plot([row['Timestamp'], row['Timestamp']],
                [row['From Node ID'], row['To Node ID']],
                color=color, linestyle='--', alpha=0.6)

# Configure axes
ax.set_yticks(nodes)
ax.set_yticklabels([f"Node {n}" for n in nodes])
ax.set_xlabel("Time (seconds since epoch)")
ax.set_ylabel("Node ID")
ax.set_title("Paxos Proposal and Consensus Events per Node")
ax.grid(axis="x", linestyle="--", alpha=0.5)

# Adjust x-axis limits
ax.set_xlim(df['Timestamp'].min() - 0.01, df['Timestamp'].max() + 0.01)

# Optional: human-readable ticks
tick_dt = [datetime.datetime.fromtimestamp(ts) for ts in ax.get_xticks()]
ax.set_xticklabels([dt.strftime("%H:%M:%S.%f")[:-3] for dt in tick_dt], rotation=45, ha='right')

# Legend outside the plot
legend_elements = [
    Line2D([0], [0], marker=m, color='w', label=a, markerfacecolor=c, markersize=8)
    for a, (m, c) in action_map.items()
]
ax.legend(handles=legend_elements, loc='upper left', bbox_to_anchor=(1, 1))

plt.tight_layout()
plt.savefig("paxos_events_with_arrows.png", dpi=300, bbox_inches='tight')
plt.show()
