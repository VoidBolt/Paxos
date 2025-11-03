import traceback
import asyncio
from contextlib import suppress

from acceptor_storage import AcceptorStorage
from strategies.single_decree import SingleDecreePaxos
from strategies.multi_paxos import MultiPaxos
from typing import Optional
import json
import os
import time
import struct

from enum import Enum, auto
from dataclasses import dataclass

# Logging config
import logging
from logging.handlers import RotatingFileHandler
import uuid
import json

from datetime import datetime
from paxos_node_interface import PaxosNodeInterface
from collections import defaultdict

CONSOLE_LOG_LEVEL = logging.INFO # logging.INFO
# Log instance for low-level network events
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


def _open_metrics_file(node_id: int, log_dir="logs"):
    os.makedirs(log_dir, exist_ok=True)
    path = f"{log_dir}/metrics_node_{node_id}.jsonl"
    # we will open and append on each write, so no long-lived file handle required here
    return path

# Helper-fns
def _emit_metric(path: str, event: dict):
    event.setdefault("ts", time.time())
    with open(path, "a") as f:
        f.write(json.dumps(event, default=str) + "\n")

# ------------------
# handle_connection -> dispatch -> branch based on MessageType to callback
# ------------------
"""
| Step | Sender              | Receiver            | Message  | Purpose                            |
| ---- | ------------------- | ------------------- | -------- | ---------------------------------- |
| 1    | Proposer            | Acceptors           | PREPARE  | “Can I propose with ID N?”         |
| 2    | Acceptors           | Proposer            | PROMISE  | “I promise not to accept < N.”     |
| 3    | Proposer            | Acceptors           | ACCEPT   | “Please accept value V with ID N.” |
| 4    | Acceptors           | Proposer / Learners | ACCEPTED | “I have accepted V with ID N.”     |
| 5    | Proposer / Learners | All nodes           | LEARN    | “Consensus reached on V.”          |
"""
class MessageType(str, Enum):
    # PROPOSE = "propose" does not exist, terminology is PROPOSER Sends PREPARE to receive PROMISE
    # ----------------------------------------------------------------------------------------------
    PREPARE = "prepare"
    PROMISE = "promise" # After getting enough PROMISES send ACCEPTED
    # ACCEPT = "accept"
    ACCEPTED = "accepted"
    LEARN = "learn"
    # ----------------------------------------------------------------------------------------------
    # Reconciliation
    SYNC_REQUEST = "sync_request"
    SYNC_RESPONSE = "sync_response"
    # --------------
    
    SINGLE_DECISION = "Base Paxos only makes one decision! It's already been made."
    SINGLE_DECREE_RESULT = "Single Decree Result."

    CHORUM_SUCC = "chorum success" # for better readable logs
    CHORUM_FAIL = "chorum failure" # for better readable logs

    LEARN_SUCC = "learn success"

    HEARTBEAT = "heartbeat"     # Checking Client Availability 

    ELECTION = "election"       # Only for MultiPaxos
    ELECTION_OK = "election_ok" # Only for MultiPaxos
    COORDINATOR = "coordinator" # Only for MultiPaxos
    ERR = "err"

class NetEvent(str, Enum):
    SERVER_LISTEN = "server_listen"
    SEND = "send"
    RCV = "rcv"
    SUCCESS = "success"
    REJECT = "reject"
    LOOPBACK = "loopback"

# https://bowtiedtechguy.medium.com/demystifying-paxos-python-implementation-and-visualization-6958c63c8d4b
class NodeState(Enum):
    UP = auto()
    DOWN = auto()
    BLOCKED = auto()
    UNKNOWN = auto()

class NodeRole(Enum):
    ACCEPTOR = auto()
    CANDIDATE = auto()
    LEADER = auto()
    PROPOSER = auto()
    LEARNER = auto()

# Dataclass to encapsulate the information for messages exchanged between nodes in the Paxos protocol.
@dataclass
class Message:
    sender_id: int
    receiver_id: int
    content: str

# Dataclass to represent a proposal made by a node in the Paxos consensus process, including its unique identifier and proposed value.
@dataclass
class Proposal:
    node_id: int
    proposal_id: int
    value: str  # Assuming proposals carry a value that's being agreed upon
    slot: int

# Abstract the consensus value in its own class
class ConsensusValue:
    def __init__(self, data) -> None:
        self.data = data
    
    def __str__(self) -> str:
        #return f"ConsensusValue({self.data})"
        return f"({self.data})"
# -----------------
# helper
# -----------------
async def propose_to(node_info, value: str):
    node = node_info['node']
    port = node_info['port']
    sender_id = node.node_id
    return await node.coordinate(value)
    # node.propose
    # reply = await send_message('127.0.0.1', port, {'type': MessageType.PROPOSE.value, 'value': value, "sender_id": sender_id})
    # return reply

def random_small():
    import random
    return random.random() * 0.2

# -----------------
# Paxos Node (async)
# -----------------

class PaxosNode(PaxosNodeInterface):
    def __init__(self, 
                 node_id: int, 
                 # role: NodeRole, 
                 logger, 
                 node_count: int, 
                 host: str, port: int, peers: dict, 
                 storage_path: str, strategy="single"):
        self.node_id = node_id
        self.totalnodecount = node_count
        self.state = NodeState.UP
        self.role: NodeRole = NodeRole.ACCEPTOR
        self.last_consensus = None
        self.consensus_reached = False # Set when a new consensus is reached and immediately reset after that.
        # self.received_promises = set()
        self.received_promises = {}  # dict of proposal_id -> list of promises
        self.logger = logger # This should be instance of custom class PaxosLogger and not python in built logger.
        self.acceptance_counts = {} # Track acceptance counts for each proposal.

        # log_dir = "logs"
        # self.logger = _make_logger(self.node_id, log_dir=log_dir, console_log_level=CONSOLE_LOG_LEVEL)
        # self.metrics_path = _open_metrics_file(self.node_id, log_dir=log_dir)
        # --------------------------------------------------------------------------------------------------------
        #
        self.host = host
        self.port = port
        self.peers = peers
        # mark as ready when listening
        self.ready_event = asyncio.Event()

        logging.debug(f"[Node {node_id}] peers: {self.peers}")
        self.storage = AcceptorStorage(storage_path, node_id)
        # verify node identity in DB
        stored_id = self.storage.get_meta("node_id")
        if stored_id is None:
            self.storage.set_meta("node_id", node_id)
        elif stored_id != node_id:
            raise RuntimeError(f"DB {storage_path} belongs to node {stored_id}, not {node_id}")
        # leader info
        self.leader_id: Optional[int] = None
        self.leader_last_heartbeat = 0.0

        # Track peer liveness
        # self.peer_last_heartbeat = {}
        self.peer_status = {}
        self.heartbeat_state = {}            # {node_id: last_success_timestamp}
        self.peer_status = defaultdict(lambda: NodeState.UNKNOWN)
        self.heartbeat_interval = 1.0
        self.heartbeat_timeout = 3.0

        # proposal counter
        self._proposal_counter = 0

        # server and tasks
        self.server = None
        self._server_task = None
        self.tasks: list[asyncio.Task] = []
        self._stopping = False

        # consensus strategy
        if strategy == "single":
            self.strategy = SingleDecreePaxos(self)
        elif strategy == "multi":
            self.strategy = MultiPaxos(self)
        else:
            raise ValueError(f"Unknown strategy {strategy}")

        self._election_in_progress = False

# -----------------
# Reconciliation Logic 
# -----------------

# --- Request sync from a specific node ---
    async def request_sync_from(self, target_node_id: int):
        """
        Ask another node to send us all decisions / accepted slots so we can catch up.
        """
        print(f"[Node {self.node_id}] Requesting Sync from Node {target_node_id}")
        
        self.role = NodeRole.LEARNER
        # Look up host/port
        if target_node_id not in self.peers:
            print(f"[Node {self.node_id}] Unknown peer {target_node_id}")
            return
        
        host, port = self.peers[target_node_id]
        msg = {
            "type": MessageType.SYNC_REQUEST.value,
            "sender_id": self.node_id
        }

        try:
            resp = await send_message(host, port, msg, timeout=5, node=self)
            if resp and resp.get("type") == MessageType.SYNC_RESPONSE.value:
                slots = resp.get("slots", {})
                for slot, data in slots.items():
                    accepted_id = data.get("accepted_id")
                    value = data.get("value")
                    # Update local storage if missing or behind
                    val = self.storage.get_accepted(slot)
                    if not val:
                        self.storage.set_accepted(slot, accepted_id, value)
                        # Also update decision if available
                        if data.get("decided", False):
                            self.storage.set_decision(slot, value, accepted_id)
                        return True
                    else:
                        local_aid = val[0]
                        if (accepted_id is not None and accepted_id > local_aid):
                            self.storage.set_accepted(slot, accepted_id, value)
                            # Also update decision if available
                            if data.get("decided", False):
                                self.storage.set_decision(slot, value, accepted_id)
                            return True
                print(f"[Node {self.node_id}] Sync completed with Node {target_node_id}")
        except Exception as e:
            print(f"[Node {self.node_id}] Sync request to Node {target_node_id} failed: {e}")
# --- Handler for incoming SYNC_REQUEST ---
    async def on_sync_request(self, msg: dict) -> dict:
        """
        Respond to a SYNC_REQUEST with all known slots and their accepted IDs / values.
        """
        sender_id = msg.get("sender_id")
        print(f"[Node {self.node_id}] Received SYNC_REQUEST from Node {sender_id}")

        slots_data = {}
        for slot, (accepted_id, value) in self.storage.all_accepted().items():
            slots_data[slot] = {
                "accepted_id": accepted_id,
                "value": value,
                "decided": self.storage.get_decision(slot) is not None
            }

        response = {
            "type": MessageType.SYNC_RESPONSE.value,
            "sender_id": self.node_id,
            "slots": slots_data
        }
        return response
# -----------------
# Availability Logic 
# -----------------
    async def heartbeat_loop(self):
        """Periodically ping peers and update their UP/DOWN status."""
        # if isinstance(self.strategy, MultiPaxos):
        #    return  # MultiPaxos handles heartbeats differently

        self.logger.info(f"Heartbeat loop started Node {self.node_id}. self._stopping? {self._stopping}",)
        self.logger.info(f"self.peers? {self.peers}",)
        while not self._stopping:
            now = time.time()

            for nid, (host, port) in self.peers.items():

                if nid == self.node_id:
                    continue

                proposal_id = self.storage.get_latest_proposal_id()
                known_slots = self.storage.get_known_slots()
                # --- Send heartbeat and check connectivity ---
                msg = {
                    "type": MessageType.HEARTBEAT.value,
                    "sender_id": self.node_id,
                    "highest_proposal_id": proposal_id,  # method to return max proposal_id
                    "known_slots": known_slots,  # method to return a sorted list of slots
                    "leader_id": self.leader_id
                }
                """
                self.log_action(
                    action="SEND_HEARTBEAT",
                    action_value=f"highest_proposal_id={msg['highest_proposal_id']}, known_slots={msg['known_slots']}",
                    target_node_id=nid,
                    target_node_role="ACCEPTOR",
                    target_node_state=NodeState.UP
                )
                """
                self.logger.debug(f"[Node {self.node_id}] SEND HEARTBEAT highest_proposal_id={msg['highest_proposal_id']}, known_slots={msg['known_slots']}")
                try:
                    reply = await send_message(host, port, msg, timeout=2, node=self)
                    if reply is not None:
                        # Mark peer as alive and update last heartbeat timestamp
                        self.heartbeat_state[nid] = now
                        if self.peer_status.get(nid) != NodeState.UP:
                            self.peer_status[nid] = NodeState.UP
                            self.logger.debug(f"Peer {nid} marked UP (heartbeat OK)")
                    else:
                        # No reply — may be temporarily unreachable
                        last = self.heartbeat_state.get(nid, 0)
                        if now - last > self.heartbeat_timeout:
                            if self.peer_status.get(nid) != NodeState.DOWN:
                                self.peer_status[nid] = NodeState.DOWN
                                self.logger.warning(f"Peer {nid} marked DOWN (no heartbeat reply)")
                except Exception as e:
                    self.logger.debug(f"Error: ", e)
                    self.logger.warning(f"Error: ", e)
                    # Connection or unexpected error — treat as potential failure
                    last = self.heartbeat_state.get(nid, 0)
                    if now - last > self.heartbeat_timeout:
                        if self.peer_status.get(nid) != NodeState.DOWN:
                            self.peer_status[nid] = NodeState.DOWN
                            self.logger.warning(f"Peer {nid} marked DOWN (exception: {e})")

            await asyncio.sleep(self.heartbeat_interval)

        self.logger.info("Heartbeat loop stopped.")
        """
        while not self._stopping:
            if self.leader_id == self.node_id:
                # I'm leader: broadcast heartbeat
                for nid, (host, port) in self.peers.items():
                    asyncio.create_task(send_message(
                        host, port,
                        {
                            'type': MessageType.HEARTBEAT.value,
                            'leader_id': self.node_id,
                            'sender_id': self.node_id
                        },
                        2,
                        self
                    ))
            else:
                # Follower: check if leader is alive
                if self.leader_id is not None and \
                (time.time() - self.leader_last_heartbeat) > self.heartbeat_timeout:
                    logging.info(f"[Node {self.node_id}] suspects leader {self.leader_id} failed")
                    asyncio.create_task(self.start_election())

            await asyncio.sleep(self.heartbeat_interval)
            """

    async def on_heartbeat(self, msg: dict) -> dict:
        sender_id = msg.get('sender_id')

        self.logger.debug(f"Node {self.node_id} received Heartbeat from Node {sender_id}")
        self.logger.debug(f"Node {self.node_id} -> {msg}")
        leader = msg.get('leader_id')
        highest_proposal_id = msg.get("highest_proposal_id")

        # Update leader info (for MultiPaxos)
        if isinstance(self.strategy, MultiPaxos) and leader is not None:
            self.leader_id = leader
            # Update liveness
            self.leader_last_heartbeat = time.time()

        # Update liveness
        if sender_id:
            # self.peer_last_heartbeat[sender] = time.time()
            # TODO
            self.peer_status[sender_id] = {
                'last_heartbeat': time.time(),
                'state': NodeState.UP
            }
            self.logger.debug(f"Node {self.node_id} updated peer status of Node {sender_id}: {self.peer_status[sender_id]}")
            self.logger.debug(f"Node {self.node_id} peer.status: {self.peer_status}")
        
        get_latest_proposal_id = self.storage.get_latest_proposal_id()
        if not get_latest_proposal_id and highest_proposal_id:
            self.logger.debug(f"[Node {self.node_id}] Detected higher proposal ID {highest_proposal_id} from Node {sender_id}")
            await self.request_sync_from(sender_id)
        elif get_latest_proposal_id and highest_proposal_id:
            if highest_proposal_id > get_latest_proposal_id:
                self.logger.debug(f"[Node {self.node_id}] Detected higher proposal ID {highest_proposal_id} from Node {sender_id}")

                await self.request_sync_from(sender_id)

        return {'type': 'heartbeat_ok', 'sender_id': self.node_id}

    def has_quorum(self):
        up_nodes = [n for n, s in self.peer_status.items() if s == NodeState.UP]
        return len(up_nodes) + 1 >= (len(self.peers) // 2 + 1)  # +1 for self

    def check_cluster_health(self):
        if not self.has_quorum():
            if self.state == NodeState.UP:
                self.set_state(NodeState.BLOCKED, "lost majority connectivity")
        elif self.state == NodeState.BLOCKED:
            self.set_state(NodeState.UP, "quorum restored")

# -----------------
# Coordinator logic (multi-paxos with Leader or Single Paxos Proposer)
# -----------------
    async def coordinate(self, value, slot: int = 1):
        """
        Run Paxos (prepare -> accept -> learn) for a given value.
        Called by the leader or proposer.
        """
        if self.state == NodeState.DOWN:
            self.logger.error("Node is DOWN, cannot coordinate.")
            return None

        if self.state == NodeState.BLOCKED:
            self.logger.warning("Node is BLOCKED, ignoring coordinate request.")
            return None
        self.logger.info(f"Node {self.node_id} Coordinate!")
        if isinstance(self.strategy, SingleDecreePaxos):
            if self.strategy.chosen_value is not None:
                # Already decided
                # logging.info(f"[Node {self.node_id}] Single-decree: value already chosen -> {self.strategy.chosen_value}")
                return True
            slot = 1  # single-decree uses only one logical slot
        else:
            slot = self.storage.next_slot()

        proposal_id = self.next_proposal_id()

        self.logger.info(f"Node {self.node_id} next_proposal_id: {proposal_id}")
        self.t0 = time.perf_counter()
        self.log_event(
            logging.INFO,
            MessageType.COORDINATOR.value, 
            value=value,
            latency=(time.perf_counter() - self.t0),
        )
        # _emit_metric(self.metrics_path, self._make_event(MessageType.COORDINATOR.value, proposal_id=proposal_id, slot=slot, value=value))
        
        proposal = Proposal(self.node_id, proposal_id, value, slot)# {"proposal_id": proposal_id, "slot": slot, "value": value}
        # -----------------
        # Phase 1: Prepare
        # -----------------
        
        await self.send_prepare(self.peers.items(), proposal)

        if not self.decide_on_promises_received(proposal):

            return False

        # -----------------
        # Phase 2: Accepted
        # -----------------
        
        accepted_count = await self.send_accept(self.peers.items(), proposal)

        quorum = len(self.peers) // 2 + 1
        if accepted_count < quorum:
            self.log_event(
                logging.INFO,
                MessageType.CHORUM_FAIL.value,
                proposal_id=proposal_id,
                slot=slot,
                value=value,
                latency=(time.perf_counter() - self.t0),
            )
            # _emit_metric(self.metrics_path, self._make_event("coordinate_failed", proposal_id=proposal_id, slot=slot, reason="not_enough_promises"))
            self.set_state(NodeState.BLOCKED, "failed to get majority accepts")                       # Could not reach majority quorum
            return None
        

        # if we are here, we have reached consensus
        self.log_event(
            logging.INFO,
            MessageType.CHORUM_SUCC.value,
            proposal_id=proposal_id,
            slot=slot,
            value=value,
            latency=(time.perf_counter() - self.t0),
        )
        # _emit_metric(self.metrics_path, self._make_event("accept_result", proposal_id=proposal_id, slot=slot, accepted_count=accepted_count, quorum=quorum))
        # -----------------
        # Phase 3: Learn
        # -----------------
        # Success — learned value
        self.set_state(NodeState.UP, "achieved quorum, decision made")
        self.set_consensus(value, slot)
        ack_learn_count = await self.send_learn(self.peers.items(), proposal)


        if self.last_consensus != None:# self.strategy.is_consensus_reached():
            self.logger.info(f"Consensus reached, saving logs to CSV for Node {self.node_id}.")
            # input("SAVE")
            self.logger.save_to_csv()

        return True

    async def send_prepare(self, nodes, proposal):
        """
        Prepare / Promise phase (Leader election)
        PROPOSER -> Send prepare to all nodes
        expect each node to return a promise if the proposal_id is the highest they have seen
        """
        print("DEBUG proposal:", proposal, type(proposal))
        prepare_msg = {
            "type": MessageType.PREPARE.value, 
            "proposal_id": proposal.proposal_id, # proposal_id, 
            "slot": proposal.slot, # slot,
            "value": proposal.value, # value,
            'sender_id': self.node_id
        }
        self.role = NodeRole.PROPOSER
        # 🟣 1️⃣ Handle self as an acceptor (loopback)
        try:
            self.log_event(
                logging.INFO,
                prepare_msg["type"],
                value=prepare_msg["value"],
                latency=(time.perf_counter() - self.t0),
                sender_id=self.node_id,
                network_op=NetEvent.LOOPBACK.value
            )

            # act as acceptor for our own prepare
            local_promise = await self.on_prepare(prepare_msg)
            if local_promise and local_promise.get("type") == MessageType.PROMISE.value:
                self.receive_promise(local_promise)
                self.logger.debug(f"[Node {self.node_id}] Counted self PROMISE for proposal {proposal.proposal_id}")

        except Exception as e:
            self.logger.error(f"[Node {self.node_id}] Error during self-promise handling: {type(e).__name__}: {e}")
            self.logger.debug(traceback.format_exc())

        # 🟣 2️⃣ Continue sending PREPARE to peers normally
        for nid, (host, port) in nodes: # self.peers.items():
            try:
                #print("Send PREPARE:", nid, (host, port))
                self.log_event(
                    logging.INFO,
                    prepare_msg['type'], 
                    value=prepare_msg['value'],
                    latency=(time.perf_counter() - self.t0),
                    # peer=f"[Node {self.node_id}] -> {peer}",
                    sender_id=nid,
                    network_op=NetEvent.SEND.value
                )

                self.log_action(
                    action="SEND_PREPARE",
                    action_value=f"proposal_id={proposal.proposal_id}",
                    target_node_id=nid,
                    target_node_role="ACCEPTOR",
                    target_node_state=NodeState.UP
                )
                # _emit_metric(self.metrics_path, self._make_event(prepare_msg['type'], proposal_id=proposal['proposal_id'], slot=proposal['slot'], value=proposal['value']))
                self.logger.debug(f"Send Prepare message with Node {self.node_id} to Node {nid}...")
                # Send prepare request to peer
                resp = await send_message(host, port, prepare_msg, 2, self)
                self.logger.debug(f"Send Prepare (Node {self.node_id}) received a response!")
                # If response is a PROMISE, handle it separately
                if resp and resp.get("type") == MessageType.PROMISE.value:
                    self.receive_promise(resp)   # ⬅️ refactored
            except Exception as e:
                self.logger.error(f"Exception in send_prepare of Node {self.node_id}: {e}")
                # logging.warning(f"[Node {self.node_id} | {self.role.name}] no response to PREPARE from {nid}: {e}")
                self.log_event(
                    logging.WARN,
                    MessageType.ERR.value,
                    latency=(time.perf_counter() - self.t0),
                )

    def receive_prepare(self, proposal):
        """
        Handle incoming PREPARE message (ACCEPTOR side).
        """
        # Check if proposal_id is highest seen so far
        if proposal.proposal_id > getattr(self, "max_seen_proposal", -1):
            self.max_seen_proposal = proposal.proposal_id
            return self.send_promise(proposal)
        else:
            return None

    async def send_accept(self, nodes, proposal):
        """
        After Prepare -> Send Accept 
        """
        accept_msg = {
            "type": MessageType.ACCEPTED.value,
            "proposal_id": proposal.proposal_id,
            "value": proposal.value,
            "slot": proposal.slot,
            'sender_id': self.node_id
        }
        accepted_count = 1  # self accepts

        for nid, (host, port) in nodes:
            try:

                self.log_event(
                    logging.INFO,
                    MessageType.ACCEPTED.value, 
                    value=accept_msg['value'],
                    latency=(time.perf_counter() - self.t0),
                    network_op=NetEvent.SEND.value,
                    sender_id=nid
                )

                self.log_action(
                    action="SEND_ACCEPT",
                    action_value=f"proposal_id={proposal.proposal_id}, value={proposal.value}",
                    target_node_id=nid,
                    target_node_role="ACCEPTOR",
                    target_node_state=NodeState.UP
                )
                # _emit_metric(self.metrics_path, self._make_event("SEND " + MessageType.ACCEPTED.value, proposal_id=proposal_id, slot=slot, value=value))

                # Send prepare request to peer
                resp = await send_message(host, port, accept_msg, 2, self)

                # If response is a PROMISE, handle it separately
                if resp and resp.get("type") == MessageType.ACCEPTED.value:
                    self.receive_accept(resp)
                    accepted_count += 1
            except Exception as e:
                self.logger.error(f"Exception in send_accept of Node {self.node_id}: {e}")

        return accepted_count

    def receive_accept(self, proposal):
        """
        Receive Accept -> 
        """
        pass

    def send_promise(self, proposal):
        """
        Send PROMISE message back to proposer.
        """
        promise_msg = {
            "type": MessageType.PROMISE.value,
            "sender_id": self.node_id,
            "proposal_id": proposal.proposal_id,
            "slot": proposal.slot,
            "accepted_value": getattr(self, "accepted_value", None),
        }
        return promise_msg

    def receive_promise(self, promise):
        """
        Handle incoming PROMISE message (PROPOSER side).
        """
        self.log_event(
            logging.INFO,
            MessageType.PROMISE.value,
            value=promise.get("accepted_value"),
            network_op=NetEvent.RCV.value,
            sender_id=promise.get("sender_id"),
        )
        try:
            # Store promises for this round
            proposal_id = promise["proposal_id"]
            if proposal_id not in self.received_promises:
                print(f"Adding pid={proposal_id}-list to received_promises.")
                self.received_promises[proposal_id] = []
            print(f"Appending Promise to proposal_id={proposal_id}-list.")

            self.log_action(
                action="RECEIVE_PROMISE",
                action_value=f"proposal_id={proposal_id}, value={promise['value']}",
                target_node_id=promise['sender_id'],
                target_node_role="ACCEPTOR",
                target_node_state=NodeState.UP
            )
            self.received_promises[proposal_id].append(promise)

            quorum_size = len(self.peers) // 2 + 1
            print("Required Quorum: ", quorum_size)
            promises = self.received_promises[proposal_id]
            print(f"Received-Promises: {len(promises)}", promises)

            if len(promises) >= quorum_size and self.state == NodeState.BLOCKED:
                self.set_state(NodeState.UP, "quorum restored during prepare phase")

        except Exception as e:
            print(f"Exception in receive_promise of Node {self.node_id}: {e}")

    async def send_learn(self, nodes, proposal):
        learn_msg = {
            "type": MessageType.LEARN.value, 
            "slot": proposal.slot, 
            "value": proposal.value, 
            "accepted_id": proposal.proposal_id,
            'sender_id': self.node_id
        }
        ack_count = 1 # assuming self agreed (TODO)

        # print(f"Node {self.node_id}", self.strategy.chosen_value)
        # input()
        for nid, (host, port) in nodes:

            print("Send LEARN:", nid, (host, port))
            self.log_event(
                logging.INFO,
                MessageType.LEARN.value, 
                value=learn_msg['value'],
                slot=learn_msg['slot'],
                latency=(time.perf_counter() - self.t0),
                network_op=NetEvent.SEND.value,
                sender_id=nid
            )

            self.log_action(
                action="SEND_LEARN",
                action_value=f"value={learn_msg['value']}",
                target_node_id=nid,
                target_node_role="LEARNER",
                target_node_state=NodeState.UP
            )
            # _emit_metric(self.metrics_path, self._make_event("SEND " + MessageType.LEARN.value, proposal_id=proposal_id, slot=slot, value=value))
            # asyncio.create_task(send_message(host, port, learn_msg, 2, self))
            resp = await send_message(host, port, learn_msg, 2, self)
            # resp -> {"type": MessageType.LEARN_SUCC.value, "slot": slot}
            if not resp:
                self.peer_status[nid] = NodeState.DOWN
                continue

            if (self.receive_learn(resp)):
                ack_count += 1
        return ack_count

    def receive_learn(self, proposal):
        if proposal['type'] == MessageType.LEARN_SUCC.value:
            return True
        return False

    def decide_on_promises_received(self, proposal):
        promises = self.received_promises[proposal.proposal_id]
        value = proposal.value
        slot = proposal.slot
        quorum_size = len(self.peers) // 2 + 1

        if len(promises) < quorum_size:
            self.logger.warning(f"[Node {self.node_id} | {self.role.name}] PREPARE failed (got {len(promises)+1}, need {quorum_size}) slot={slot}")
            # _emit_metric(self.metrics_path, self._make_event("coordinate_failed", proposal_id=proposal_id, slot=slot, reason="not_enough_promises"))
            self.set_state(NodeState.BLOCKED, "lost quorum during prepare")

            # input("Failed Chorum since not enough promises?")
            self.log_action(
                action="QUORUM_FAILURE",
                action_value=f"received={len(promises)}, required={quorum_size}",
            )
            return False

        # _emit_metric(self.metrics_path, self._make_event("prepare_result", proposal_id=proposal_id, slot=slot, promises=len(promises), quorum=quorum))

        # Adopt highest accepted value (if any)
        accepted = [(p["accepted_id"], p["accepted_value"]) for p in promises if p.get("accepted_id")]
        if accepted:
            _, chosen_value = max(accepted, key=lambda x: x[0])
            logging.info(f"[Node {self.node_id} | {self.role.name}] adopting previously accepted value={chosen_value} slot={proposal.slot}")
            value = chosen_value
        
        self.storage.set_promised(proposal.slot, proposal.proposal_id)
        self.storage.set_accepted(proposal.slot, proposal.proposal_id, value)
        return True

    def set_state(self, new_state: NodeState, reason: str = ""):
        old_state = getattr(self, "state", None)
        if old_state != new_state:
            self.log_action(
                action="STATE_CHANGE",
                action_value=reason or f"{old_state.name if old_state else 'INIT'} → {new_state.name}",
                target_node_id=self.node_id,
                target_node_role=getattr(self, "role", "UNKNOWN"),
                target_node_state=new_state,
            )
            self.state = new_state
            self.logger.info(f"[STATE] {self.node_id}: {old_state.name if old_state else 'INIT'} -> {new_state.name} ({reason})")

    def log_action(
        self,
        action: str,
        action_value: str = "",
        target_node_id: str = None,
        target_node_role: str = None,
        target_node_state: NodeState = None,
        consensus_value: str = None,
        consensus_reached: bool = False,
    ):
        """
        General-purpose structured logging helper for any Paxos action or state transition.
        """
        try:
            # Resolve target info
            to_node_id = target_node_id or self.node_id
            to_node_role = target_node_role or getattr(self, "role", "UNKNOWN")
            to_node_state = target_node_state.name if target_node_state else (
                self.peer_status.get(to_node_id, NodeState.UP).name
                if hasattr(self, "peer_status") else "UNKNOWN"
            )

            # Resolve current node info
            from_role = getattr(self, "role", "UNKNOWN")
            from_state = getattr(self, "state", NodeState.UP).name

            # input(f"Is_Consensus_Reached?: {self.strategy.is_consensus_reached()} -> {self.strategy.chosen_value}")

            # Resolve consensus data
            consensus_value = consensus_value or (
                self.storage.get_latest_decision() if hasattr(self, "storage") else None
            )
            consensus_reached = consensus_reached or (
                self.strategy.is_consensus_reached() if hasattr(self, "strategy") else False
            )

            # input(f"Consensus_Value: {consensus_value}, reached? {consensus_reached}")
            
            # Write structured log entry
            if hasattr(self, "logger") and hasattr(self.logger, "record_log"):
                self.logger.record_log(
                    from_node_id=self.node_id,
                    from_node_role=from_role,
                    from_node_state=from_state,
                    to_node_id=to_node_id,
                    to_node_role=to_node_role,
                    to_node_state=to_node_state,
                    action=action,
                    action_value=action_value,
                    consensus_value=consensus_value,
                    consensus_reached=consensus_reached,
                )
        except Exception as e:
            print(f"Error on log_action: {e}")
    def log_state_change(self, old_state: NodeState, new_state: NodeState, reason: str = ""):
        """
        Log a node state transition using the structured Paxos logger.
        """
        self.logger.record_log(
            from_node_id=self.node_id,
            from_node_role=self.role.name if hasattr(self, "role") else "UNKNOWN",
            from_node_state=old_state.name if old_state else "UNKNOWN",
            to_node_id=self.node_id,
            to_node_role=self.role.name if hasattr(self, "role") else "UNKNOWN",
            to_node_state=new_state.name,
            action="STATE_CHANGE",
            action_value=reason or f"{old_state.name} → {new_state.name}",
            consensus_value=self.storage.get_latest_decision() if hasattr(self, "storage") else None,
            consensus_reached=self.strategy.is_consensus_reached() if hasattr(self, "strategy") else False
        )
        

    def receive_broadcast(self, proposal):
        pass

    def set_consensus(self, value, slot=1, accepted_id=0):
        self.last_consensus = value
        self.storage.set_decision(slot, value, accepted_id)
        if isinstance(self.strategy, SingleDecreePaxos):
            self.strategy.chosen_value = value
            self.strategy.proposal_id = accepted_id



    def reset_consensus_reached(self):
        print(f"reset_consensus called, last_consensus=None!")
        self.last_consensus = None


    def log_event(self, level, event, **fields):
        """
        Unified structured log for correlation across nodes.
        """
        record = {
            "ts": datetime.utcnow().isoformat() + "Z",
            "node_id": self.node_id,
            "role": self.role.name if hasattr(self, "role") else None,
            "event": event,
        }
        record.update(fields)
        send_str = ""
        if fields.get('network_op') != None:
            if fields.get('network_op') == NetEvent.SEND.value:
                send_str = f"[Node {self.node_id} -> Node {fields.get('sender_id', '?')}]: {event} "
            else:
                send_str = f"[Node {fields.get('sender_id', '?')} -> Node {self.node_id}]: {event} "
        else:
            send_str = f"[Node {self.node_id}]: {event} "
        # Console-friendly human message
        summary = (
            f"{send_str}"
            f"dir={fields.get('direction','?')} " # peer={fields.get('peer','?')} "
            f"msg={fields.get('msg_id','?')} pid={fields.get('proposal_id','?')} slot={fields.get('slot','?')} "
            f"value={fields.get('value','')}"
        )
        self.logger.log(level, summary, extra={"extra_data": record})

    def _make_event(self, etype: str, **fields):
        ev = {
            "node": self.node_id,
            "event": etype,
            "pid": fields.pop("proposal_id", None),
            "slot": fields.pop("slot", None),
            "value": fields.pop("value", None),
            "extra": fields
        }
        return ev
    @property
    def running(self) -> bool:
        return self._server_task is not None and not self._server_task.done()
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
        self.ready_event.set()  # ✅ mark as ready
        # self.logger.info(f"[Node {self.node_id}] listening on {addr}")
        e1 = f"[Node {self.node_id}]-NET ->" + " " + NetEvent.SERVER_LISTEN.value + " " + str(addr)
        self.log_event(
            logging.INFO,
            e1
        )
        async with self.server:
            await self.server.serve_forever()
        # async with self.server:
        #    await self.server.serve_forever()

    async def handle_connection(self, reader: asyncio.StreamReader, writer: asyncio.StreamWriter):
        peer = writer.get_extra_info('peername')
        info_keys = ["peername", "sockname", "sslcontext", "peercert", "ssl_object", "socket"]

        network_logger.debug(f"[Node {self.node_id}] received connection from {peer}")

        for key in info_keys:
            val = writer.get_extra_info(key)
            network_logger.debug(f"{key}: {val}")
        # sender_id = writer.get_extra_info('sender_id')
        try:
            hdr = await reader.readexactly(MSG_HDR.size)
            (n,) = MSG_HDR.unpack(hdr)
            body = await reader.readexactly(n)
            msg = json.loads(body.decode())

            if not msg:
                reply = {"status": "internal error (msg could not be received)"}  # <-- fix here

            # if msg["type"] != 'heartbeat' and msg['type'] != 'heartbeat_ok':
            #    print(msg)
            sender_id = msg["sender_id"]
            
            # check if message is paxos-related, so no heartbeat f.e.
            # send actual proposal to dispatch handler?
            # proposal = Proposal(sender_id, msg["proposal_id"], msg['value'], msg['slot'])

            if msg.get('type') == 'heartbeat' or msg.get('type') == 'heartbeat_ok':
                self.logger.debug(f"[Node {sender_id} -> Node {self.node_id}] RECV msg from {peer} of type({msg.get('type')})")
            else:
                self.logger.info(f"[Node {sender_id} -> Node {self.node_id}] RECV msg from {peer} of type({msg.get('type')})")
            # _emit_metric(self.metrics_path, self._make_event("RECV", from_peer=peer, type=msg.get("type"), raw=msg))

            # dispatch
            reply = await self.dispatch(msg)

            if not reply:
                reply = {"status": "internal error (dispatch method returned empty reply)"}  # <-- fix here
            
            if reply.get('type') == 'heartbeat_ok':
                self.logger.debug(f"[Node {self.node_id} -> Node {sender_id}] {NetEvent.SEND.value} msg to {peer} of type({reply.get('type')})")
            else:
                self.logger.info(f"[Node {self.node_id} -> Node {sender_id}] {NetEvent.SEND.value} msg to {peer} of type({reply.get('type')})")

            # _emit_metric(self.metrics_path, self._make_event(NetEvent.SEND.value, to_peer=peer, type=reply.get("type")))


            data = json.dumps(reply).encode()
            writer.write(MSG_HDR.pack(len(data)))
            writer.write(data)
            await writer.drain()
        except Exception as e:
            print(f"Exception in handle_connection of Node {self.node_id} in fn: type({msg.get('type')}))", e)
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
        try:
            mtype = MessageType(msg.get("type"))
        except ValueError:
            print("Got Unknown MessageType! Check dispatch.")
            return await self.on_unknown(msg)
        
        # CLEAN THIS UP
        handlers = {
            # MessageType.PROPOSE: self.on_client_propose, # instead of triggering via network, call on node.coordinate
            MessageType.PREPARE: self.on_prepare, # self.send_promise, # self.on_prepare,
            MessageType.ACCEPTED: self.on_accept,
            MessageType.LEARN: self.on_learn,
            MessageType.HEARTBEAT: self.on_heartbeat,
            MessageType.ELECTION: self.on_election,
            MessageType.ELECTION_OK: self.on_election_ok,
            MessageType.COORDINATOR: self.on_coordinator,
            MessageType.SYNC_REQUEST: self.on_sync_request,
        }
        handler = handlers.get(mtype, self.on_unknown)

        try:

            return await handler(msg)
            # If the handler accepts 'peer', pass it in
            # sig = inspect.signature(handler)
            # if 'peer' in sig.parameters:
            # else:
            #     return await handler(msg)
        except Exception as e:
            logging.exception(f"Node {self.node_id} handler {mtype} crashed: {e}")
            return {"type": MessageType.ERR.value, "err": f"handler_exception_{mtype.value}", "sender_id": self.node_id}

    async def on_unknown(self, msg: dict):
        logging.debug(f"Node {self.node_id} unknown message type: {msg.get('type')}")
        return {'err': 'unknown', "sender_id": self.node_id}

# -----------------
# Acceptor: prepare
# -----------------
    async def on_prepare(self, msg: dict) -> dict:
        slot = msg.get("slot", 1)

        proposal_id = msg["proposal_id"]
        sender_id = msg["sender_id"]
        value = msg["value"]
        promised = self.storage.get_promised(slot)
        self.log_action(
            action="RECEIVE_PREPARE",
            action_value=f"promised_id={proposal_id}",
            target_node_id=sender_id,
            target_node_role="PROPOSER",
            target_node_state=NodeState.UP
        )
        self.log_event(
            logging.INFO,
            MessageType.PREPARE.value,
            proposal_id=proposal_id,
            slot=slot,
            value=value,
            network_op=NetEvent.RCV.value,
            sender_id=sender_id
        )

        accepted_id, accepted_value = self.storage.accepted(slot)
        # _emit_metric(self.metrics_path, self._make_event(e1, proposal_id=proposal_id, slot=slot, value=value))
        if promised is None or proposal_id > promised:
            self.storage.set_promised(slot, proposal_id)

            self.log_event(
                logging.INFO,
                MessageType.PROMISE.value, # "PROMISE",
                proposal_id=proposal_id,
                slot=slot,
                value=value,
                accepted_id=accepted_id,
                sender_id=sender_id,
                network_op=NetEvent.SEND.value
            )

            self.log_action(
                action="SEND_PROMISE",
                action_value=f"promised_id={proposal_id}",
                target_node_id=sender_id,
                target_node_role="PROPOSER",
                target_node_state=NodeState.UP
            )
            # _emit_metric(self.metrics_path, self._make_event(e, proposal_id=proposal_id, slot=slot, accepted_id=accepted_id, accepted_value=accepted_value))
            return {
                "type": MessageType.PROMISE.value,
                "proposal_id": proposal_id,
                "slot": slot,
                "accepted_id": accepted_id,
                "accepted_value": accepted_value,
                "value": value,
                "sender_id": self.node_id
            }
        else:
            # logging.debug(f"[Node {self.node_id} | {self.role.name}] REJECT prepare pid={proposal_id} promised={promised} slot={slot}")
            self.logger.debug(f"[Node {self.node_id}] REJECT prepare pid={proposal_id} promised={promised} slot={slot}")
            # _emit_metric(self.metrics_path, self._make_event("promise_reject", proposal_id=proposal_id, slot=slot, promised=promised))
            return {"type": NetEvent.REJECT.value, "proposal_id": proposal_id, "promised_id": accepted_id, "slot": slot, "sender_id": sender_id, "value": accepted_value}

# -----------------
# Acceptor: accept request
# -----------------
    async def on_accept(self, msg: dict) -> dict:
        slot = msg.get("slot", 1)
        proposal_id = msg["proposal_id"]
        value = msg["value"]
        sender_id = msg["sender_id"]

        promised = self.storage.get_promised(slot)

        self.log_action(
            action="RECEIVE_ACCEPT",
            action_value=f"proposal_id={proposal_id}, accepted=True",
            target_node_id=sender_id,
            target_node_role="PROPOSER",
            target_node_state=NodeState.UP
        )
        if promised is None or proposal_id >= promised:
            self.storage.set_promised(slot, proposal_id)
            self.storage.set_accepted(slot, proposal_id, value)
            # logging.info(f"[Node {self.node_id} | {self.role.name}] ACCEPTED pid={proposal_id} value={value} slot={slot}")
            # self.logger.info(f"[Node {self.node_id} | {self.role.name}] ACCEPTED pid={proposal_id} value={value} slot={slot}")
            self.log_event(
                logging.INFO,
                MessageType.ACCEPTED.value, # "ACCEPTED",
                proposal_id=proposal_id,
                slot=slot,
                value=value,
                # peer=f"[Node {sender_id}] -> {peer}"
                sender_id=self.node_id
            )
            # _emit_metric(self.metrics_path, self._make_event("accepted", proposal_id=proposal_id, slot=slot, value=value))

            self.log_action(
                action="SEND_ACCEPTED",
                action_value=f"proposal_id={proposal_id}, accepted=True",
                target_node_id=sender_id,
                target_node_role="PROPOSER",
                target_node_state=NodeState.UP
            )
            return {"type": MessageType.ACCEPTED.value, "proposal_id": proposal_id, "slot": slot, "sender_id": self.node_id}
        else:
            # logging.debug(f"[Node {self.node_id} | {self.role.name}] REJECT accept pid={proposal_id} promised={promised} slot={slot}")
            self.logger.debug(f"[Node {self.node_id} | {self.role.name}] REJECT accept pid={proposal_id} promised={promised} slot={slot}")
            # _emit_metric(self.metrics_path, self._make_event("accept_reject", proposal_id=proposal_id, slot=slot, promised=promised))
            return {"type": NetEvent.REJECT.value, "promised_id": promised, "slot": slot, "sender_id": self.node_id}
# -----------------
# Learner: learn broadcast
# -----------------
    async def on_learn(self, msg: dict) -> dict:
        slot = msg.get("slot", 1)
        value = msg["value"]
        accepted_id = msg["accepted_id"]
        sender_id = msg["sender_id"]
        self.role = NodeRole.LEARNER
        # Update acceptor storage
        self.storage.set_accepted(slot, accepted_id, value)
        self.set_consensus(value, slot, accepted_id)

        self.set_state(NodeState.UP, "achieved quorum, decision made")
        self.log_action(
            action="RECEIVE_LEARN",
            action_value=f"value={value}",
            target_node_id=sender_id,
            target_node_role="PROPOSER",
            target_node_state=NodeState.UP
        )

        # print(f"Node {self.node_id}", self.strategy.chosen_value)
        # input()
        # If single-decree, update strategy chosen_value
        # if isinstance(self.strategy, SingleDecreePaxos):
        #    if self.strategy.chosen_value is None:
        #        self.strategy.chosen_value = value
        #        self.logger.debug(f"[Node {self.node_id}] Single-decree: value set via LEARN -> {value}")

        
        self.logger.debug(f"[Node {self.node_id} | {self.role.name}] LEARNED value={value} slot={slot}")

        self.log_event(
            logging.INFO,
            MessageType.LEARN.value, # "CLIENT_LEARN",
            proposal_id=accepted_id,
            slot=slot,
            accepted_id=accepted_id,
            value=value,
            # peer=f"[Node {sender_id}] -> {peer}"
            network_op=NetEvent.RCV.value,
            sender_id=sender_id
        )

        self.log_action(
            action="SEND_LEARN_SUCCESS",
            action_value=f"value={value}",
            target_node_id=sender_id,
            target_node_role="PROPOSER",
            target_node_state=NodeState.UP
        )

        if self.last_consensus != None:# self.strategy.is_consensus_reached():
            self.logger.info(f"Consensus reached, saving logs to CSV for Node {self.node_id}.")
            # input("SAVE")
            self.logger.save_to_csv()
        # _emit_metric(self.metrics_path, self._make_event("learn", slot=slot, value=value, accepted_id=accepted_id))
        return {"type": MessageType.LEARN_SUCC.value, "slot": slot, "value": value, "sender_id": self.node_id, "proposal_id": accepted_id}

# -----------------
# Client propose
# -----------------
    async def on_client_propose(self, msg: dict, peer) -> dict:
        value = msg.get('value')
        sender_id = msg.get("sender_id")
        # logging.info(f"[Node {self.node_id}] proposing value -> {value}")
        start = time.perf_counter()
        # self.logger.info(f"[Node {self.node_id}] proposing value -> {value}")
        """
        self.log_event(
            logging.INFO,
            MessageType.PROPOSE.value,
            value=value,
            latency= (time.perf_counter()-start),
            # peer=f"[Node {self.node_id}] -> {peer}"
            network_op=NetEvent.SEND.value,
            sender_id=self.node_id
        )
        
        # _emit_metric(self.metrics_path, self._make_event(MessageType.PROPOSE.value, value=value))
        """
        # Single-decree short-circuit
        if isinstance(self.strategy, SingleDecreePaxos):
            if self.strategy.chosen_value is not None:
                # Already decided: return immediately
                end = time.perf_counter()

                self.log_event(
                    logging.INFO,
                    MessageType.SINGLE_DECISION.value,
                    value=value,
                    latency=(end - start),
                    peer=f"[Node {sender_id}] -> {peer}"
                )
                return {
                    'type': MessageType.SINGLE_DECISION.value,
                    'ok': True,
                    'value': self.strategy.chosen_value,
                    'info': MessageType.SINGLE_DECISION.value,
                    'sender_id': self.node_id
                }
            else:
                # logging.info(f"[Node {self.node_id}] SingleDecreePaxos (value not chosen yet?)")
                self.logger.info(f"[Node {self.node_id}] SingleDecreePaxos (value not chosen yet?)")

            # No leader needed for single-decree: propose directly
            ok = await self.strategy.propose(value)
            end = time.perf_counter()

            self.log_event(
                logging.INFO,
                MessageType.SINGLE_DECREE_RESULT.value,
                value=value,
                latency=(end - start),
            )
            # _emit_metric(self.metrics_path, self._make_event(MessageType.SINGLE_DECREE_RESULT.value, value=value, ok=ok, latency=(end-start)))
            return {'type': MessageType.SINGLE_DECREE_RESULT.value, 'ok': ok, 'value': self.strategy.chosen_value, "sender_id": self.node_id}

        # Multi-Paxos path requires leader
        if self.leader_id is None:
            asyncio.create_task(self.start_election())
            return {'type': 'err', 'err': 'no_leader', "sender_id": self.node_id}
        if self.leader_id != self.node_id:
            peer = self.peers.get(self.leader_id)
            if not peer:
                return {'type': 'err', 'err': 'leader_unknown', "sender_id": self.node_id}

            host, port = peer
            # PROPOSE ??
            prepare_res = {
                'type': MessageType.PREPARE.value, 
                'value': value, 
                'sender_id': self.node_id
            }
            return await send_message(host, port, prepare_res, 2, self)

        # Multi-Paxos leader path
        if isinstance(self.strategy, MultiPaxos):
            slot = self.storage.next_slot()
            ok = await self.strategy.propose(value, slot=slot)
            return {'type': 'propose_result', 'ok': ok, 'slot': slot, 'sender_id': self.node_id}

    # -----------------
    # leader election tasks
    # -----------------
    async def start_election(self):
        if not isinstance(self.strategy, MultiPaxos):
            logging.debug(f"[Node {self.node_id} Election not part of Single-Decree Paxos. Skipping.")
            return  # single-decree: no election needed

        if self._election_in_progress or self.leader_id is not None:
            logging.debug(f"[Node {self.node_id} Election is already in progress or leader is already selected. Skipping new election.")
            return

        self._election_in_progress = True
        self.role = NodeRole.CANDIDATE
        logging.info(f"[Node {self.node_id} | {self.role.name}] starting election")

        higher = {nid: addr for nid, addr in self.peers.items() if nid > self.node_id}

        if not higher:
            # no higher nodes: become leader
            await self.announce_coordinator()
            self._election_in_progress = False
            return

        # send election messages to higher nodes
        tasks = [send_message(host, port, {'type': 'election', 'sender_id': self.node_id}, 2, self)
                for nid, (host, port) in higher.items()]
        results = await asyncio.gather(*tasks, return_exceptions=True)

        someone_ok = any(isinstance(r, dict) for r in results if r is not None)

        if not someone_ok:
            # no higher node responded: become leader
            await self.announce_coordinator()
        else:
            # wait for coordinator message
            await asyncio.sleep(self.heartbeat_timeout * 0.7)
            if self.leader_id is None:
                # retry once with small random delay
                await asyncio.sleep(random_small())
                await self.start_election()

        self._election_in_progress = False

    async def announce_coordinator(self):
        self.role = NodeRole.LEADER
        self.leader_id = self.node_id
        self.leader_last_heartbeat = time.time()
        logging.info(f"[Node {self.node_id} | {self.role.name}] became coordinator")
        for nid, (host, port) in self.peers.items():
            asyncio.create_task(send_message(host, port, {"type": MessageType.COORDINATOR.value, "leader_id": self.node_id, 'sender_id': self.node_id}, 2, self))
# -----------------
# election/heartbeat handlers added (missing in original)
# -----------------
    async def on_election(self, msg: dict) -> dict:
        sender = msg.get('sender_id')
        logging.info(f"[Node {self.node_id}] received ELECTION from {sender}")

        # Only respond if sender is lower
        if self.node_id > sender and self.role != NodeRole.LEADER:
            # reply is implicit; schedule election if not already candidate
            asyncio.create_task(self.start_election())

        return {'type': 'election_ok', "sender_id": self.node_id}


    async def on_election_ok(self, msg: dict) -> dict:
# a higher node acknowledged our election message
        logging.debug(f"[Node {self.node_id}] received ELECTION_OK")
# nothing special to do here; start_election checks responses
        return {'type': 'ok', "sender_id": self.node_id}

    async def on_coordinator(self, msg: dict) -> dict:
        leader = msg.get('leader_id')
        logging.info(f"[Node {self.node_id}] acknowledges coordinator {leader}")
        self.leader_id = leader
        self.role = NodeRole.ACCEPTOR
        self.leader_last_heartbeat = time.time()
        return {'type': 'ok', "sender_id": self.node_id}

    # -----------------
    # lifecycle
    # -----------------
    async def start(self):
        self._stopping = False
        # start server
        self._server_task = asyncio.create_task(self.start_server())

        self.set_state(NodeState.UP, "Server was started.")
        # could be here to help identify and manage-availability for consensus-backoff mechanism
        # Delay heartbeat startup until server is ready
        async def delayed_heartbeat_start():
            await self.ready_event.wait()
            await asyncio.sleep(0.3)  # small buffer
            self.tasks.append(asyncio.create_task(self.heartbeat_loop()))

        # Launch the delayed heartbeat
        asyncio.create_task(delayed_heartbeat_start())
        # self.tasks.append(asyncio.create_task(self.heartbeat_loop()))

        # Only start heartbeat and election for Multi-Paxos
        if isinstance(self.strategy, MultiPaxos):
            # self.tasks.append(asyncio.create_task(self.heartbeat_loop()))
            # small startup election attempt
            await asyncio.sleep(0.2 + random_small())
            asyncio.create_task(self.start_election())

    async def stop(self):
        self._stopping = True

        self.set_state(NodeState.DOWN, "Server was stopped. No Communication.")

        if self.server:
            self.server.close()
            try:
                await self.server.wait_closed()
            except Exception:
                pass
            self.server = None

        if self._server_task:
            self._server_task.cancel()
            try:
                await self._server_task
            except asyncio.CancelledError:
                pass
            self._server_task = None

        for t in self.tasks:
            t.cancel()


# -----------------
# Utility functions
# -----------------

MSG_HDR = struct.Struct('!I')  # 4-byte length prefix

async def send_message(
    host: str,
    port: int,
    message: dict,
    timeout: float = 2.0,
    node: PaxosNode | None = None,
) -> Optional[dict]:
    """Open a TCP connection, send a JSON message with 4-byte length prefix, and wait for a JSON reply.
    Returns parsed JSON reply or None on error or timeout."""

    msg_id = message.get("msg_id") or str(uuid.uuid4())
    message["msg_id"] = msg_id

    network_logger.debug(f"SEND -> {host}:{port} id={msg_id} type={message.get('type')}")

    try:
        reader, writer = await asyncio.wait_for(asyncio.open_connection(host, port), timeout=timeout)
    except (asyncio.TimeoutError, ConnectionRefusedError, OSError) as e:
        network_logger.warning(f"[send_message] Connection to {host}:{port} failed: {e}")
        return None
    except Exception as e:
        network_logger.exception(f"[send_message] Unexpected exception: {e}")
        return None

    try:
        data = json.dumps(message).encode()
        writer.write(MSG_HDR.pack(len(data)))
        writer.write(data)
        await writer.drain()

        hdr = await asyncio.wait_for(reader.readexactly(MSG_HDR.size), timeout=timeout)
        (n,) = MSG_HDR.unpack(hdr)
        body = await asyncio.wait_for(reader.readexactly(n), timeout=timeout)
        reply = json.loads(body.decode())

        network_logger.debug(
            f"[Node {reply.get('sender_id')} -> Node {node.node_id if node else '?'}]: "
            f"RECV <- {host}:{port} type={reply.get('type')}"
        )
        return reply

    except (asyncio.TimeoutError, ConnectionResetError, OSError, json.JSONDecodeError) as e:
        network_logger.warning(f"[send_message] Error talking to {host}:{port}: {e}")
        return None
    except Exception as e:
        network_logger.exception(f"[send_message] Unexpected error: {e}")
        return None
    finally:
        # Close writer safely
        with suppress(Exception):
            writer.close()
            await writer.wait_closed()
    """
    except Exception as e:
        if node:
            print(f"Exception in send_message of Node {node.node_id}: {e}")
        # if node:
            # node.logger.warning(f"send_message({message}) ERROR to {host}:{port} -> {e}")
            #_emit_metric(node.metrics_path, node._make_event("send_error", to=f"{host}:{port}", err=str(e)))
        return None
    """
