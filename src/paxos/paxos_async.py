"""
paxos_async.py
"""
import sys, pathlib
sys.path.append(str(pathlib.Path(__file__).parent))
# from rich import print  # optional, adds color to terminal output
from datetime import datetime
import asyncio
import argparse
from paxos.paxos_node import PaxosNode, propose_to
from paxos.paxos_logger import PaxosLogger
import logging
import pathlib
import json
import socket
import platform
import subprocess

import subprocess
import re

# auto discover own ip in own namespace, redundant if config driven but convenient
# import netifaces

def get_local_ips_ns(node_id):
    try:
        """sudo ip netns exec node2 ip addr show veth2"""
        """sudo ip addr show veth[id]"""
        result = subprocess.run(
            ["sudo", "ip","netns", "exec", f"node{node_id}", "ip", "addr", "show", f"veth{node_id}"],
            capture_output=True,
            text=True,
            check=False
        )

        if result.returncode != 0:
            return []

        output = result.stdout

        # Extract IPv4 addresses
        ips = re.findall(r"inet (\d+\.\d+\.\d+\.\d+)/", output)

        return ips

    except Exception:
        return []

def load_cluster_config(path):
    with open(path, "r") as f:
        cfg = json.load(f)

    nodes = cfg["nodes"]
    return {n["id"]: (n["host"], n["port"]) for n in nodes}

# -----------------
# CLI and example
# -----------------
async def start_nodes(n: int, base_port: int, strategy: str, loglevel=logging.DEBUG):
    """
    Start N Paxos nodes concurrently, ensuring all servers are ready
    before returning.
    """
    nodes = {}
    peers_map = {i: ('127.0.0.1', base_port + (i - 1)) for i in range(1, n + 1)}

    # Prepare workspace
    workspace = pathlib.Path('./paxos_manager_workspace')
    workspace.mkdir(exist_ok=True)

    # Clear old dbs
    for f in workspace.glob('paxos_node_*.db'):
        try:
            f.unlink()
        except Exception as e:
            logging.warning(f"Could not remove old db {f}: {e}")

    # Instantiate node objects
    for i in range(1, n + 1):
        port = base_port + (i - 1)
        peers = {nid: addr for nid, addr in peers_map.items() if nid != i}
        db_path = str(workspace / f"paxos_node_{i}.db")

        node = PaxosNode(
            node_id=i,
            logger=PaxosLogger(0, i, "logs", loglevel),
            node_count=n+1,
            host='127.0.0.1',
            port=port,
            peers=peers,
            storage_path=db_path,
            strategy=strategy,
        )

        # ✅ Ensure each node has a readiness event
        # if not hasattr(node, "ready_event"):
        #    node.ready_event = asyncio.Event()

        nodes[i] = {
            'node': node,
            'task': None,
            'running': False,
            'port': port,
            'db': db_path,
        }

    # Log peer setup
    for nid, info in nodes.items():
        print(f"Node {nid} peers: {info['node'].peers}")

    # Start all nodes concurrently
    for i, info in nodes.items():
        node: PaxosNode = info['node']
        info['task'] = asyncio.create_task(node.start())
        info['running'] = True

    # ✅ Wait for all nodes to signal readiness
    await asyncio.gather(*(info['node'].ready_event.wait() for info in nodes.values()))

    # Flush any buffered logs before proceeding
    for handler in logging.root.handlers:
        handler.flush()

    print("\n✅ All nodes started and ready.\n")
    return nodes


async def stop_nodes(nodes):
    for info in nodes.values():
        node: PaxosNode = info['node']
        try:
            await node.stop()
        except Exception:
            pass
        info['running'] = False
        # cancel any background task associated
        t = info.get('task')
        if t:
            t.cancel()

def print_state(nodes: dict, node_id: int | None = None):
    """
    Plain-text version: prints the current Paxos cluster state with readable formatting,
    including peer_status info (how each node perceives the others' state).
    """
    print(f"\n=== Paxos Cluster State @ {datetime.now().strftime('%H:%M:%S')} ===")

    def _format_slot(node, slot):
        accepted = node.storage.get_accepted(slot)
        decided = getattr(node.storage, "get_decision", lambda s: None)(slot)
        accepted_id, accepted_val = accepted if accepted else (None, None)
        parts = []
        if accepted_id:
            parts.append(f"id={accepted_id}")
        if accepted_val:
            parts.append(f"val={accepted_val}")
        if decided:
            parts.append(f"✔ decided={decided}")
        return f"{slot}: " + ", ".join(parts) if parts else f"{slot}: (empty)"

    def _format_peer_status(node):
        """Return a concise string describing this node's view of its peers."""
        peer_status = getattr(node, "peer_state", {})
        if not peer_status:
            return "no peer status info"

        parts = []
        for pid, status in sorted(peer_status.items()):
            print(f"Peer_Status: {status}")
            # Handle cases where status is a dict or an enum
            if isinstance(status, dict):
                # try to extract state field if present
                state = status.get("state")
                state_name = state.name if hasattr(state, "name") else str(state)
                parts.append(f"{pid}={state_name}")
            elif hasattr(status, "name"):
                parts.append(f"{pid}={status.name}")
            else:
                parts.append(f"{pid}={status}")
        return ", ".join(parts)

    # === Single node view ===
    if node_id:
        info = nodes.get(node_id)
        if not info:
            print(f"Unknown node {node_id}")
            return

        node = info["node"]
        print(f"Node {node.node_id}")
        print(f"  role={node.role.name}, state={node.state.name}, running={info['running']}, leader={node.leader_id}")
        # print(f"  consensus_reached={getattr(node.strategy, 'consensus_reached', False)}")
        print(f"  paxos_in_progess={getattr(node, 'paxos_in_progress', False)}")
        print(f"  peer_status: {_format_peer_status(node)}")

        slots = node.storage.all_slots() if hasattr(node.storage, "all_slots") else []
        if not slots:
            print("  no slots yet")
        else:
            for slot in sorted(slots):
                print("   ", _format_slot(node, slot))
        return

    # === Cluster-wide summary ===
    for nid, info in sorted(nodes.items()):
        node = info["node"]
        print(f"Node {node.node_id}")
        print(f"  role={node.role.name}, state={node.state.name}, running={info['running']}, leader={node.leader_id}")
        print(f"  consensus_reached={getattr(node, 'consensus_reached', False)}")
        print(f"  peer_status: {_format_peer_status(node)}")

        slots = node.storage.all_slots() if hasattr(node.storage, "all_slots") else []
        if not slots:
            print("  no slots yet")
        else:
            for slot in sorted(slots):
                print("   ", _format_slot(node, slot))
        print()
"""
def print_state(nodes, node_id=None):
    if node_id:
        info = nodes.get(node_id)
        if not info:
            print("unknown node", node_id)
            return
        node = info['node']
        print(f"Node {node.node_id}: running={info['running']} leader={node.leader_id}")
        slots = node.storage.all_slots()
        if not slots:
            print("  no slots yet")
        else:
            for slot in sorted(slots):
                accepted = node.storage.get_accepted(slot)
                print(f"  slot {slot}: accepted_id={accepted[0]}, accepted_value={accepted[1]}")
    else:
        for nid, info in sorted(nodes.items()):
            node = info['node']
            slots = node.storage.all_slots()
            if not slots:
                slot_info = "no slots yet"
            else:
                slot_info = ", ".join(f"{s}:{node.storage.get_accepted(s)[1]}" for s in sorted(slots))
            print(f"Node {nid}: running={info['running']} leader={node.leader_id} accepted_values=[{slot_info}]")
"""
async def crash_node(nodes, node_id):
    info = nodes.get(node_id)
    if not info:
        print("unknown node", node_id)
        return
    node: PaxosNode = info['node']
    # stopping server and tasks
    await node.stop()
    info['running'] = False
    print(f"Node {node_id} crashed (stopped).")

async def heal_node(nodes, node_id):
    info = nodes.get(node_id)
    if not info:
        print("unknown node", node_id)
        return
    if info['running']:
        print(f"Node {node_id} already running.")
        return
    node: PaxosNode = info['node']
    info['task'] = asyncio.create_task(node.start())
    info['running'] = True
    # allow election/heartbeat to run
    await asyncio.sleep(0.4)
    print(f"Node {node_id} healed (restarted).")

async def wait_for_nodes_ready(nodes):
    """Wait for all nodes' ready_event flags to be set."""
    # print(nodes.values())
    # input("Wait...")
    await asyncio.gather(*(node["node"].ready_event.wait() for node in nodes.values()))
    # Flush logs to ensure clean console output before REPL
    for handler in logging.root.handlers:
        handler.flush()
    print("\nAll nodes are ready. Starting REPL...\n")

async def main_loop(args, loglevel=logging.DEBUG):
    """
    Start a single Paxos node in distributed mode using a cluster config JSON file.
    The node automatically discovers its peers from the config.
    """
    # --- Load cluster config ---
    with open(args.config, "r") as f:
        cfg = json.load(f)

    # Build a dict of node_id -> (host, port)
    nodes = cfg["nodes"]
    print(nodes.items())
    all_nodes = {
        int(node_id): (node_info["host"], node_info["port"])
        for node_id, node_info in nodes.items()
    }
    print("All_Nodes: ", all_nodes)
    # Determine my host and port
    #
    print(f"Finding host, port of specified node_id: {args.node_id}")
    node_id = int(args.node_id)
    if node_id not in all_nodes:
        raise ValueError(f"Node ID {args.node_id} not found in cluster config")

    my_host, my_port = all_nodes[node_id]
    # Build peers dict (all other nodes)
    peers = {nid: addr for nid, addr in all_nodes.items() if nid != node_id}

    workspace = pathlib.Path("paxos_manager_workspace")
    workspace.mkdir(exist_ok=True)

    storage_path = workspace / f"paxos_node_{args.node_id}.db"
    # storage_path = f'paxos_manager_workspace/paxos_node_{args.node_id}.db'
    storage_path=str(storage_path)
    node = PaxosNode(
        node_id, 
        logger=PaxosLogger(0, node_id, "logs", loglevel), 
        node_count=len(all_nodes), 
        host=my_host,# '0.0.0.0', 
        port=my_port, 
        peers=peers, 
        storage_path=storage_path, 
        strategy="multi"
    )

    await node.start()
    print(f"Node {args.node_id} started at {my_host}:{my_port}, peers: {peers}")

    # --- REPL ---
    loop = asyncio.get_event_loop()
    print("Commands: propose <value> <slot> | state | exit")

    while True:
        line = await loop.run_in_executor(None, input, "> ")
        if not line:
            continue
        parts = line.strip().split()
        cmd = parts[0]

        if cmd == 'exit':
            break

        elif cmd == 'state':
            print(f"Node {args.node_id}: running={node.running} leader={node.leader_id}")
            print(f"peers: {node.peers}")
            print(f"peer_state: {node.peer_state}")
            # print(f"  promised_id: {node.storage.promised_id}")
            
            accepted = node.storage.all_accepted()
            if not accepted:
                print("  No slots have reached consensus yet.")
            else:
                print("  Slots with consensus:")
                for slot, (aid, val) in sorted(accepted.items()):
                    print(f"    slot {slot}: accepted_id={aid}, accepted_value={val}")

        elif cmd == 'propose' and len(parts) == 1:
            print("Usage: propose <value> <slot>")
        elif cmd == 'propose':
            if len(parts) != 3:
                print("Usage: propose <value> <slot>")
                continue

            value = parts[1]
            slot = int(parts[2])

            print(f"Proposing value={value} for slot={slot} to peers: {peers}")
            await propose_to({"node": node}, value, slot, use_worker=True)
        else:
            print('unknown command')

    await node.stop()

def get_primary_ip():
    """Get the primary non-loopback IPv4 of the machine without subprocess."""
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        # Doesn't need to be reachable — no packets are actually sent.
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
    except Exception:
        ip = None
    finally:
        s.close()
    return ip

def get_local_ips(allow_subprocess=True):
    ips = set()

    # --- Method 1: Primary IP via UDP trick (best) ---
    primary_ip = get_primary_ip()
    if primary_ip and not primary_ip.startswith("127."):
        ips.add(primary_ip)

    # If subprocess allowed, collect all interface IPs too
    if allow_subprocess:
        try:
            system = platform.system().lower()

            if "windows" in system:
                out = subprocess.check_output("ipconfig", text=True)
                for line in out.splitlines():
                    line = line.strip()
                    if "IPv4 Address" in line or line.startswith("IPv4"):
                        ip = line.split(":")[-1].strip()
                        if not ip.startswith("127."):
                            ips.add(ip)

            else:
                # hostname -I
                try:
                    out = subprocess.check_output("hostname --i", shell=True, text=True)
                    for ip in out.split():
                        if not ip.startswith("127."):
                            ips.add(ip)
                except:
                    pass

                # ip addr
                out = subprocess.check_output("ip addr", text=True)
                for line in out.splitlines():
                    line = line.strip()
                    if line.startswith("inet ") and "127.0.0.1" not in line:
                        ip = line.split()[1].split("/")[0]
                        ips.add(ip)

        except Exception:
            pass

    return list(ips)


def detect_id_from_config(config_path, local_ips):
    """Return the node ID that matches one of the local IP addresses."""
    with open(config_path, "r") as f:
        config = json.load(f)

    for node_id, node_info in config["nodes"].items():
        if node_info["host"] in local_ips:
            return int(node_id)

    return None

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    subprocess_allowed = True
    parser.add_argument('--config', type=str, default="cluster_config.json")
    parser.add_argument('--allow-subprocess', action='store_true',
                        help="Allow subprocess IP scanning")
    # parser.add_argument("--veth", type=str, default="veth1")
    parser.add_argument("--node_id", type=str, default="0")
    """
    if not subprocess_allowed:
        parser.add_argument('--id', type=int, required=True)
    else:
        import subprocess
        import platform       
        def get_ip_address():
            # Return primary IP address using subprocess calls.
            try:
                system = platform.system().lower()

                if "windows" in system:
                    # Windows: use ipconfig
                    output = subprocess.check_output("ipconfig", text=True)
                    for line in output.splitlines():
                        line = line.strip()
                        if line.startswith("IPv4 Address") or "IPv4" in line:
                            ip = line.split(":")[-1].strip()
                            return ip

                else:
                    # Linux / macOS: try hostname -I first
                    try:
                        ip = subprocess.check_output("hostname -I", shell=True, text=True).strip()
                        if ip:
                            return ip.split()[0]
                    except:
                        pass

                    # Fallback: ip addr
                    output = subprocess.check_output("ip addr", text=True)
                    for line in output.splitlines():
                        line = line.strip()
                        if line.startswith("inet ") and "127.0.0.1" not in line:
                            ip = line.split()[1].split("/")[0]
                            return ip

            except Exception as e:
                return None

            return None
    # parser.add_argument('--port', type=int, required=True)
    # parser.add_argument('--peers', type=str, default='')
    parser.add_argument('--config', type=str, default="cluster_config.json")
    """
    args = parser.parse_args()
    # print("Detect local IPs...")
    # local_ips = get_local_ips(args.veth)
    # print(f"Local IPs: {local_ips}")

    # print("Detect local IPs...")
    # local_ips_ns = get_local_ips_ns(args.node_id)# allow_subprocess=args.allow_subprocess)
    # print(f"Local IPs (ns): {local_ips_ns}")

    # node_id = detect_id_from_config(args.config, local_ips_ns)

    # if node_id is None:
    #     raise RuntimeError(
    #         f"Could not match any local IP {local_ips_ns} with nodes in {args.config}"
    #    )

    # args.id = node_id
    # print(f"Detected node ID: {args.id} (IPs: {local_ips_ns})")
    try:
        asyncio.run(main_loop(args))
    except KeyboardInterrupt:
        pass

