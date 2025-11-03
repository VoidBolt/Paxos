# paxos_manager.py
"""
Paxos manager: run multiple in-process PaxosNode instances (from paxos_async.py)
and provide a simple CLI to propose values, crash/heal nodes, and inspect state.

Usage:
    python paxos_manager.py --n 5 --base-port 9001

This expects paxos_async.py to be importable from the same directory and that
it exposes PaxosNode and send_message functions.
"""
import logging
import traceback
import argparse
import asyncio
# Allows the repl-line to stay at the bottom while async processes are writing to stdout
from prompt_toolkit import PromptSession
from prompt_toolkit.patch_stdout import patch_stdout

# Import the PaxosNode class and send_message from paxos_async.py in same folder.
# paxos_async must be on PYTHONPATH; keep the manager next to it.
# import paxos_async as paxos_mod
from paxos_async import wait_for_nodes_ready, print_state, crash_node, heal_node, start_nodes, stop_nodes
from paxos_node import propose_to, CONSOLE_LOG_LEVEL

async def repl(nodes):
    # Wait until all nodes are confirmed ready before allowing interaction
    await wait_for_nodes_ready(nodes)

    print("Manager commands: propose <node_id> <value> | state [node_id] | crash <id> | heal <id> | stop | help")

    session = PromptSession()

    # loop = asyncio.get_event_loop()

    with patch_stdout():
        while True:
            try:
                line = await session.prompt_async("> ")
            except (EOFError, KeyboardInterrupt):
                print("\nExiting REPL...")
                break

            if not line:
                continue

            parts = line.strip().split(maxsplit=2)
            cmd = parts[0]

            try:
                if cmd == "help":
                    print("Commands: propose <node_id> <value> | state [node_id] | crash <id> | heal <id> | stop")
                elif cmd == "state":
                    if len(parts) == 2:
                        print_state(nodes, int(parts[1]))
                    else:
                        print_state(nodes)
                elif cmd == "propose":
                    if len(parts) < 3:
                        print("usage: propose <node_id> <value>")
                    else:
                        nid = int(parts[1])
                        val = parts[2]
                        node = nodes.get(nid)
                        if not node:
                            print("unknown node", node)
                            continue
                        await propose_to(node, val)
                elif cmd == "crash":
                    await crash_node(nodes, int(parts[1]))
                elif cmd == "heal":
                    await heal_node(nodes, int(parts[1]))
                elif cmd == "stop":
                    print("stopping nodes...")
                    await stop_nodes(nodes)
                    break
                else:
                    print("unknown command, try help")
            except Exception as e:
                print(f"Error in paxos_manager: {type(e).__name__}: {e}")
                traceback.print_exc()

            await asyncio.sleep(0.1)
async def main(n, base_port, strategy):
    nodes = await start_nodes(n, base_port, strategy, CONSOLE_LOG_LEVEL)
    try:
        await repl(nodes)
    finally:
        await stop_nodes(nodes)

if __name__ == '__main__':
    p = argparse.ArgumentParser()
    p.add_argument('--n', type=int, default=3, help="Number of Paxos nodes")
    p.add_argument('--base-port', type=int, default=9001, help="Base port for nodes")
    p.add_argument('--strategy', type=str, default='single', choices=['single', 'multi'])
    p.add_argument('--debug', action='store_true', help="Enable debug logging")
    args = p.parse_args()
    try:
        # pass strategy to node start
        asyncio.run(main(args.n, args.base_port, args.strategy))
    except KeyboardInterrupt:
        print("exited")
