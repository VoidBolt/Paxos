import argparse
import json
import asyncio
import pathlib
import logging

from paxos_node import PaxosNode
from paxos_logger import PaxosLogger


async def main():
    parser = argparse.ArgumentParser()

    parser.add_argument("--node-id", required=True, type=int)
    parser.add_argument("--config", required=True, type=str)
    parser.add_argument("--loglevel", default="INFO")

    args = parser.parse_args()
    node_id = args.node_id

    # Load cluster config
    with open(args.config, "r") as f:
        config = json.load(f)

    all_nodes = config["nodes"]
    if str(node_id) not in all_nodes:
        raise SystemExit(f"Node ID {node_id} is not defined in config file.")

    my_config = all_nodes[str(node_id)]
    host = my_config["host"]
    port = my_config["port"]

    peers = {
        int(nid): (info["host"], info["port"])
        for nid, info in all_nodes.items()
        if int(nid) != node_id
    }

    # Prepare local workspace
    workspace = pathlib.Path("workspace")
    workspace.mkdir(exist_ok=True)

    db_path = workspace / my_config["storage"]

    # Create logger for this node
    logger = PaxosLogger(0, node_id, str(workspace / "logs"), args.loglevel)

    # Instantiate Paxos node
    node = PaxosNode(
        node_id=node_id,
        host=host,
        port=port,
        peers=peers,
        storage_path=str(db_path),
        strategy=config.get("strategy", "basic"),
        logger=logger,
        node_count=len(all_nodes),
    )

    # Start node and wait forever
    await node.start()

if __name__ == "__main__":
    asyncio.run(main())

