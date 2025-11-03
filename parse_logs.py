import re
import argparse
import os
import json
# Example timestamp regex: [2025-10-20 16:18:14,925]
TIMESTAMP_RE = re.compile(r"\[(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2},\d+)\]")
"""
def parse_logs(logfiles):
    all_events = []
    for logfile in logfiles:
        all_events.extend(parse_log(logfile))
    print(all_events)
    input("...")
    all_events.sort(key=lambda x: x[3])  # assuming x[3] is timestamp
    # Deduplicate and sort by timestamp if available
    seen = set()
    unique_events = []
    for e in all_events:
        if e not in seen:
            seen.add(e)
            unique_events.append(e)
    return unique_events
"""
def parse_single_log_json(logfile):
    """Parse one node JSON log and return list of (ts, src, dst, msg) tuples."""
    events = []
    with open(logfile) as f:
        for line in f:
            try:
                rec = json.loads(line)
            except json.JSONDecodeError:
                continue

            ts = rec.get("ts")
            node_id = rec.get("node_id")
            event = rec.get("event")
            peer = rec.get("peer", "")
            value = rec.get("value", "")
            slot = rec.get("slot")
            pid = rec.get("proposal_id")

            if not node_id or not event:
                continue  # skip boilerplate lines

            src = f"Node{node_id}"

            # Determine destination from "peer" field if it contains "[Node X]"
            dst = src
            if isinstance(peer, str) and "[Node " in peer:
                m = re.search(r"\[Node (\d+)\]", peer)
                if m:
                    dst = f"Node{m.group(1)}"

            # Human-readable message text
            msg = event.upper()
            if value:
                msg += f" {value}"
            if slot:
                msg += f" (slot {slot})"
            if pid:
                msg += f" pid={pid}"

            events.append((ts, src, dst, msg))
    return events


def parse_logs_json(logdir):
    """Load and merge all node_*.log files (JSON format) into sorted events."""
    all_events = []
    for fname in os.listdir(logdir):
        if fname.startswith("node_") and fname.endswith(".log"):
            path = os.path.join(logdir, fname)
            all_events.extend(parse_single_log_json(path))

    # Sort chronologically
    all_events.sort(key=lambda x: x[0])
    return all_events

def parse_single_log(logfile):
    """Parse one node log and return a list of events with timestamps."""
    # Regex patterns
    patterns = {
        "PROPOSE": re.compile(r"\[Node (\d+)\].*proposing value -> (.+)"),
        "PROMISE": re.compile(r"\[Node (\d+).*PROMISE pid=.* slot=(\d+)"),
        "ACCEPTED": re.compile(r"\[Node (\d+).*ACCEPTED pid=.* value=(.+) slot=(\d+)"),
        "DECIDED": re.compile(r"\[Node (\d+).*DECIDED slot=(\d+) value=(.+)"),
        "LEARNED": re.compile(r"\[Node (\d+).*LEARNED value=(.+) slot=(\d+)"),
    }

    events = []

    with open(logfile) as f:
        for line in f:
            ts_match = TIMESTAMP_RE.search(line)
            ts = ts_match.group(1) if ts_match else None

            for kind, pattern in patterns.items():
                if m := pattern.search(line):
                    if kind == "PROPOSE":
                        node, val = m.groups()
                        events.append((ts, f"Node{node}", f"PROPOSE {val.strip()}"))
                    elif kind == "PROMISE":
                        node, slot = m.groups()
                        events.append((ts, f"Node{node}", f"PROMISE (slot {slot})"))
                    elif kind == "ACCEPTED":
                        node, val, slot = m.groups()
                        events.append((ts, f"Node{node}", f"ACCEPTED {val.strip()} (slot {slot})"))
                    elif kind == "DECIDED":
                        node, slot, val = m.groups()
                        events.append((ts, f"Node{node}", f"DECIDED {val.strip()} (slot {slot})"))
                    elif kind == "LEARNED":
                        node, val, slot = m.groups()
                        events.append((ts, f"Node{node}", f"LEARNED {val.strip()} (slot {slot})"))
                    break  # only match one pattern per line

    return events

def parse_logs(logdir):
    """Parse all node logs in a directory and return merged, sorted events."""
    all_events = []
    for fname in os.listdir(logdir):
        if fname.startswith("node_") and fname.endswith(".log"):
            logfile = os.path.join(logdir, fname)
            events = parse_single_log(logfile)
            print(events)
            input()
            all_events.extend(events)

    # Sort by timestamp
    all_events.sort(key=lambda x: x[0] or "")

    # Deduplicate exact duplicates
    seen = set()
    unique_events = []
    for e in all_events:
        if e not in seen:
            seen.add(e)
            unique_events.append(e)

    return unique_events

def parse_log(logfile):
    # Regex patterns
    pattern_propose = re.compile(r"\[Node (\d+)\].*proposing value -> (.+)")
    pattern_promise = re.compile(r"\[Node (\d+).*PROMISE pid=.* slot=(\d+)")
    pattern_accepted = re.compile(r"\[Node (\d+).*ACCEPTED pid=.* value=(.+) slot=(\d+)")
    pattern_decided = re.compile(r"\[Node (\d+).*DECIDED slot=(\d+) value=(.+)")
    pattern_learned = re.compile(r"\[Node (\d+).*LEARNED value=(.+) slot=(\d+)")

    events = []
    current_proposer = None
    current_value = None

    with open(logfile) as f:
        for line in f:
            # 1️⃣ A node starts proposing a value
            if m := pattern_propose.search(line):
                proposer, val = m.groups()
                current_proposer = proposer
                current_value = val.strip()
                events.append((f"Node{proposer}", f"Node{proposer}", f"PROPOSE {current_value}"))
            
            # 2️⃣ Nodes send PROMISE responses
            elif m := pattern_promise.search(line):
                node, slot = m.groups()
                if current_proposer:
                    events.append((f"Node{node}", f"Node{current_proposer}", f"PROMISE (slot {slot})"))
            
            # 3️⃣ Nodes accept a value
            elif m := pattern_accepted.search(line):
                node, val, slot = m.groups()
                if current_proposer:
                    events.append((f"Node{node}", f"Node{current_proposer}", f"ACCEPTED {val.strip()} (slot {slot})"))
            
            # 4️⃣ The proposer decides on a value
            elif m := pattern_decided.search(line):
                node, slot, val = m.groups()
                events.append((f"Node{current_proposer or node}", f"Node{node}", f"DECIDED {val.strip()} (slot {slot})"))
            
            # 5️⃣ Learners learn the chosen value
            elif m := pattern_learned.search(line):
                node, val, slot = m.groups()
                events.append((f"Node{current_proposer or node}", f"Node{node}", f"LEARNED {val.strip()} (slot {slot})"))

    # Deduplicate and preserve order
    seen = set()
    unique_events = []
    for e in events:
        if e not in seen:
            seen.add(e)
            unique_events.append(e)

    return unique_events

"""
def write_plantuml(events, output_path):
    with open(output_path, "w") as out:
        out.write("@startuml\n")
        out.write("title Paxos Single-Decree Sequence\n")
        out.write("participant Node1\nparticipant Node2\nparticipant Node3\nparticipant Node4\nparticipant Node5\n\n")

        for src, dst, msg in events:
            # Visual tweak: “PROPOSE” appears as a note instead of a message
            if src == dst and "PROPOSE" in msg:
                out.write(f"note over {src}: {msg}\n")
            elif src == dst:
                out.write(f"note over {src}: {msg}\n")
            else:
                out.write(f"{src} -> {dst}: {msg}\n")

        out.write("@enduml\n")

    print(f"✅ PlantUML diagram written to {output_path}")
"""
def write_plantuml(events, output_path):
    with open(output_path, "w") as out:
        out.write("@startuml\n")
        out.write("title Paxos Single-Decree Sequence\n")
        for i in range(1, 6):
            out.write(f"participant Node{i}\n")
        out.write("\n")

        for ts, src, dst, msg in events:
            label = f"{msg}\\n[{ts}]"
            if src == dst:
                out.write(f"note over {src}: {label}\n")
            else:
                out.write(f"{src} -> {dst}: {label}\n")

        out.write("@enduml\n")

    print(f"✅ PlantUML diagram written to {output_path}")
def write_mermaid(events, output_path):
    with open(output_path, "w") as out:
        out.write("sequenceDiagram\n")
        for src, dst, msg in events:
            if msg == "BECAME LEADER":
                out.write(f"Note over Node{src}: Became Leader\n")
            else:
                out.write(f"Node{src}->>Node{dst}: {msg}\n")
    print(f"✅ Mermaid diagram written to {output_path}")


def main():
    parser = argparse.ArgumentParser(
        description="Generate Paxos sequence diagrams (PlantUML or Mermaid) from log files."
    )
    # parser.add_argument(
    #     "logfile",
    #     help="Path to the Paxos log file (e.g. logs/paxos.log)"
    # )
    parser.add_argument(
        "-f", "--format",
        choices=["plantuml", "mermaid"],
        default="plantuml",
        help="Output format (default: plantuml)"
    )
    parser.add_argument(
        "-o", "--output-dir",
        default=".",
        help="Output directory (default: current directory)"
    )

    args = parser.parse_args()

    # logfiles = [os.path.join("logs", f) for f in os.listdir("logs") if f.startswith("node_") and f.endswith(".log")]
    events = parse_logs_json("logs")
    # Sort by timestamp
    events.sort(key=lambda x: x[0] or "")

    os.makedirs(args.output_dir, exist_ok=True)

    if args.format == "plantuml":
        output_path = os.path.join(args.output_dir, "paxos_sequence.puml")
        write_plantuml(events, output_path)
    else:
        output_path = os.path.join(args.output_dir, "paxos_sequence.mmd")
        write_mermaid(events, output_path)


if __name__ == "__main__":
    main()

