import netifaces
from unittest.mock import patch
from paxos.paxos_async import get_local_ips_ns


def test_returns_ipv4_addresses():
    print("Testing Discovery...")
    with patch("paxos_async.netifaces.ifaddresses") as mock:
        print("Patch paxos_async.netifaces.ifaddresses...")
        mock.return_value = {
            netifaces.AF_INET: [
                {"addr": "192.168.1.10"},
                {"addr": "10.0.0.5"},
            ]
        }
        for id in range(44):
            # id = 1
            result = get_local_ips_ns(id) # veth1 is old, id now
            assertion = result == [f"10.10.0.{id}"]
            print(f"id={id}: {result}", assertion)
            assert assertion
if __name__ == "__main__":
    test_returns_ipv4_addresses()
