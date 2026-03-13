import json
from paxos.paxos_async import get_local_ips_ns

def test_local_ip_in_cluster_config():
    # Load cluster configuration
    with open("cluster_subnet.json") as f:
        cluster_config = json.load(f)

    # Extract allowed IPs
    allowed_ips = {
        cluster_config["nodes"][k]["host"]
        for k in cluster_config["nodes"]
    }

    # Call your function (replace veth_name if needed)
    local_ips = get_local_ips_ns(1)

    print(f"Local IPs: {local_ips}")
    print(f"Allowed cluster IPs: {allowed_ips}")

    # Validate membership
    assert any(ip in allowed_ips for ip in local_ips), \
        "No local IP matches cluster configuration"

if __name__ == "__main__":

    test_local_ip_in_cluster_config()

