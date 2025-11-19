"""
paxos_async.py
"""
# from rich import print  # optional, adds color to terminal output
from datetime import datetime
import asyncio
import argparse
from paxos_node import NodeState, PaxosNode, send_message
from paxos_logger import PaxosLogger
import logging
import pathlib

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
        print(f"  paxos_in_progess={getattr(node, "paxos_in_progress", False)}")
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
    print(nodes.values())
    input("Wait...")
    await asyncio.gather(*(node["node"].ready_event.wait() for node in nodes.values()))
    # Flush logs to ensure clean console output before REPL
    for handler in logging.root.handlers:
        handler.flush()
    print("\nAll nodes are ready. Starting REPL...\n")

async def main_loop(args):
    peers = {}
    if args.peers:
        for entry in args.peers.split(','):
            if not entry.strip():
                continue
            nid_s, port_s = entry.split(':')
            nid = int(nid_s)
            peers[nid] = ('127.0.0.1', int(port_s))

    storage_path = f'paxos_manager_workspace/paxos_node_{args.id}.db'
    node = PaxosNode(args.id, '127.0.0.1', args.port, peers, storage_path)
    await node.start()

    print("Commands: propose <value> | state | exit")
    loop = asyncio.get_event_loop()

    while True:
        line = await loop.run_in_executor(None, input, "> ")
        if not line:
            continue
        parts = line.strip().split(maxsplit=1)
        cmd = parts[0]

        if cmd == 'exit':
            break

        elif cmd == 'state':
            print(f"Node {args.id}: running={node.running} leader={node.leader_id}")
            # print(f"  promised_id: {node.storage.promised_id}")
            
            accepted = node.storage.all_accepted()
            if not accepted:
                print("  No slots have reached consensus yet.")
            else:
                print("  Slots with consensus:")
                for slot, (aid, val) in sorted(accepted.items()):
                    print(f"    slot {slot}: accepted_id={aid}, accepted_value={val}")

        elif cmd == 'propose' and len(parts) == 1:
            print("Usage: propose <value>")
        elif cmd == 'propose' and len(parts) == 2:
            value = parts[1]
            # send propose message to local node (will forward to leader if not leader)
            reply = await send_message('127.0.0.1', args.port, {'type': 'propose', 'value': value})
            print('reply:', reply)
        else:
            print('unknown command')

    await node.stop()

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--id', type=int, required=True)
    parser.add_argument('--port', type=int, required=True)
    parser.add_argument('--peers', type=str, default='')
    args = parser.parse_args()
    try:
        asyncio.run(main_loop(args))
    except KeyboardInterrupt:
        pass

