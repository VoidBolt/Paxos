import re
import argparse
import os
import json
# Example timestamp regex: [2025-10-20 16:18:14,925]
TIMESTAMP_RE = re.compile(r"\[(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2},\d+)\]")
NODE_MSG_RE = re.compile(
    r"\[Node\s+(\d+)\s*(?:->\s*Node\s*(\d+))?\s*\]",
    re.IGNORECASE
)
TYPE_RE = re.compile(r"type\(([^)]+)\)")
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
    """
    Parse one node JSON log and return list of (ts, src, dst, msg)
    """
    events = []

    with open(logfile) as f:
        for line in f:
            try:
                rec = json.loads(line)
            except json.JSONDecodeError:
                continue

            ts = rec.get("ts")
            msg = rec.get("msg", "")

            # 1) Detect NodeX or NodeX -> NodeY
            m = NODE_MSG_RE.search(msg)
            if m:
                src_id = m.group(1)
                dst_id = m.group(2)
            else:
                continue  # not a network/logical event; skip

            src = f"Node{src_id}"
            dst = f"Node{dst_id}" if dst_id else src  # self-msg or no dst → note over

            # 2) Extract message type if available: type(PROMISE)
            t = TYPE_RE.search(msg)
            mtype = t.group(1) if t else ""

            # 3) Try to extract slot/value/pid from msg or extra
            extra = rec.get("extra", {}).get("extra_data", {})
            pid = extra.get("proposal_id") or extra.get("pid")
            slot = extra.get("slot")
            value = extra.get("value")

            # Build readable label
            label = mtype
            if value:
                label += f" value={value}"
            if slot:
                label += f" slot={slot}"
            if pid:
                label += f" pid={pid}"

            label = label.strip() or msg  # fallback to whole msg

            events.append((ts, src, dst, label))

    return events


def parse_logs_json(logdir):
    """
    Load all node_*.log JSON logs and merge + sort
    """
    all_events = []
    for fname in os.listdir(logdir):
        if fname.startswith("node_") and fname.endswith(".log"):
            path = os.path.join(logdir, fname)
            all_events.extend(parse_single_log_json(path))

    # Sort by timestamp string (ISO8601 sorted correctly alphabetically)
    all_events.sort(key=lambda x: x[0])
    return all_events

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
        out.write("title Paxos Message Sequence\n")

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

