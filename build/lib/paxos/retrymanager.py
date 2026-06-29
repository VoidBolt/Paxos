import asyncio
import random
import struct
import logging
import json
from contextlib import suppress

from typing import Awaitable, Callable
from paxos.proto.paxos_pb2 import PaxosMessage

NETWORK_LOG_LEVEL = logging.CRITICAL
network_logger = logging.getLogger("network")
network_logger.setLevel(NETWORK_LOG_LEVEL)
# Optional: attach handler if not configured elsewhere
if not network_logger.handlers:
    handler = logging.StreamHandler()
    formatter = logging.Formatter("[%(asctime)s] [NETWORK] %(levelname)s: %(message)s")
    handler.setFormatter(formatter)
    network_logger.addHandler(handler)
    network_logger.propagate = False  # prevent duplicate output via root logger

# -----------------
# Utility functions
# -----------------

MSG_HDR = struct.Struct('!I')  # 4-byte length prefix

async def send_message(host, port, message, timeout=2.0, node=None):
    """Send a message (supports Protobuf or dict) and await response."""
    try:
        reader, writer = await asyncio.wait_for(
            asyncio.open_connection(host, port), timeout=timeout
        )
        try:
            # --- Serialize ---
            if hasattr(message, "SerializeToString"):  # Protobuf object
                data = message.SerializeToString()
                is_proto = True
            else:  # fallback to JSON
                data = json.dumps(message).encode()
                is_proto = False

            writer.write(MSG_HDR.pack(len(data)))
            writer.write(data)
            await writer.drain()

            # --- Receive response ---
            hdr = await asyncio.wait_for(reader.readexactly(MSG_HDR.size), timeout=timeout)
            (n,) = MSG_HDR.unpack(hdr)
            body = await asyncio.wait_for(reader.readexactly(n), timeout=timeout)

            if is_proto:
                reply = PaxosMessage.FromString(body)
            else:
                reply = json.loads(body.decode())

            if node:
                network_logger.debug(
                    f"[Node {reply.sender_id if hasattr(reply,'sender_id') else '?'} -> "
                    f"Node {node.node_id if node else '?'}]: "
                    f"RECV type={getattr(reply, 'type', '?')}"
                )
            return reply
        finally:
            with suppress(Exception):
                writer.close()
                await writer.wait_closed()

    except (asyncio.TimeoutError, ConnectionRefusedError, ConnectionResetError, OSError) as e:
        network_logger.warning(f"[send_message] Failed to reach {host}:{port}: {e}")
        return None
    except Exception as e:
        network_logger.exception(f"[send_message] Unexpected: {e}")
        return None

"""
async def send_message(
    host: str,
    port: int,
    message: dict,
    timeout: float = 2.0,
    node=None,
    max_retries: int = 5,
    base_delay: float = 1.0,
    max_delay: float = 30.0,
) -> Optional[dict]:
    msg_id = message.get("msg_id") or str(uuid.uuid4())
    message["msg_id"] = msg_id

    reply = await send_message_once(host, port, message, timeout=timeout, node=node)
    if reply is not None:
        return reply

    # Schedule async background retries
    async def retry_task():
        for attempt in range(1, max_retries + 1):
            delay = min(max_delay, base_delay * 2 ** (attempt - 1))
            delay *= random.uniform(0.5, 1.5)
            print(
                f"[send_message] Retrying {host}:{port} in {delay:.2f}s (attempt {attempt}/{max_retries})"
            )
            network_logger.info(
            f"[send_message] Retrying {host}:{port} in {delay:.2f}s (attempt {attempt}/{max_retries})"
            )
            await asyncio.sleep(delay)
            result = await send_message_once(host, port, message, timeout=timeout, node=node)
            if result is not None:
                network_logger.info(f"[send_message] Retry succeeded to {host}:{port} (msg_id={msg_id})")
                return
        network_logger.error(f"[send_message] Giving up on {host}:{port} after {max_retries} retries.")

    # Don't block the caller — fire off the retries in background
    asyncio.create_task(retry_task())
    return None
"""
class RetryManager:
    """Manages queued and on-demand retries for Paxos messages."""
    def __init__(self):
        self.queue = asyncio.Queue()
        self.running = True
        self.worker_task = asyncio.create_task(self._worker())

    async def stop(self):
        """Gracefully stop the retry worker."""
        self.running = False
        await self.queue.put(None)
        await self.worker_task

    async def schedule_retry(
        self,
        host,
        port,
        message,
        node,
        attempt=1,
        max_retries=5,
        base_delay=1.0,
        max_delay=30.0,
        timeout=2.0,
    ):
        """Queue-based retry: adds a message to be retried later by the worker."""
        await self.queue.put((host, port, message, node, attempt, max_retries, base_delay, max_delay, timeout))

    async def _worker(self):
        """Background worker that processes queued retry tasks."""
        while self.running:
            item = await self.queue.get()
            if item is None:  # shutdown
                break

            host, port, message, node, attempt, max_retries, base_delay, max_delay, timeout = item
            delay = min(max_delay, base_delay * 2 ** (attempt - 1))
            delay *= random.uniform(0.5, 1.5)
            await asyncio.sleep(delay)

            result = await send_message_once(host, port, message, timeout, node)
            if result is None and attempt < max_retries:
                await self.schedule_retry(
                    host, port, message, node, attempt + 1, max_retries, base_delay, max_delay, timeout
                )
            # else: success or max attempts reached

    # 🔁 NEW: On-demand retry wrapper
    async def run(
        self,
        func: Callable[[], Awaitable],
        retries: int = 3,
        base_delay: float = 0.5,
        max_delay: float = 10.0,
        jitter: float = 0.3,
    ):
        """
        Run an async function with exponential backoff and jitter.
        Returns the result if successful, or None if all retries fail.
        """
        for attempt in range(1, retries + 1):
            try:
                result = await func()
                if result is not None:
                    return result
            except Exception as e:
                # optional: log if needed
                print(f"[RetryManager.run] attempt {attempt}/{retries} failed: {e}")

            if attempt < retries:
                delay = min(max_delay, base_delay * 2 ** (attempt - 1))
                delay *= random.uniform(1 - jitter, 1 + jitter)
                await asyncio.sleep(delay)
        return None

