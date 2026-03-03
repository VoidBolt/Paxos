import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from datetime import datetime

# Load all CSVs into a single dataframe
csv_files = ["paxosresult_1.csv", "paxosresult_2.csv"]  # add more if needed
dfs = [pd.read_csv(f) for f in csv_files]
df = pd.concat(dfs, ignore_index=True)

# Convert Timestamp column to datetime
df['Timestamp'] = pd.to_datetime(df['Timestamp'])

# Map node IDs to y-axis positions
nodes = sorted(df['From Node ID'].unique())
node_y = {node_id: i+1 for i, node_id in enumerate(nodes)}

# Map actions to markers/colors
action_colors = {
    "SEND_PREPARE": 'blue',
    "RECEIVE_PROMISE": 'green',
    "SEND_ACCEPT": 'red',
    "RECEIVE_ACCEPT": 'orange',
    "SEND_LEARN": 'purple',
    "RECEIVE_LEARN": 'brown',
    "COORDINATOR": 'pink'
}
action_markers = {
    "SEND_PREPARE": 'o',
    "RECEIVE_PROMISE": '^',
    "SEND_ACCEPT": 's',
    "RECEIVE_ACCEPT": 'D',
    "SEND_LEARN": 'X',
    "RECEIVE_LEARN": 'P',
    "COORDINATOR": '*'
}

fig, ax = plt.subplots(figsize=(12, 6))

for idx, row in df.iterrows():
    y = node_y[row['From Node ID']]
    ax.scatter(row['Timestamp'], y,
               color=action_colors.get(row['Action'], 'black'),
               marker=action_markers.get(row['Action'], 'o'),
               s=100)
    # Draw line to target node (optional, for SEND actions)
    if 'SEND' in row['Action']:
        y_to = node_y.get(row['To Node ID'], y)
        ax.plot([row['Timestamp'], row['Timestamp']], [y, y_to],
                color='gray', linestyle='--', alpha=0.5)

# Formatting
ax.set_yticks(list(node_y.values()))
ax.set_yticklabels([f"Node {n}" for n in node_y.keys()])
ax.set_xlabel("Time")
ax.set_ylabel("Nodes")
ax.xaxis.set_major_formatter(mdates.DateFormatter("%H:%M:%S"))
plt.title("Paxos Node Event Timeline")

# Legend
handles = [plt.Line2D([0], [0], marker=action_markers[a], color='w',
                      markerfacecolor=c, markersize=10) 
           for a, c in action_colors.items()]
labels = list(action_colors.keys())
ax.legend(handles, labels, title="Action Type", bbox_to_anchor=(1.05, 1), loc='upper left')

plt.tight_layout()
plt.show()
