#!/usr/bin/env python3
import subprocess

NUM_NODES = 44
BRIDGE_NAME = "br0"

def run(cmd):
    subprocess.run(cmd, shell=True, check=False)

# Delete namespaces
for i in range(NUM_NODES):
    ns = f"node{i}"
    run(f"sudo ip netns del {ns}")

# Delete veths (host side)
for i in range(NUM_NODES):
    veth_br = f"veth{i}-br"
    run(f"sudo ip link del {veth_br}")

# Delete bridge if exists
run(f"sudo ip link set {BRIDGE_NAME} down")
run(f"sudo ip link del {BRIDGE_NAME}")

print("Cleared previous network namespaces, veths, and bridge.")

