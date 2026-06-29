import yaml

INVENTORY_FILE = "inventories/inventory_lab.yml"


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


def main():
    with open(INVENTORY_FILE, "r") as f:
        inventory = yaml.safe_load(f)

    result = {}

    walk_group(inventory.get("all", inventory), result)

    for host, node_id in sorted(result.items(), key=lambda x: x[1]):
        print(f"{node_id:>3}  {host}")


if __name__ == "__main__":
    main()
