"""
paxos_async.py

Async Paxos node implementation (single-decree optimization with leader/coordinator),
persistent acceptor state (sqlite), and Bully-style leader election.

Usage (example):

# start node 1
python paxos_async.py --id 1 --port 9001 --peers 2:9002,3:9003
# start node 2
python paxos_async.py --id 2 --port 9002 --peers 1:9001,3:9003
# start node 3
python paxos_async.py --id 3 --port 9003 --peers 1:9001,2:9002

Then use the `propose` command to propose a value via any node's admin HTTP endpoint.

This file is a reference implementation intended for education and testing. It is NOT
production hardened. It focuses on:
 - asyncio-based networking (TCP+JSON per-message)
 - persistent acceptor state stored in sqlite per node
 - a simple Bully-style leader election and heartbeat
 - leader acts as coordinator to run the two-phase Paxos rounds

"""

import argparse
import asyncio
import json
import logging
import os
import sqlite3
import struct
import time
from typing import Dict, Optional, Tuple, List

from strategies.single_decree import SingleDecreePaxos
logging.basicConfig(level=logging.INFO, format="[%(asctime)s] %(message)s")

# -----------------
# Utility functions
# -----------------

MSG_HDR = struct.Struct('!I')  # 4-byte length prefix

async def send_message(host: str, port: int, message: dict, timeout: float = 2.0) -> Optional[dict]:
    """Open a TCP connection, send a JSON message with 4-byte length prefix, and wait for a JSON reply.
    Returns parsed JSON reply or None on error or timeout."""
    try:
        reader, writer = await asyncio.wait_for(asyncio.open_connection(host, port), timeout=timeout)
        data = json.dumps(message).encode()
        writer.write(MSG_HDR.pack(len(data)))
        writer.write(data)
        await writer.drain()

        # read reply
        hdr = await asyncio.wait_for(reader.readexactly(MSG_HDR.size), timeout=timeout)
        (n,) = MSG_HDR.unpack(hdr)
        body = await asyncio.wait_for(reader.readexactly(n), timeout=timeout)
        reply = json.loads(body.decode())
        writer.close()
        try:
            await writer.wait_closed()
        except Exception:
            pass
        return reply
    except Exception as e:
        logging.debug(f"send_message error to {host}:{port} -> {e}")
        return None

# -----------------
# Persistent storage
# -----------------

class AcceptorStorage:
    """Simple sqlite-based storage for acceptor state. File is per-node."""
    def __init__(self, path: str):
        init_needed = not os.path.exists(path)
        self.path = path
        self.conn = sqlite3.connect(path, check_same_thread=False)
        if init_needed:
            self._init_db()

    def _init_db(self):
        cur = self.conn.cursor()
        cur.execute("""
        CREATE TABLE state (
            key TEXT PRIMARY KEY,
            val TEXT
        )
        """)
        # promised_id, accepted_id, accepted_value
        cur.execute("INSERT INTO state (key, val) VALUES ('promised_id', NULL)")
        cur.execute("INSERT INTO state (key, val) VALUES ('accepted_id', NULL)")
        cur.execute("INSERT INTO state (key, val) VALUES ('accepted_value', NULL)")
        self.conn.commit()

    def _get(self, key: str):
        cur = self.conn.cursor()
        cur.execute("SELECT val FROM state WHERE key = ?", (key,))
        row = cur.fetchone()
        if not row:
            return None
        return None if row[0] is None else json.loads(row[0])

    def _set(self, key: str, value):
        cur = self.conn.cursor()
        cur.execute("UPDATE state SET val = ? WHERE key = ?", (None if value is None else json.dumps(value), key))
        self.conn.commit()

    @property
    def promised_id(self):
        return self._get('promised_id')

    @promised_id.setter
    def promised_id(self, v):
        self._set('promised_id', v)

    @property
    def accepted_id(self):
        return self._get('accepted_id')

    @accepted_id.setter
    def accepted_id(self, v):
        self._set('accepted_id', v)

    @property
    def accepted_value(self):
        return self._get('accepted_value')

    @accepted_value.setter
    def accepted_value(self, v):
        self._set('accepted_value', v)

# -----------------
# Paxos Node (async)
# -----------------

class PaxosNode:
    def __init__(self, node_id: int, host: str, port: int, peers: Dict[int, Tuple[str, int]], storage_path: str):
        self.node_id = node_id
        self.host = host
        self.port = port
        self.peers = peers  # dict node_id -> (host, port)

        # persistent acceptor state
        self.storage = AcceptorStorage(storage_path)

        # in-memory leader info
        self.leader_id: Optional[int] = None
        self.leader_last_heartbeat = 0.0
        self.heartbeat_interval = 1.0
        self.heartbeat_timeout = 3.0

        # proposal id generator (monotonic counter)
        self._proposal_counter = 0

        # server
        self.server = None
        self._server_task = None

        # tasks
        self.tasks: List[asyncio.Task] = []

        # for graceful shutdown
        self._stopping = False

    # -----------------
    # proposal id helpers
    # -----------------
    def next_proposal_id(self) -> int:
        self._proposal_counter += 1
        # embed node id in low bits to break ties deterministically
        return (int(time.time() * 1000) << 16) | (self.node_id & 0xffff) | (self._proposal_counter & 0xff)

    # -----------------
    # network server
    # -----------------
    async def start_server(self):
        self.server = await asyncio.start_server(self.handle_connection, self.host, self.port)
        addr = self.server.sockets[0].getsockname()
        logging.info(f"Node {self.node_id} listening on {addr}")
        async with self.server:
            await self.server.serve_forever()

    async def handle_connection(self, reader: asyncio.StreamReader, writer: asyncio.StreamWriter):
        peer = writer.get_extra_info('peername')
        try:
            hdr = await reader.readexactly(MSG_HDR.size)
            (n,) = MSG_HDR.unpack(hdr)
            body = await reader.readexactly(n)
            msg = json.loads(body.decode())

            # dispatch
            reply = await self.dispatch(msg)

            if reply is None:
                # send empty reply
                writer.write(MSG_HDR.pack(0))
            else:
                data = json.dumps(reply).encode()
                writer.write(MSG_HDR.pack(len(data)))
                writer.write(data)
            await writer.drain()
        except Exception as e:
            logging.debug(f"Node {self.node_id} connection error from {peer}: {e}")
        finally:
            try:
                writer.close()
                await writer.wait_closed()
            except Exception:
                pass

    # -----------------
    # message handlers
    # -----------------
    async def dispatch(self, msg: dict) -> Optional[dict]:
        mtype = msg.get('type')
        if mtype == 'prepare':
            return await self.on_prepare(msg)
        elif mtype == 'accept_request':
            return await self.on_accept_request(msg)
        elif mtype == 'learn':
            return await self.on_learn(msg)
        elif mtype == 'heartbeat':
            return await self.on_heartbeat(msg)
        elif mtype == 'election':
            return await self.on_election(msg)
        elif mtype == 'election_ok':
            return await self.on_election_ok(msg)
        elif mtype == 'coordinator':
            return await self.on_coordinator(msg)
        elif mtype == 'propose':
            return await self.on_client_propose(msg)
        else:
            logging.debug(f"Node {self.node_id} unknown message type: {mtype}")
            return {'err': 'unknown'}

    # Acceptor: prepare
    async def on_prepare(self, msg: dict) -> dict:
        proposal_id = msg['proposal_id']
        # check promised id
        promised = self.storage.promised_id
        if promised is None or proposal_id > promised:
            self.storage.promised_id = proposal_id
            logging.debug(f"Node {self.node_id} PROMISE for pid {proposal_id}")
            return {
                'type': 'promise',
                'proposal_id': proposal_id,
                'accepted_id': self.storage.accepted_id,
                'accepted_value': self.storage.accepted_value,
            }
        else:
            logging.debug(f"Node {self.node_id} REJECT prepare pid {proposal_id} (promised {promised})")
            return {'type': 'reject', 'promised_id': promised}

    # Acceptor: accept request
    async def on_accept_request(self, msg: dict) -> dict:
        proposal_id = msg['proposal_id']
        value = msg['value']
        promised = self.storage.promised_id
        if promised is None or proposal_id >= promised:
            self.storage.promised_id = proposal_id
            self.storage.accepted_id = proposal_id
            self.storage.accepted_value = value
            logging.info(f"Node {self.node_id} accepted pid {proposal_id} val {value}")
            return {'type': 'accepted', 'proposal_id': proposal_id}
        else:
            logging.debug(f"Node {self.node_id} REJECT accept pid {proposal_id} (promised {promised})")
            return {'type': 'reject', 'promised_id': promised}

    # Learner: learn broadcast
    async def on_learn(self, msg: dict) -> dict:
        value = msg['value']
        # store as accepted_value (learned)
        if self.storage.accepted_value is None:
            self.storage.accepted_value = value
            logging.info(f"Node {self.node_id} learned value {value} via Learn")
        return {'type': 'ok'}

    # Heartbeat
    async def on_heartbeat(self, msg: dict) -> dict:
        leader = msg.get('leader_id')
        self.leader_id = leader
        self.leader_last_heartbeat = time.time()
        return {'type': 'hb_ack'}

    # Election messages (Bully algorithm)
    async def on_election(self, msg: dict) -> dict:
        sender = msg.get('sender')
        logging.info(f"Node {self.node_id} got ELECTION from {sender}")
        # Reply OK and start own election if higher id
        # send election_ok back
        peer = self.peers.get(sender)
        if peer:
            host, port = peer
            asyncio.create_task(send_message(host, port, {'type': 'election_ok', 'sender': self.node_id}))
        # If my id is higher than sender, I should start election
        if self.node_id > sender:
            asyncio.create_task(self.start_election())
        return {'type': 'election_ack'}

    async def on_election_ok(self, msg: dict) -> dict:
        # someone higher responded; wait for coordinator announcement
        logging.info(f"Node {self.node_id} received ELECTION_OK from {msg.get('sender')}")
        return {'type': 'ok'}

    async def on_coordinator(self, msg: dict) -> dict:
        leader = msg.get('leader_id')
        logging.info(f"Node {self.node_id} sees coordinator {leader}")
        self.leader_id = leader
        self.leader_last_heartbeat = time.time()
        return {'type': 'ok'}

    # Client propose: if I'm leader, run paxos; else forward to leader
    async def on_client_propose(self, msg: dict) -> dict:
        value = msg.get('value')
        if self.leader_id is None:
            # no leader known, start election and reject for now
            asyncio.create_task(self.start_election())
            return {'type': 'err', 'err': 'no_leader'}
        if self.leader_id != self.node_id:
            # forward to leader
            leader = self.leader_id
            peer = self.peers.get(leader)
            if not peer:
                return {'type': 'err', 'err': 'leader_unknown'}
            host, port = peer
            reply = await send_message(host, port, {'type': 'propose', 'value': value})
            return reply

        # I'm the leader: run coordinator that executes prepare/accept phases
        ok = await self.coordinate(value)
        return {'type': 'propose_result', 'ok': ok}

    # -----------------
    # coordinator (leader) logic: two-phase paxos (single-decree)
    # -----------------
    async def coordinate(self, value) -> bool:
        """Leader coordinates a single paxos instance for `value`.
        Returns True if consensus reached.
        """
        # Phase 1: prepare
        proposal_id = self.next_proposal_id()
        promises = []
        majority = len(self.peers) // 2 + 1

        # send prepare to all (including self via on_prepare)
        targets = list(self.peers.items()) + [(self.node_id, (self.host, self.port))]
        tasks = []
        for nid, (host, port) in targets:
            tasks.append(send_message(host, port, {'type': 'prepare', 'proposal_id': proposal_id}))
        results = await asyncio.gather(*tasks, return_exceptions=True)
        for r in results:
            if isinstance(r, dict) and r.get('type') == 'promise' and r.get('proposal_id') == proposal_id:
                promises.append(r)

        logging.info(f"Coordinator {self.node_id} got {len(promises)} promises (need {majority})")
        if len(promises) < majority:
            return False

        # choose highest accepted value if any
        accepted = [(p.get('accepted_id'), p.get('accepted_value')) for p in promises if p.get('accepted_value') is not None]
        if accepted:
            _, chosen = max(accepted, key=lambda x: x[0])
            value = chosen

        # Phase 2: accept request
        tasks = []
        for nid, (host, port) in targets:
            tasks.append(send_message(host, port, {'type': 'accept_request', 'proposal_id': proposal_id, 'value': value}))
        results = await asyncio.gather(*tasks, return_exceptions=True)
        accepted_count = 0
        for r in results:
            if isinstance(r, dict) and r.get('type') == 'accepted' and r.get('proposal_id') == proposal_id:
                accepted_count += 1

        logging.info(f"Coordinator {self.node_id} got {accepted_count} accepts (need {majority})")
        if accepted_count >= majority:
            # broadcast learn
            tasks = []
            for nid, (host, port) in targets:
                tasks.append(send_message(host, port, {'type': 'learn', 'value': value}))
            await asyncio.gather(*tasks, return_exceptions=True)
            logging.info(f"Coordinator {self.node_id} achieved consensus on {value}")
            return True
        return False

    # -----------------
    # leader election tasks
    # -----------------
    async def heartbeat_loop(self):
        while not self._stopping:
            if self.leader_id == self.node_id:
                # I am leader: broadcast heartbeat to peers
                for nid, (host, port) in self.peers.items():
                    asyncio.create_task(send_message(host, port, {'type': 'heartbeat', 'leader_id': self.node_id}))
            else:
                # check leader liveness
                if self.leader_id is not None and (time.time() - self.leader_last_heartbeat) > self.heartbeat_timeout:
                    logging.info(f"Node {self.node_id} suspects leader {self.leader_id} failed")
                    asyncio.create_task(self.start_election())
            await asyncio.sleep(self.heartbeat_interval)

    async def start_election(self):
        logging.info(f"Node {self.node_id} starting election")
        higher = {nid: addr for nid, addr in self.peers.items() if nid > self.node_id}
        if not higher:
            # I am highest; become coordinator
            await self.announce_coordinator()
            return

        # send election to higher nodes
        tasks = []
        for nid, (host, port) in higher.items():
            tasks.append(send_message(host, port, {'type': 'election', 'sender': self.node_id}))
        results = await asyncio.gather(*tasks, return_exceptions=True)
        someone_ok = any(isinstance(r, dict) for r in results if r is not None)
        if not someone_ok:
            # no one higher replied -> I win
            await self.announce_coordinator()
        else:
            logging.info(f"Node {self.node_id} waiting for coordinator announcement")
            # wait for coordinator message; if none after timeout, retry
            await asyncio.sleep(self.heartbeat_timeout * 0.7)
            if self.leader_id is None:
                # retry
                await self.start_election()

    async def announce_coordinator(self):
        self.leader_id = self.node_id
        self.leader_last_heartbeat = time.time()
        # tell everyone
        for nid, (host, port) in self.peers.items():
            asyncio.create_task(send_message(host, port, {'type': 'coordinator', 'leader_id': self.node_id}))
        logging.info(f"Node {self.node_id} became coordinator")

    # -----------------
    # lifecycle
    # -----------------
    async def start(self):
        # start server and background tasks
        self._server_task = asyncio.create_task(self.start_server())
        self.tasks.append(asyncio.create_task(self.heartbeat_loop()))
        # small startup election attempt
        await asyncio.sleep(0.2 + random_small())
        asyncio.create_task(self.start_election())

    async def stop(self):
        self._stopping = True
        if self.server:
            self.server.close()
            try:
                await self.server.wait_closed()
            except Exception:
                pass
        for t in self.tasks:
            t.cancel()

# -----------------
# helper
# -----------------

def random_small():
    import random
    return random.random() * 0.2

# -----------------
# CLI and example
# -----------------

async def main_loop(args):
    peers = {}
    if args.peers:
        for entry in args.peers.split(','):
            if not entry.strip():
                continue
            nid_s, port_s = entry.split(':')
            nid = int(nid_s)
            peers[nid] = ('127.0.0.1', int(port_s))

    storage = f'paxos_node_{args.id}.db'
    node = PaxosNode(args.id, '127.0.0.1', args.port, peers, storage)
    await node.start()

    # simple admin REPL (propose values or query state)
    print("Commands: propose <value> | state | exit")
    loop = asyncio.get_event_loop()
    while True:
        line = await loop.run_in_executor(None, input, "> ")
        if not line:
            continue
        parts = line.strip().split(maxsplit=1)
        cmd = parts[0]
        if cmd == 'exit':
            break
        elif cmd == 'state':
            print('leader:', node.leader_id)
            print('promised_id:', node.storage.promised_id)
            print('accepted_id:', node.storage.accepted_id)
            print('accepted_value:', node.storage.accepted_value)
        elif cmd == 'propose' and len(parts) == 2:
            value = parts[1]
            # send propose message to local node (will forward to leader if not leader)
            reply = await send_message('127.0.0.1', args.port, {'type': 'propose', 'value': value})
            print('reply:', reply)
        else:
            print('unknown')

    await node.stop()

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--id', type=int, required=True)
    parser.add_argument('--port', type=int, required=True)
    parser.add_argument('--peers', type=str, default='')
    args = parser.parse_args()
    try:
        asyncio.run(main_loop(args))
    except KeyboardInterrupt:
        pass

