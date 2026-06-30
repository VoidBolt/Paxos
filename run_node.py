import os
import argparse
# import json
import asyncio
import pathlib
# import logging
import yaml
import socket

from paxos.paxos_node import PaxosNode, propose_to
from paxos.paxos_logger import PaxosLogger


def load_yml_config(path):

    def walk_group(group, result):
        if not isinstance(group, dict):
            return

        # collect hosts
        hosts = group.get("hosts", {})
        for host, attrs in hosts.items():
            if isinstance(attrs, dict) and "node_id" in attrs:
                result[host] = attrs["node_id"]

        # recurse into children
        children = group.get("children", {})
        for child in children.values():
            walk_group(child, result)

    with open(path, "r") as f:
        inventory = yaml.safe_load(f)

    result = {}

    walk_group(inventory.get("all", inventory), result)
    nodes = {}

    for host, node_id in sorted(result.items(), key=lambda x: x[1]):
        meta = inventory.get("hosts", {}).get(host, {})  # safe fallback

        hostname = meta.get("ansible_host", host)

        nodes[node_id] = {
            "host": host + ".ris.bht-berlin.de",
            "hostname": hostname,
            "meta": meta,
            "port": 5000 + node_id,
        }
    # print(f"Nodes:\n {nodes}")

    local_identities = {
        socket.getfqdn(),
        socket.gethostname(),
        socket.gethostname().split(".")[0],
    }
    print(f"local_identities: {local_identities}")
    # print(f"Nodes:\n {nodes}")

    my_node_id = None
    identities_list = list(local_identities)

    for nid, info in nodes.items():
        host_name = info["host"].split(".")[0]
        # print(identities_list[0], identities_list[1])
        # print(nid, info)
        for identity in identities_list:
            # print("host_name in identity? -> ", host_name, identity, host_name in identity)
            if host_name.lower() in identity:
                # print(f'Found Identity! -> {info["host"]}')
                my_node_id = nid

    if my_node_id is None:
        print("My_node_id:", my_node_id)
        raise RuntimeError(
            f"Could not identify this node. "
        )

    my_host = nodes[my_node_id]["hostname"]
    my_port = nodes[my_node_id]["port"]

    # Build peers dict (all other nodes)
    peers_unsanitized = {nid: addr for nid, addr in nodes.items() if nid != my_node_id}
    # print(peers_unsanitized)
    # print(peers_unsanitized.items())
    peers = {}
    for nid, peer in peers_unsanitized.items():
        peers[nid] = (peer["host"], peer["port"])
        # print(f"Node {my_node_id} check to Node {nid}, peer: {peer}!")
    # print(peers)
    # input("Look at peers, it should be host -> port, if not remap new data structure...")
    return my_host, my_port, my_node_id, peers, nodes

async def main():
    parser = argparse.ArgumentParser()

    # parser.add_argument("--node-id", required=True, type=int)
    # parser.add_argument("--config", required=True, type=str)
    parser.add_argument('--inventory', type=str, required=True)
    parser.add_argument("--loglevel", default="INFO")

    args = parser.parse_args()
    # node_id = args.node_id
    """
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
    """

    host, port, node_id, peers, nodes = load_yml_config(args.inventory)
    # Prepare local workspace
    workspace = pathlib.Path("workspace")
    workspace.mkdir(exist_ok=True)

    db_path = os.path.join(workspace, "data")#my_config["storage"])

    # Create logger for this node
    logger = PaxosLogger(0, node_id, os.path.join(workspace,"logs"), args.loglevel)

    # Instantiate Paxos node
    node = PaxosNode(
        node_id=node_id,
        host=host,
        port=port,
        peers=peers,
        storage_path=str(db_path),
        strategy="basic", # config.get("strategy", "basic"),
        logger=logger,
        node_count=len(nodes),
    )

    # Start node and wait forever
    await node.start()

if __name__ == "__main__":
    asyncio.run(main())

