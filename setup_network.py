#!/usr/bin/env python3
import subprocess

NUM_NODES = 44
SUBNET = "10.10.0."
BRIDGE_NAME = "br0"

def run(cmd):
    try:
        subprocess.run(cmd, shell=True, check=True)
    except subprocess.CalledProcessError:
        pass

def namespace_exists(ns):
    output = subprocess.run("ip netns list", shell=True, capture_output=True, text=True)
    return ns in (output.stdout.splitlines() if output.stdout else [])

def interface_exists(iface):
    output = subprocess.run("ip link show", shell=True, capture_output=True, text=True)
    return iface in (line.split(":")[1].strip() for line in output.stdout.splitlines() if ":" in line)

def create_bridge():
    if not interface_exists(BRIDGE_NAME):
        print(f"Creating bridge {BRIDGE_NAME}")
        run(f"sudo ip link add name {BRIDGE_NAME} type bridge")
        run(f"sudo ip link set {BRIDGE_NAME} up")
    else:
        print(f"Bridge {BRIDGE_NAME} already exists")

def setup_node(i):
    ns = f"node{i}"
    veth_ns = f"veth{i}"
    veth_br = f"veth{i}-br"
    ip_addr = f"{SUBNET}{i}/24"

    # Create namespace if missing
    if not namespace_exists(ns):
        print(f"Creating namespace {ns}")
        run(f"sudo ip netns add {ns}")

    # Create veth pair
    if not interface_exists(veth_ns) and not interface_exists(veth_br):
        print(f"Creating veth pair {veth_ns} <-> {veth_br}")
        run(f"sudo ip link add {veth_ns} type veth peer name {veth_br}")
        run(f"sudo ip link set {veth_ns} netns {ns}")
    else:
        print(f"Veth pair {veth_ns} / {veth_br} already exists")

    # Assign IP and bring up
    run(f"sudo ip netns exec {ns} ip addr flush dev {veth_ns}")
    run(f"sudo ip netns exec {ns} ip addr add {ip_addr} dev {veth_ns}")
    run(f"sudo ip netns exec {ns} ip link set {veth_ns} up")
    run(f"sudo ip netns exec {ns} ip link set lo up")
    run(f"sudo ip link set {veth_br} up")
    run(f"sudo ip link set {veth_br} master {BRIDGE_NAME}")

def test_connectivity():
    print("\nTesting connectivity (first 5 nodes for brevity)...")
    for i in range(0, min(NUM_NODES, 5)):
        ns = f"node{i}"
        for j in range(0, min(NUM_NODES, 5)):
            if i != j:
                ip = f"{SUBNET}{j}"
                print(f"{ns} -> {ip}")
                run(f"sudo ip netns exec {ns} ping -c 1 -W 1 {ip}")

def main():
    create_bridge()
    for i in range(NUM_NODES):
        setup_node(i)
    test_connectivity()
    print("\nNetwork setup complete for nodes 0 to 43.")

if __name__ == "__main__":
    main()
