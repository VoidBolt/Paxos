import asyncio
import argparse

async def send(node_id: int, cmd: str):
    host = "127.0.0.1"
    port = 10000 + node_id   # MUST match node.control_port

    reader, writer = await asyncio.open_connection(host, port)

    writer.write((cmd + "\n").encode())
    await writer.drain()

    response = await reader.readline()
    print(response.decode().strip())

    writer.close()
    await writer.wait_closed()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("node_id", type=int)
    parser.add_argument("cmd", type=str, nargs=argparse.REMAINDER)

    args = parser.parse_args()

    cmd = " ".join(args.cmd)

    asyncio.run(send(args.node_id, cmd))


if __name__ == "__main__":
    main()
