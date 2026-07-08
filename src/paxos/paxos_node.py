from re import A
import traceback
import asyncio
import contextlib

from typing import Optional
import json
import os
import time

from enum import Enum, auto
from dataclasses import dataclass

# Logging config
import logging
import json
# from utils.networkLogger import NetworkLogger

from paxos.acceptor_storage import AcceptorStorage
from paxos.strategies.single_decree import SingleDecreePaxos
from paxos.strategies.multi_paxos import MultiPaxos
from paxos.paxos_node_interface import PaxosNodeInterface

from paxos.clock import VirtualClock
from paxos.proto.paxos_pb2 import PaxosMessage, MultiPaxosPayload, SinglePaxosPayload

from paxos.retrymanager import network_logger, send_message, RetryManager, MSG_HDR

ENABLE_SYNC=True

CONSOLE_LOG_LEVEL = logging.INFO # logging.INFO
# Log instance for low-level network events

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
    HEARTBEAT_OK = "heartbeat ok"

    ELECTION = "election"       # Only for MultiPaxos
    ELECTION_OK = "election ok" # Only for MultiPaxos
    COORDINATOR = "coordinator" # Only for MultiPaxos
    COORINATOR_OK = "coordinator ok"
    ERR = "err"
"""

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

class ElectionRole(Enum):
    FOLLOWER = auto()
    CANDIDATE = auto()
    LEADER = auto()

class NodeRole(Enum):
    ACCEPTOR = auto()
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
# Paxos Node (async)
# -----------------

class PaxosNode(PaxosNodeInterface):
    def __init__(self, 
                 node_id: int, 
                 logger, 
                 node_count: int, 
                 host: str, port: int, peers: dict, 
                 storage_path: str, strategy="single"):
        print(f"Starting PaxosNode on {host}:{port}")
        self.node_id = node_id
        self.leader_ballot = None

        self.totalnodecount = node_count
        self.state = NodeState.UP
        self.role: NodeRole = NodeRole.ACCEPTOR
        self.election_role: ElectionRole = ElectionRole.FOLLOWER
        self.last_consensus = None
        self.consensus_reached = False # Set when a new consensus is reached and immediately reset after that.
        # self.received_promises = set()
        self.received_promises = {}  # dict of proposal_id -> list of promises
        self.logger = logger # This should be instance of custom class PaxosLogger and not python in built logger.
        self.acceptance_counts = {} # Track acceptance counts for each proposal.

        self.host = host
        self.port = port
        self.peers = peers

        # mark as ready when listening
        self.ready_event = asyncio.Event()
        # use queue instead of coordinate, to get non-blocking actions
        self.proposal_queue = asyncio.Queue()

        self.logger.debug(f"[Node {node_id}] peers: {self.peers}")
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
        # self.peer_status = {}
        self.heartbeat_state = {}            # {node_id: last_success_timestamp}
        self.peer_state = {}

        for peer in self.peers:
            print(f"Peer: {peer}")
            self.peer_state[peer] = {
                'last_heartbeat': -1,
                'state': NodeState.UNKNOWN,
                'role': NodeRole.ACCEPTOR
            }

        # self.peer_state[msg.sender_id] = {
        #     'last_heartbeat': time_received,
        #     'state': NodeState[msg.state],
        #     'role': NodeRole[msg.role],
        # }
        self.heartbeat_interval = 1.0
        self.heartbeat_timeout = 3.0
        
        # treat coordination as a continous task and repeat upon failure
        self.retry_interval = 5.0

        # proposal counter
        self._proposal_counter = 0

        self.retry_manager = RetryManager()
        # syncing flags to not overload the requests
        self.synced = False
        self.sync_in_progress = False
        self.paxos_in_progress = False
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

        self.clock = VirtualClock()
        self.initialize_proposal_counter()
        self.simulated = False

        self.worker_task = asyncio.create_task(self.proposal_worker())

# -----------------
# Reconciliation Logic 
# -----------------

# --- Request sync from a specific node ---
    async def request_sync_from(self, target_node_id: int):
        """Ask another node to send us all decisions / accepted slots so we can catch up."""
        self.logger.info(f"Node {self.node_id} Sync Request send to {target_node_id}")
        # print(f"Node {self.node_id} Sync Request send to {target_node_id}")
        if self.sync_in_progress:
            self.logger.debug(f"[Node {self.node_id}] Sync already in progress, skipping duplicate request.")
            return

        self.sync_in_progress = True
        self.logger.info(f"[Node {self.node_id}] Requesting Sync from Node {target_node_id} => sync_in_progress={self.sync_in_progress}")

        self.role = NodeRole.LEARNER
        if target_node_id not in self.peers:
            self.logger.warning(f"[Node {self.node_id}] Unknown peer {target_node_id}")
            self.sync_in_progress = False
            return

        host, port = self.peers[target_node_id]
        # msg = {"type": MessageType.SYNC_REQUEST.value, "sender_id": self.node_id}
        msg = PaxosMessage(type=PaxosMessage.SYNC_REQUEST, sender_id=self.node_id)

        try:
            
            self.logger.info(f"Node {self.node_id} attempting to get SYNC_RESPONSE from Node {target_node_id}")
            resp = await send_message(host, port, msg, timeout=5, node=self)

            if resp and resp.type == PaxosMessage.SYNC_RESPONSE: # resp.get("type") == MessageType.SYNC_RESPONSE.value:
                self.logger.info(f"Node {self.node_id} got SYNC_RESPONSE: {resp}")
                # print(f"Node {self.node_id} got SYNC_RESPONSE: {resp}")
                slots = resp.slots # resp.get("slots", {})
                for slot, data in slots.items():
                    self.logger.info(f"Node {self.node_id} Slot: {slot}, Data: {data}")
                    accepted_id = data.accepted_id
                    value = data.value
                    print("HELP SYNC")
                    if self.storage.get_decision(slot) != value:
                        self.set_consensus(value, slot, accepted_id)
                self.synced = True
                self.logger.info(f"[Node {self.node_id}] Sync completed with Node {target_node_id}")
        except Exception as e:

            tb = traceback.format_exc()
            self.logger.info(f"Peer_State: {self.peer_state}")
            self.logger.warning(f"[Node {self.node_id}] Sync request to Node {target_node_id} failed: {e}")
            self.logger.error(
                f"[request_sync_from] Exception in Node {self.node_id} while sending receiving SYNC_RESPONSE"
                f"Error: {e}\n"
                f"Traceback:\n{tb}"
            )
        finally:
            self.sync_in_progress = False
# --- Handler for incoming SYNC_REQUEST ---
    async def on_sync_request(self, msg: dict) -> dict:
        """
        Respond to a SYNC_REQUEST with all known slots and their accepted IDs / values.
        """
        try:
            self.logger.info(f"[Node {self.node_id}] Received SYNC_REQUEST from Node {msg.sender_id}")
            slots_data = {}
            for slot, (accepted_id, value) in self.storage.all_accepted().items():
                slots_data[slot] = {
                    "accepted_id": accepted_id,
                    "value": value,
                    "decided": self.storage.get_decision(slot) is not None
                }
            self.logger.info(f"[Node {self.node_id}] got slots_data={slots_data}")

            if not slots_data:  # Check if there's no data to return
                self.logger.error(f"Node {self.node_id} has no accepted slots to sync!")
                return PaxosMessage(type=PaxosMessage.SYNC_RESPONSE, sender_id=self.node_id, slots={})
            return PaxosMessage(type=PaxosMessage.SYNC_RESPONSE, sender_id=self.node_id, slots=slots_data)
        except Exception as e:
            self.logger.error(f"Node {self.node_id} on_sync_request Error: ", e)
# -----------------
# Availability Logic 
# -----------------
    async def handle_peer_revival(self, peer_id):
        if self.state == NodeState.BLOCKED and self.has_quorum():
            self.logger.info(f"[Node {self.node_id}] Quorum restored; Node {peer_id} revived; unblocking proposer.")
            self.set_state(NodeState.UP, "quorum restored")
    
    async def send_heartbeat(self, nid, host, port, now):
        # print(f"Sending Heartbeat... nid: {nid}, host: {host}, {port}, {now}")
        if nid == self.node_id:
            return
        
        self.logger.debug(f"Node {self.node_id} Sending heartbeat to Node {nid} -> {host}:{port} at {now}")
        # print(f"Node {self.node_id} Sending heartbeat to Node {nid} -> {host}:{port} at {now}")
        proposal_id = self.storage.get_latest_proposal_id()
        # print(f"Node {self.node_id} got {proposal_id} from storage.")
        known_slots = self.storage.get_known_slots()
        # --- Send heartbeat and check connectivity ---
        msg = PaxosMessage(
            type=PaxosMessage.HEARTBEAT,
            sender_id=self.node_id,
            proposal_id=proposal_id,
            known_slots=known_slots,
            state=self.state.name,
            role=self.role.name,
            leader_id=self.leader_id or -1,
            timestamp=now,
        )                
        self.logger.debug(f"[Node {self.node_id}] SEND HEARTBEAT highest_proposal_id={msg.proposal_id}, known_slots={msg.known_slots}")
        try:
            reply = await send_message(host, port, msg, timeout=20, node=self)
            if reply is not None:
                # Mark peer as alive and update last heartbeat timestamp
                self.heartbeat_state[nid] = now
                if self.peer_state[nid] != None and self.peer_state[nid]['state'] != NodeState.UP:
                    self.peer_state[nid]['state'] = NodeState.UP
                    # print(f"Peer {nid}: {self.peer_state[nid]}")
                    self.logger.debug(f"Peer {nid} marked UP (heartbeat OK)")
                    print(f"Peer {nid} marked UP (heartbeat OK)")
                    await self.handle_peer_revival(nid)
            else:
                # No reply — may be temporarily unreachable
                last = self.heartbeat_state.get(nid, 0)
                if now - last > self.heartbeat_timeout:
                    if self.peer_state[nid] != None and self.peer_state[nid]['state'] != NodeState.DOWN:
                        self.peer_state[nid]['state'] = NodeState.DOWN
                        self.logger.warning(f"Peer {nid} marked DOWN (no heartbeat reply)")
                        print(f"Peer {nid} marked DOWN (no heartbeat reply)")

                        # if a peer has been detected that is down and the leader, try to reelect with remaining peers
                        if nid == self.leader_id:
                            print("Peer is supposed to be the leader but is DOWN -> start_election...")
                            await self.start_election()

        except Exception as e:
            print(f"Could not send Heartbeat to nid: {nid}, host: {host}, port: {port}")
            self.logger.error(f"Error: {e}")
            # Connection or unexpected error — treat as potential failure
            last = self.heartbeat_state.get(nid, 0)
            if now - last > self.heartbeat_timeout:
                if nid in self.peer_state and self.peer_state[nid] != None and self.peer_state[nid]['state'] != NodeState.DOWN:
                    self.peer_state[nid]['state'] = NodeState.DOWN
                    self.logger.warning(f"Peer {nid} marked DOWN (exception: {e})")

                    # if a peer has been detected that is down and the leader, try to reelect with remaining peers
                    if nid == self.leader_id:
                        print("Peer is supposed to be the leader but is DOWN -> start_election...")
                        await self.start_election()

    async def heartbeat_loop(self):
        """Periodically ping peers and update their UP/DOWN status."""
        # if isinstance(self.strategy, MultiPaxos):
        #    return  # MultiPaxos handles heartbeats differently
        print(f"Node {self.node_id} Heart-start!")
        print(f"Heartbeat loop started Node {self.node_id}. self._stopping? {self._stopping}",)
        print(f"self.peers? {self.peers}",)

        try:
            while not self._stopping:
                now = self.clock.now() # time.time()
                for nid, (host, port) in self.peers.items():
                    # print(f"Node {self.node_id} Heart to Node {nid}!")

                    # if nid in self.peer_state and self.peer_state[nid].state == NodeState.UP:
                    await self.send_heartbeat(nid, host, port, now)

                await asyncio.sleep(self.heartbeat_interval)
        except Exception as e:
            tb = traceback.format_exc()

            print(self._stopping)
            print(f"Exception: {e}", f"Traceback:\n{tb}")
            self.logger.info(f"Peer_State: {self.peer_state}")
            self.logger.error(
                f"[heartbeat_loop] Exception in Node {self.node_id} while sending HEARTBEAT"
                f"Error: {e}\n"
                f"Traceback:\n{tb}"
            )

        self.lpgger.info(f"HEARTBEAT LOOP STOPPED.")

    async def on_heartbeat(self, msg: PaxosMessage) -> dict:
        time_received = self.clock.now() # time.time()

        self.logger.debug(f"Node {self.node_id} received Heartbeat from Node {msg.sender_id}")
        self.logger.debug(f"Node {self.node_id} -> {msg}")

        # print(f"Node {self.node_id} received Heartbeat from Node {msg.sender_id}")

        if msg.leader_id is not None:
            self.leader_id = msg.leader_id
            self.leader_last_heartbeat = time_received

        # Update liveness
        if msg.sender_id:
            self.peer_state[msg.sender_id] = {
                'last_heartbeat': time_received,
                'state': NodeState[msg.state],
                'role': NodeRole[msg.role],
            }
            self.logger.debug(f"Node {self.node_id} updated peer status of Node {msg.sender_id}: {self.peer_state[msg.sender_id]}")
            self.logger.debug(f"Node {self.node_id} peer.status: {self.peer_state}")
            self.logger.info(f"Node {self.node_id} peer.status: {self.peer_state}")

        
        require_sync = False #default

        # print("Figuring out if this Node requires Syncing...")
        


        # last_decision = self.storage.get_last_decision()
        latest = self.storage.get_latest_proposal_id()
        last_decision = self.storage.get_known_slots()
        my_pid = latest if latest is not None else 0

        self.logger.info(f"Last Decision: {last_decision}")


        if not last_decision:
            # print("NOT last_decision")
            require_sync = not self.paxos_in_progress and msg.proposal_id>my_pid # and msg.proposal_id > my_pid
            self.logger.debug(f"Node {self.node_id} Heartbeat from Node {msg.sender_id} with proposal_id: {msg.proposal_id}, my_pid: {my_pid}, checking if reconciliation is required...require_sync?{require_sync}")
            self.logger.info(
                f"[Node {self.node_id}] Detected higher proposal ID "
                f"{msg.proposal_id} from Node {msg.sender_id}"
                f"because msg.proposal_id>my_pid => {msg.proposal_id}>{my_pid} "
            )

        if last_decision:
            # print("last_decision")
            _, _, pid = last_decision
            require_sync = not self.paxos_in_progress and msg.proposal_id>latest # pid # and msg.proposal_id > my_pid
            self.logger.info(f"msg.proposal_id: {msg.proposal_id} > latest: {latest}")
            self.logger.info(f"msg.proposal_id: {msg.proposal_id} > pid: {pid}")
            self.logger.info(f"Node {self.node_id} Heartbeat from Node {msg.sender_id} with proposal_id: {msg.proposal_id}, pid: {pid}, checking if reconciliation is required...require_sync?{require_sync}")
            self.logger.info(
                f"[Node {self.node_id}] Detected higher proposal ID "
                f"{msg.proposal_id} from Node {msg.sender_id}"
                f"because msg.proposal_id>pid => {msg.proposal_id}>{pid} "
            )

        # print(f"Node {self.node_id} received Heartbeat from Node {msg.sender_id}, requireSync?: {require_sync}")

        if require_sync and ENABLE_SYNC:
            print(f"Node {self.node_id} requires_sync from sender: {msg.sender_id}!")
            await self.request_sync_from(msg.sender_id)
        return PaxosMessage(type=PaxosMessage.HEARTBEAT_OK, sender_id=self.node_id) # {'type': 'heartbeat_ok', 'sender_id': self.node_id}

    def check_cluster_health(self) -> None:
        if not self.has_quorum():
            if self.state == NodeState.UP:
                self.set_state(NodeState.BLOCKED, "lost majority connectivity")
        elif self.state == NodeState.BLOCKED:
            self.set_state(NodeState.UP, "quorum restored")

    def has_quorum(self) -> bool:
        up_count = sum(1 for s in self.peer_state.values() if s["state"] == NodeState.UP)
        return (up_count + 1) >= (len(self.peers) // 2 + 1)  # +1 = self
# -----------------
# Coordinator logic (multi-paxos with Leader or Single Paxos Proposer)
# -----------------
    async def proposal_worker(self):
        while True:
            self.logger.info(f"Proposal Worker retrieving proposition for proposal queue and coordinating. The current strategy is: {self.strategy}")
            value, slot = await self.proposal_queue.get()
            try:
                await self.coordinate(value, slot)
            except Exception as e:
                self.logger.error(f"Error coordinating proposal: {e}")
            finally:
                self.proposal_queue.task_done()   

    async def coordinate_forever(self, value, slot):
        while not self._stopping:
            result = await self.coordinate(value, slot)
            if result:
                self.logger.info("Consensus achieved!")
                break

            # Check if state changed — maybe quorum restored
            if self.state == NodeState.BLOCKED:
                self.logger.info("Still blocked, will retry after cooldown...")
                await asyncio.sleep(self.retry_interval)
            elif self.state == NodeState.DOWN:
                self.logger.warning("Node down; waiting for recovery...")
                await asyncio.sleep(self.retry_interval)
            else:
                self.logger.debug("Retrying coordinate round...")
                await asyncio.sleep(self.retry_interval)

    async def prepare_self(self, proposal):
        self.roles = []
        if NodeRole.PROPOSER not in self.roles:
            self.roles.append(NodeRole.PROPOSER)
        if NodeRole.ACCEPTOR not in self.roles:
            self.roles.append(NodeRole.ACCEPTOR)

        prepare_msg = PaxosMessage(
            type=PaxosMessage.PREPARE,
            sender_id=self.node_id,
            proposal_id=proposal.proposal_id,
            multi=MultiPaxosPayload(
                slot=proposal.slot,
                value=proposal.value,
                ok=False  # typically False for prepare phase
            ),
            # slot=proposal.slot,
            # value=proposal.value,
            leader_id=self.leader_id or -1,
            timestamp=self.clock.now(),  # logical time
        )

        # 🟣 1️⃣ Handle self as an acceptor (loopback)
        try:
            self.logger.info("Creating Local Promise...")
            # act as acceptor for our own prepare
            local_promise = await self.on_prepare(prepare_msg)
            self.logger.info(f"Local Promise (counting self): {local_promise}")

            # if local_promise and local_promise.get("type") == MessageType.PROMISE.value:
            if local_promise and local_promise.type == PaxosMessage.PROMISE:
                self.receive_promise(local_promise)
                self.logger.debug(f"[Node {self.node_id}] Counted self PROMISE for proposal {proposal.proposal_id}")
            elif local_promise and local_promise.type == PaxosMessage.ERR:

                self.logger.info(f"Received Local Error, indicating we need to increase our proposal_id: {proposal.proposal_id}")
                self.logger.info(f"proposal: {proposal}")
                self.logger.info(f"local_promise: {local_promise}")


                print(f"Received Local Error, indicating we need to increase our proposal_id: {proposal.proposal_id}")
                print(f"proposal: {proposal}")
                print(f"local_promise: {local_promise}")
                if (
                    isinstance(self.strategy, MultiPaxos)
                    and self.leader_id == self.node_id
                    and self.leader_ballot is not None
                ):
                    print(f"I am the leader (current_ballot = {self.leader_ballot}), a proposal is being rejected by proposal_id, which means i need to increase my leader_ballot!")
                    self.leader_ballot = self.next_proposal_id()
                    proposal.proposal_id = self.leader_ballot
                    print(f"I am the leader, setting my proposal_id to my leader_ballot: {self.leader_ballot}")
                else:

                    print(f"I am the leader, setting my proposal_id to my leader_ballot: {self.leader_ballot}")
                    proposal.proposal_id = self.next_proposal_id()
                print(f"Incremented proposal.id: {proposal.proposal_id}")
                resp = await self.prepare_self(proposal)
                return resp

        except Exception as e:
            self.logger.error(f"[Node {self.node_id}] Error during self-promise handling: {type(e).__name__}: {e}")
            self.logger.debug(traceback.format_exc())

    async def send_fast_path(self, leader, value, slot):
        """
        Send leader forwarded proposition in an attempt for him to skip the prepare phase
        """
        self.logger.debug(f"inside send_fast_path... leader={leader}, value={value}, slot={slot}")
        degraded = True # default
        proposal = Proposal(
            node_id=self.node_id,
            proposal_id=-1, # leader.leader_ballot,
            value=value,
            slot=slot
        )

        self.logger.debug(f"inside send_fast_path proposal={proposal}")

        fast_path_msg = PaxosMessage(
            type=PaxosMessage.FAST_PATH,
            sender_id=self.node_id,
            proposal_id=proposal.proposal_id,
            multi=MultiPaxosPayload(
                slot=proposal.slot,
                value=proposal.value,
                ok=True
            ),
            leader_id=self.leader_id or -1,
            timestamp=self.clock.now(),  # logical time
        )

        host, port = leader[0], leader[1]
        if self.leader_id != -1 and self.leader_id in self.peer_state:
            leader_state = self.peer_state[self.leader_id]
            self.logger.info(f"send_fast_path to {host}:{port} -> state: {leader_state}")
            if leader_state["state"] == NodeState.DOWN:
                await self.start_election()

        self.logger.info(f"inside send_fast_path sending to: host={host}, port={port}")
        try:
            resp = await self.retry_manager.run(
                lambda: send_message(host, port, fast_path_msg, timeout=0.5 if degraded else 2.0, node=self),
                retries=1 if degraded else 5,
                base_delay=0.5,
                max_delay=4.0
            )

            if not resp:
                self.logger.info(f"Did not receive a response to my proposal from Node {self.leader_id} at {host}:{port}")
                self.logger.info(f"If Fast_path_did not get a response, try reelection....")
                asyncio.create_task(self.start_election())
                return


            if resp.type == PaxosMessage.FAST_PATH_OK:
                self.logger.debug("FAST_PATH_OK RECEIVED! Good, the leader will handle the coordination.")
            """
            elif resp.type == PaxosMessage.ERR:
                self.logger.error(f"Received PaxosMessage.ERR")
                self.logger.error(f"Received Error adopting value:{resp.multi.value!r}")
                self.logger.error(f"Received Error adopting higher id:{resp.multi.accepted_id!r}")
                
                print(f"Received PaxosMessage.ERR")
                print(f"Received Error adopting value:{resp.multi.value}\n")
                print(f"Received Error adopting higher id:{resp.multi.accepted_id}")
                
                if resp.multi.accepted_id is not None:
                        adopted_id = resp.multi.accepted_id + 1
                        proposal.proposal_id = adopted_id
                        self.logger.info(f"Overrode proposal_id of proposal: {proposal}")
                else:
                    self.logger.info("Could not adjust proposal_id")

                # Only adopt value if it exists (not empty string)
                if resp.multi.value is not None:# and resp.multi.value != '':
                    adopted_value = resp.multi.value
                    proposal.value = adopted_value
                    self.logger.info(f"Overrode value of proposal: {proposal}")
                else:
                    self.logger.info("Received value for already decided slot was empty, couldnt adopt value")
            """
        except Exception as e:
            self.logger.warning(f"[Node {self.node_id}] Failed FAST_PATH to {self.leader_id}: {e}")

    async def on_fast_path(self, paxosmsg):
        """
        Receive Fast_path from peer that is not the leader in multi-paxos allowing self (leader) to skip prepare phase 
        """
        self.logger.info(f"received fast_path from {paxosmsg.sender_id}, am i the leader? -> {self.node_id == self.leader_id}")
        if self.node_id == self.leader_id:
            await self.coordinate(paxosmsg.multi.value, paxosmsg.multi.slot, skip_prepare=True)
            return PaxosMessage(
                type=PaxosMessage.FAST_PATH_OK, 
                proposal_id=self.leader_ballot, 
                slot=paxosmsg.slot, 
                sender_id=self.node_id
            )
        else:
            self.logger.warning("Received Fast_Path Message but I am not a leader! Returning Rejection. This should never happen.")
            return PaxosMessage(
                type=PaxosMessage.REJECT, 
                proposal_id=-1, 
                slot=paxosmsg.slot, 
                sender_id=self.node_id
            )


    def on_fast_path_ok(self, paxosmsg):
        """
        acknowledges fast_path receive
        """
        print(f"Node {self.node_id} received fast_path_ok! Good Leader will coordinate the value proposition.")

    async def coordinate(self, value, slot, skip_prepare=False):
        """
        Run Paxos (prepare -> accept -> learn) for a given value.
        Called by the leader or proposer.
        """
        print(f"Running Coordinate with: [value, slot, skip_prepare] = [{value}, {slot}, {skip_prepare}]")
        if self.state == NodeState.DOWN:
            self.logger.error("Node is DOWN, cannot coordinate.")
            return None

        if self.state == NodeState.BLOCKED:
            self.logger.warning("Node is BLOCKED, ignoring coordinate request.")
            return None

        self.logger.info(f"Node {self.node_id} Coordinate!")
        self.logger.info(f"Current Strategy: {self.strategy}")

        if isinstance(self.strategy, SingleDecreePaxos):
            if self.strategy.chosen_value is not None:
                return True
        elif isinstance(self.strategy, MultiPaxos):
            self.logger.info("MultiPaxos redirect should happen here... identify the leader and send him your suggested value for a slot!")
            if self.leader_id == -1:
                await(self.start_election())

            if self.leader_id and self.node_id != self.leader_id:
                leader = self.peers[self.leader_id]
                self.logger.info(f"Identified Leader -> {leader}. Attempting to forward proposition...")
                await self.send_fast_path(leader, value, slot)
                return False

        if self.leader_id == self.node_id:
            if not self.leader_ballot:
                proposal_id = self.next_proposal_id()
            else:
                proposal_id = self.leader_ballot
        else:
            proposal_id = self.next_proposal_id()

        self.logger.info(f"Node {self.node_id} next_proposal_id: {proposal_id}")
        self.t0 = time.perf_counter()
        
        proposal = Proposal(
            self.node_id, 
            proposal_id, 
            value, 
            slot
        )

        # either send self a prepare to treat it the same or count + 1 during promise evaluation
        if not skip_prepare:
            print("NOT SKIPPING PREPARE PHASE (NO MULTI PAXOS LEADER)")

            # -----------------
            # Phase 1: Prepare
            # -----------------
            self.logger.info(f"Node {self.node_id} send prepare to {self.peers.items()}!")

            print("---"*15)
            print("---"*5, "PREPARE", "---"*5)
            print("---"*15)

            proposal = await self.send_prepare(self.peers.items(), proposal)

            if not proposal:
                raise Exception("After Prepare proposal wasn't returned...")

            print("---"*15)
            print("---"*5, "PREPARE", "---"*5)
            print("---"*15)

            print(f"Proposal after sending each peer a prepare: {proposal}")
            print("---"*15)

            self.logger.info(f"Node {self.node_id} Proposal after send_prepare: {proposal}")

            if not self.decide_on_promises_received(proposal):
                print("Decide on Promises Received returned False")
                return False

            print("RECEIVED ENOUGH PROMISES")

            print("---"*15)
            print("---"*5, "ACCEPT", "---"*5)
            print("---"*15)
            # -----------------
            # Phase 2: Accepted
            # -----------------
            self.logger.info(f"Sending Accept-Paxos-Msg with proposal: {proposal}, slot:{proposal.slot}, value: {proposal.value}")

            print(f"Sending Accept-Paxos-Msg with proposal: {proposal}, slot:{proposal.slot}, value: {proposal.value}")
            accepted_count = await self.send_accept(self.peers.items(), proposal)

            self.logger.info(f"Node {self.node_id} got {accepted_count} acceptances from peers!")
            quorum = len(self.peers) // 2 + 1
            if accepted_count < quorum:
                # _emit_metric(self.metrics_path, self._make_event("coordinate_failed", proposal_id=proposal_id, slot=slot, reason="not_enough_promises"))
                
                self.logger.info(f"Node {self.node_id} failed to get majority of acceptances ({accepted_count}<{quorum}==False) with peers!")
                self.set_state(NodeState.BLOCKED, "failed to get majority accepts")                       # Could not reach majority quorum
                return None
            

            self.logger.info(f"Node {self.node_id} successfully got majority of acceptances ({accepted_count}<{quorum}==True) with peers!")
            # if we are here, we have reached consensus

            # -----------------
            # Phase 3: Learn
            # -----------------
            print("---"*15)
            print("---"*5, "LEARN", "---"*5)
            print("---"*15)
            # Success — learned value
            self.set_state(NodeState.UP, "achieved quorum, decision made")
            print("HELP COORDINATE")
            self.set_consensus(proposal.value, proposal.slot, proposal.proposal_id)
            
            self.logger.info(f"Node {self.node_id} sending learn messages to peers!")
            ack_learn_count = await self.send_learn(self.peers.items(), proposal)
            self.logger.info(f"Node {self.node_id} got #learn_ack={ack_learn_count}.")

            self.logger.info(f"Consensus reached, saving logs to CSV for Node {self.node_id}.")
            # input("SAVE")

            return True
        else:
            print("SKIPPING PREPARE PHASE (AS MULTI PAXOS LEADER; USE LEADER_BALLOT FOR DECISIONS)")
            print("Fast foward coordinate, leader_ballot should be set (if not set it when a leader has been chosen) and it should be bigger than any proposal_id seen before..")

            print("---"*15)
            print("---"*5, "FAST_PATH_MULTI_PAXOS (with LEADER avail...)", "---"*5)
            print("---"*15)
            self.logger.info(f"Node {self.node_id} is the leader and received fast_forward proposal from peer, skip prepare and going to phase 2 immediately...")
            if not self.leader_ballot and isinstance(self.strategy, MultiPaxos):

                print("LEADER BALLOT NOT SET!")
                raise ValueError("Leader Ballot not defined! This should not be the case, a leader should get a Leader Ballot definition on successfully getting elected!")

            print("---"*15)
            print("---"*5, "ACCEPT", "---"*5)
            print("---"*15)
            # -----------------
            # Phase 2: Accepted
            # -----------------
            self.logger.info(f"Sending Accept-Paxos-Msg with proposal: {proposal}, slot:{proposal.slot}, value: {proposal.value}")

            print(f"Sending Accept-Paxos-Msg with proposal: {proposal}, slot:{proposal.slot}, value: {proposal.value}")
            accepted_count = await self.send_accept(self.peers.items(), proposal)

            self.logger.info(f"Node {self.node_id} got {accepted_count} acceptances from peers!")
            quorum = len(self.peers) // 2 + 1
            if accepted_count < quorum:
                # _emit_metric(self.metrics_path, self._make_event("coordinate_failed", proposal_id=proposal_id, slot=slot, reason="not_enough_promises"))
                
                self.logger.info(f"Node {self.node_id} failed to get majority of acceptances ({accepted_count}<{quorum}==False) with peers!")
                self.set_state(NodeState.BLOCKED, "failed to get majority accepts")                       # Could not reach majority quorum
                return None
            

            self.logger.info(f"Node {self.node_id} successfully got majority of acceptances ({accepted_count}<{quorum}==True) with peers!")
            # if we are here, we have reached consensus

            # -----------------
            # Phase 3: Learn
            # -----------------
            print("---"*15)
            print("---"*5, "LEARN", "---"*5)
            print("---"*15)
            # Success — learned value
            self.set_state(NodeState.UP, "achieved quorum, decision made")
            print("HELP COORDINATE")
            self.set_consensus(proposal.value, proposal.slot, proposal.proposal_id)
            
            self.logger.info(f"Node {self.node_id} sending learn messages to peers!")
            ack_learn_count = await self.send_learn(self.peers.items(), proposal)
            self.logger.info(f"Node {self.node_id} got #learn_ack={ack_learn_count}.")

            self.logger.info(f"Consensus reached, saving logs to CSV for Node {self.node_id}.")
            # input("SAVE")

            return True
        return False
    async def send_prepare(self, nodes, proposal: Proposal) -> Proposal:
        """
        Send PREPARE for a given slot to all peers.
        If a quorum reports an existing accepted value, adopt it.
        Always return the updated proposal.
        """
        print(f"[Node {self.node_id}] send PREPARE for slot {proposal.slot}... -> {proposal}")

        self.role = NodeRole.PROPOSER

        # Track highest accepted_id and value seen
        adopted_value = None
        responses = []

        for nid, (host, port) in nodes:

            self.log_action(
                action="SEND_PREPARE",
                action_value=f"promised_id={proposal.proposal_id}",
                target_node_id=str(nid),
                target_node_role=self.peer_state[nid]['role'].name if nid in self.peer_state else NodeRole.ACCEPTOR.name,# self.role.name, # "PROPOSER",
                target_node_state=self.peer_state[nid]['state'].name if  nid in self.peer_state else NodeState.UNKNOWN# self.state, # NodeState.UP
            )
            degraded = True  # default
            if nid in self.peer_state:
                peer_state = NodeState(self.peer_state[nid]['state'])
                if peer_state != NodeState.DOWN:
                    degraded = False

            prepare_msg = PaxosMessage(
                type=PaxosMessage.PREPARE,
                sender_id=self.node_id,
                proposal_id=proposal.proposal_id,
                multi=MultiPaxosPayload(
                    slot=proposal.slot,
                    value=proposal.value,
                    ok=False
                ),
                leader_id=self.leader_id or -1,
                timestamp=self.clock.now(),
            )

            try:
                resp = await self.retry_manager.run(
                    lambda: send_message(host, port, prepare_msg, timeout=0.5 if degraded else 2.0, node=self),
                    retries=1 if degraded else 5,
                    base_delay=0.5,
                    max_delay=4.0
                )

                if not resp:
                    print(f"Did not receive a response to my proposal from Node {nid} at {host}:{port}")
                    continue

                responses.append(resp)

                if resp.type == PaxosMessage.PROMISE:
                    self.logger.debug(f"Received promise from Node {resp.sender_id}")
                    print(f"Received promise from Node {resp.sender_id}")
                elif resp.type == PaxosMessage.ERR:
                    self.logger.error(f"Received PaxosMessage.ERR")
                    self.logger.error(f"Received Error adopting value:{resp.multi.value!r}")
                    self.logger.error(f"Received Error adopting higher id:{resp.multi.accepted_id!r}")
                    
                    print(f"Received PaxosMessage.ERR")
                    print(f"Received Error adopting value:{resp.multi.value}\n")
                    print(f"Received Error adopting higher id:{resp.multi.accepted_id}")

                    if (
                        isinstance(self.strategy, MultiPaxos)
                        and self.leader_id == self.node_id
                        and self.leader_ballot is not None
                    ):
                        print(f"I am the leader (current_ballot = {self.leader_ballot}), a proposal is being rejected by proposal_id, which means i need to increase my leader_ballot!")
                        self.leader_ballot = self.next_proposal_id()
                        proposal.proposal_id = self.leader_ballot
                        print(f"I am the leader, setting my proposal_id to my leader_ballot: {self.leader_ballot}")
                    else:

                        print(f"I am the leader, setting my proposal_id to my leader_ballot: {self.leader_ballot}")
                        proposal.proposal_id = self.next_proposal_id()
                    """
                    if resp.multi.accepted_id is not None:
                         adopted_id = resp.multi.accepted_id + 1
                         proposal.proposal_id = adopted_id
                         print(f"Overrode proposal_id of proposal: {proposal}")
                    else:
                        print("Could not adjust proposal_id")
                    # Only adopt value if it exists (not empty string)
                    if resp.multi.value is not None:# and resp.multi.value != '':
                        adopted_value = resp.multi.value
                        proposal.value = adopted_value
                        print(f"Overrode value of proposal: {proposal}")
                    else:
                        print("Received value for already decided slot was empty, couldnt adopt value")
                    """
                    # Retry
                    return await self.send_prepare(nodes, proposal)

            except Exception as e:
                self.logger.warning(f"[Node {self.node_id}] Failed PREPARE to {nid}: {e}")
                continue

        for resp in responses:
            self.receive_promise(resp)   # ⬅️ refactored

        return proposal
    def receive_prepare(self, proposal: Proposal):
        """
        Handle incoming PREPARE message (ACCEPTOR side).
        """
        print("---"*5, f"RECEIVE_PREPARE NODE {self.node_id}", "---"*5)
        promised = self.storage.get_promised(proposal.slot)
        promised = 0 if not promised else promised
        latest = self.storage.get_latest_proposal_id()
        latest = 0 if not latest else latest

        self.log_action(
            action="RECEIVE_PREPARE",
            action_value=f"promised_id={proposal.proposal_id}",
            target_node_id=str(proposal.node_id),
            target_node_role=self.role.name, # "PROPOSER",
            target_node_state=self.state, # NodeState.UP
        )

        if promised is None or (proposal.proposal_id > promised and proposal.proposal_id > latest): # getattr(self, "max_seen_proposal", -1)):
            self.max_seen_proposal = proposal.proposal_id
            return self.send_promise(proposal)

    async def send_accept(self, nodes, proposal: Proposal):
        """
        After Prepare -> Send Accept 
        """
        print(f"Sending Accept message with proposal: {proposal}")
        accept_msg = PaxosMessage(
            type=PaxosMessage.ACCEPTED, 
            proposal_id=proposal.proposal_id, 
            multi=MultiPaxosPayload(
                slot=proposal.slot,
                value=proposal.value,
                ok=False,  # typically False for prepare phase
            ),
            sender_id=self.node_id,
        )
        accepted_count = 1  # self accepts

        for nid, (host, port) in nodes:
            degraded = False
            if nid in self.peer_state:
                peer_state = NodeState(self.peer_state[nid]['state'])
                if peer_state == NodeState.DOWN:
                    self.logger.warning(f"[Node {self.node_id}] Peer {nid} is DOWN — trying lightweight accept anyway.")
                    degraded = True
                elif peer_state == NodeState.UP:
                    degraded = False
            else:
                degraded = True
            try:

                self.log_action(
                    action="SEND_ACCEPT",
                    action_value=f"proposal_id={proposal.proposal_id}, value={proposal.value}",
                    target_node_id=nid,
                    target_node_role=self.peer_state[nid]["role"].name, # "ACCEPTOR",
                    target_node_state=self.peer_state[nid]['state'].name# NodeState.UP
                )
                # _emit_metric(self.metrics_path, self._make_event("SEND " + MessageType.ACCEPTED.value, proposal_id=proposal_id, slot=slot, value=value))

                # Send accept request to peer
                resp = await self.retry_manager.run(
                    lambda: send_message(host, port, accept_msg, timeout=0.5 if degraded else 2.0, node=self),
                    retries=1 if degraded else 5,
                    base_delay=1.0,
                    max_delay=10.0,
                )
                # resp = await send_message(host, port, accept_msg, 2, self)

                # If response is a PROMISE, handle it separately
                if resp and resp.type == PaxosMessage.ACCEPTED: # resp.get("type") == MessageType.ACCEPTED.value:
                    accepted_count += 1
                elif resp:
                    self.logger.warning(f"On Send Accept got wrong response: {resp}")

            except Exception as e:
                self.logger.error(f"Exception in send_accept of Node {self.node_id}: {e}")

        return accepted_count

    def send_promise(self, proposal):
        """
        Send PROMISE message back to proposer.
        """
        # accepted_slot, accepted_id, accepted_value = self.storage.accepted_with_slot(proposal.slot)
        print("---"*5,  "CHECK_GET_PROMISED", "---"*5)
        promised = self.storage.get_promised(proposal.slot)
        print(f"self.storage.get_promised(proposal.slot) = {promised} at slot: {proposal.slot}")

        print("---"*5,  "CHECK_GET_ACCEPTED", "---"*5)
        accepted = self.storage.get_accepted(proposal.slot)
        print(f"self.storage.get_accepted(proposal.slot) = {accepted} at slot: {proposal.slot}")


        accepted_id, accepted_value = self.storage.accepted(proposal.slot)
        print(f"Sending back promise to proposal: {proposal} with slot, id, value: {proposal.slot}, {accepted_id}, {accepted_value}")
        self.log_action(
            action="SEND_PROMISE",
            action_value=f"promised_id={proposal.proposal_id}",
            target_node_id=proposal.sender_id,
            target_node_role=self.peer_state[proposal.sender_id]['role'].name,# "PROPOSER",
            target_node_state=self.peer_state[proposal.sender_id]['state'].name, # NodeState.UP
        )
        promise_msg = PaxosMessage(type=PaxosMessage.PROMISE, proposal_id=proposal.proposal_id, multi=MultiPaxosPayload(value=accepted_value or None, accepted_id=accepted_id or 0, slot=accepted_slot, ok=True), sender_id=self.node_id)
        return promise_msg

    def receive_promise(self, promise):
        """
        Handle incoming PROMISE message (PROPOSER side).
        """
        try:
            # Store promises for this round
            proposal_id = promise.proposal_id
            if proposal_id not in self.received_promises:
                self.logger.info(f"Node {self.node_id}: Adding pid={proposal_id}-list to received_promises.")
                self.received_promises[proposal_id] = []
            self.logger.info(f"Appending Promise to proposal_id={proposal_id}-list.")
            

            self.log_action(
                action="RECEIVE_PROMISE",
                action_value=f"proposal_id={proposal_id}, value={promise.multi.value}",
                target_node_id=str(self.node_id), # promise.sender_id, # ['sender_id'],
                target_node_role=self.role.name, # self.peer_state[promise.sender_id]['role'].name if promise.sender_id != self.node_id else self.role.name,# "ACCEPTOR",
                target_node_state=self.state.name,# self.peer_state[promise.sender_id]['state'].name if promise.sender_id != self.node_id else self.state.name, # ['sender_id']] # NodeState.UP
                consensus_reached=False
            )
            self.received_promises[proposal_id].append(promise)

            quorum_size = len(self.peers) // 2 + 1
            self.logger.info(f"Required Quorum: {quorum_size}")
            promises = self.received_promises[proposal_id]
            self.logger.info(f"Received-Promises: {len(promises)}, {promises}")

            if len(promises) >= quorum_size and self.state == NodeState.BLOCKED:
                self.set_state(NodeState.UP, "quorum restored during prepare phase")

        except Exception as e:
            # Capture traceback
            tb = traceback.format_exc()

            # Log detailed error with context
            self.logger.error(
                f"[receive_promise] Exception in Node {self.node_id} while handling "
                f"promise from sender_id={getattr(promise, 'sender_id', 'UNKNOWN')} "
                f"for proposal_id={getattr(promise, 'proposal_id', 'UNKNOWN')}.\n"
                f"Error: {e}\n"
                f"Traceback:\n{tb}"
            )

            # Optional: re-raise if the failure should bubble up
            # raise
            raise e

    async def send_learn(self, nodes, proposal: Proposal) -> int:
        learn_msg = PaxosMessage(
            type=PaxosMessage.LEARN, 
            proposal_id=proposal.proposal_id, 
            multi=MultiPaxosPayload(value=proposal.value, slot=proposal.slot),
            slot=proposal.slot, 
            sender_id=self.node_id
        )
        ack_count = 1 # assuming self agreed (TODO)

        print(f"Node {self.node_id} send Learn! {learn_msg}")
        # input()
        for nid, (host, port) in nodes:

            self.logger.info(f"[Node {self.node_id}] Send LEARN: {nid}: {(host, port)}" )

            self.log_action(
                action="SEND_LEARN",
                action_value=f"value={learn_msg.multi.value}",
                target_node_id=nid,
                target_node_role=self.peer_state[nid]['role'].name, # "LEARNER",
                target_node_state=self.peer_state[nid]['state'].name, # NodeState.UP
                consensus_reached=True
            )
            resp = await self.retry_manager.run(
                lambda: send_message(host, port, learn_msg, timeout=2, node=self),
                retries=5,
                base_delay=1.0,
                max_delay=10.0,
            )
            # resp = await send_message(host, port, learn_msg, 2, self)
            if not resp:
                self.peer_state[nid]['state'] = NodeState.DOWN 
                continue

            if resp.type == PaxosMessage.LEARN_OK: # resp['type'] == MessageType.LEARN_SUCC.value:
            # if (self.receive_learn(resp)):

                self.log_action(
                    action="RECEIVE_LEARN_OK",
                    action_value=f"value={resp.multi.value}",
                    target_node_id=self.node_id,
                    target_node_role=self.role.name,# self.peer_state[resp.sender_id]['role'].name, # "LEARNER",
                    target_node_state=self.state.name,# self.peer_state[resp.sender_id]['state'].name, # NodeState.UP
                    consensus_reached=True
                )
                ack_count += 1
                self.logger.debug(f"Received acknowledgement. ack_count={ack_count}")
        return ack_count

    def _msg_slot(self, msg) -> int:
        """
        Return the slot number carried by a PaxosMessage. Normalizes between
        msg.slot and msg.multi.slot. Prefer msg.multi.slot if present.
        """
        try:
            # prefer multi.slot if present and not None/0 (0 might be used as default)
            if getattr(msg, "multi", None) is not None:
                s = getattr(msg.multi, "slot", None)
                if s is not None:
                    return int(s)
        except Exception:
            pass

        # fallback to msg.slot
        s2 = getattr(msg, "slot", None)
        if s2 is None:
            raise ValueError("Message does not contain slot")
        return int(s2)
    """
    defined receive_learn(self, proposal: Proposal) -> dict:
        self.role = NodeRole.LEARNER

        # if proposal.proposal_id > self.storage.get_highest_less_than_n()
        # Update acceptor storage
        print(f"Node {self.node_id}, Received learn: {proposal}")
        self.storage.set_accepted(proposal.slot, proposal.proposal_id, proposal.value)
        print("HELP LEARN")
        self.set_consensus(proposal.value, proposal.slot, proposal.proposal_id)
        self.set_state(NodeState.UP, "achieved quorum, decision made")
        self.log_action(
            action="RECEIVE_LEARN",
            action_value=f"value={proposal.value}",
            target_node_id=str(proposal.node_id),
            target_node_role=self.peer_state[proposal.node_id]['role'].name, # "PROPOSER",
            target_node_state=self.peer_state[proposal.node_id]['state'].name, # NodeState.UP
            consensus_reached=True
        )
        
        self.logger.debug(f"[Node {self.node_id} | {self.role.name}] LEARNED value={proposal.value} slot={proposal.slot}")

        self.log_action(
            action="SEND_LEARN_OK",
            action_value=f"value={proposal.value}",
            target_node_id=str(proposal.node_id),
            target_node_role="PROPOSER",
            target_node_state=NodeState.UP,
            consensus_reached=True
        )

        if self.last_consensus != None:# self.strategy.is_consensus_reached():
            self.logger.info(f"Consensus reached, saving logs to CSV for Node {self.node_id}.")
            # input("SAVE")
            self.logger.save_to_csv()

        # self.storage.set_latest_proposal_id(proposal.proposal_id)
        self.paxos_in_progress = False
        self.synced = True
        self.logger.info(f"[Node {self.node_id}] Learned slot {proposal.slot} with value={proposal.value}, updated latest_proposal_id={proposal.proposal_id}")
        return PaxosMessage(
            type=PaxosMessage.LEARN_OK, 
            proposal_id=proposal.proposal_id, 
            multi=MultiPaxosPayload(
                value=proposal.value, 
                slot=proposal.slot, 
                ok=True
            ),
            sender_id=self.node_id
        )
    """
    def receive_learn(self, proposal: Proposal) -> dict:

        print(f"Node {self.node_id}, Received learn: {proposal}")
        self.role = NodeRole.LEARNER
        print(f"SET ACCEPTED slot: {proposal.slot}, id: {proposal.proposal_id}, value: {proposal.value}")
        self.storage.set_accepted(proposal.slot, proposal.proposal_id, proposal.value)
        self.set_consensus(proposal.value, proposal.slot, proposal.proposal_id)
        self.set_state(NodeState.UP, "achieved quorum, decision made")
        self.log_action(
            action="RECEIVE_LEARN",
            action_value=f"value={proposal.value}",
            target_node_id=str(proposal.node_id),
            target_node_role=self.peer_state[proposal.node_id]['role'].name, # "PROPOSER",
            target_node_state=self.peer_state[proposal.node_id]['state'].name, # NodeState.UP
            consensus_reached=True
        )
        
        self.logger.debug(f"[Node {self.node_id} | {self.role.name}] LEARNED value={proposal.value} slot={proposal.slot}")

        self.log_action(
            action="SEND_LEARN_OK",
            action_value=f"value={proposal.value}",
            target_node_id=str(proposal.node_id),
            target_node_role="PROPOSER",
            target_node_state=NodeState.UP,
            consensus_reached=True
        )

        if self.last_consensus != None:# self.strategy.is_consensus_reached():
            self.logger.info(f"Consensus reached, saving logs to CSV for Node {self.node_id}.")
            # input("SAVE")
            self.logger.save_to_csv()

        # self.storage.set_latest_proposal_id(proposal.proposal_id)
        self.paxos_in_progress = False
        self.synced = True
        self.logger.info(f"[Node {self.node_id}] Learned slot {proposal.slot} with value={proposal.value}, updated latest_proposal_id={proposal.proposal_id}")
        # _emit_metric(self.metrics_path, self._make_event("learn", slot=slot, value=value, accepted_id=accepted_id))
        # return {"type": MessageType.LEARN_SUCC.value, "slot": proposal.slot, "value": proposal.value, "sender_id": self.node_id, "proposal_id": proposal.proposal_id}# accepted_id}
        return PaxosMessage(
            type=PaxosMessage.LEARN_OK, 
            proposal_id=proposal.proposal_id, 
            multi=MultiPaxosPayload(
                value=proposal.value, 
                slot=proposal.slot, 
                ok=True
            ),
            sender_id=self.node_id
        )
        # if proposal['type'] == MessageType.LEARN_SUCC.value:
        #     return True
        # return False
    def decide_on_promises_received(self, proposal: Proposal, count_self=True):
        """
        Choose value for this proposal based on received promises.
        Implements the Paxos rule:
        - Adopt the previously accepted value with highest proposal_id if any.
        - Otherwise, keep our own proposal value.
        """
        promises = self.received_promises.get(proposal.proposal_id, [])

        print("---"*5, f"DECIDE_ON_PROMISES_RECEIVED NODE {self.node_id}", "---"*5)
        print(f"Received Promises: {promises}")
        # only keep unique promises by sender and only PROMISE messages
        seen = {}
        for p in promises:
            if getattr(p, "type", None) != PaxosMessage.PROMISE:
                continue
            seen[p.sender_id] = p
        unique_promises = list(seen.values())

        quorum_size = len(self.peers) // 2 if count_self else len(self.peers) // 2 + 1 # + 1 =>  count self

        self.logger.info(f"Node {self.node_id} got {len(unique_promises)} promises with an required quorum_size of {quorum_size}.")

        if len(unique_promises) < quorum_size:
            self.logger.warning(
                f"[Node {self.node_id}] Prepare phase failed: only {len(promises)} promises received, "
                f"need quorum {quorum_size} for slot {proposal.slot}"
            )
            self.set_state(NodeState.BLOCKED, "lost quorum during prepare")
            return False

        # --- Pick the value to propose ---
        highest_accepted = None  # tuple (accepted_id, accepted_value)
        for p in promises:
            accepted_id = p.multi.accepted_id if p.multi.accepted_id is not None else 0
            accepted_value = p.multi.value
            if accepted_id:
                if highest_accepted is None or accepted_id > highest_accepted[0]:
                    highest_accepted = (accepted_id, accepted_value)

        if highest_accepted:
            # There is a previously accepted value; adopt it
            chosen_id, chosen_value = highest_accepted
            self.logger.debug(
                f"[Node {self.node_id}] Adopting previously accepted value={chosen_value} "
                f"from highest accepted_id={chosen_id} for slot {proposal.slot}"
            )
            # proposal.proposal_id = chosen_id + 1 
            proposal.value = chosen_value
        else:
            self.logger.debug(
                f"[Node {self.node_id}] No previously accepted value; keeping own value={proposal.value} for slot {proposal.slot}"
            )

        # Record that we promised not to accept lower proposal_ids
        self.storage.set_promised(proposal.slot, proposal.proposal_id)
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
        Handles dict-based peer_status and enum NodeState safely.
        """
        try:
            to_node_id = target_node_id or self.node_id
            to_node_role = target_node_role or getattr(self, "role", "UNKNOWN")
            to_node_state = "UNKNOWN"
            if target_node_state is not None:
                to_node_state = target_node_state.name if hasattr(target_node_state, "name") else str(target_node_state)
            # --- Current node info ---
            from_role = getattr(self, "role", "UNKNOWN")
            raw_from_state = getattr(self, "state", NodeState.UP)
            from_state = raw_from_state.name if hasattr(raw_from_state, "name") else str(raw_from_state)
            # --- Consensus info ---
            consensus_value = consensus_value or ( self.storage.get_latest_decision() if hasattr(self, "storage") else None )
            consensus_reached = consensus_reached or ( self.strategy.is_consensus_reached() if hasattr(self, "strategy") else False)

            # --- Logging ---
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
            else:
                # Fallback for when logger isn't fully initialized
                print(
                    f"[LOG] {self.node_id}: {action} -> node {to_node_id} "
                    f"(state={to_node_state}, value={action_value}, consensus={consensus_reached})"
                )

        except Exception as e:
            self.logger.error(f"[log_action ERROR] {type(e).__name__}: {e}")

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

    def set_consensus(self, value, slot, accepted_id):
        print(f"Setting Consensus...")        
        self.last_consensus = value

        self.storage.set_decision(slot, value, accepted_id, self.clock.now())

        latest_proposal_id = self.storage.get_latest_proposal_id()
        if latest_proposal_id < accepted_id:
            self.storage.set_latest_proposal_id(accepted_id)
        # print(f"After setting decision, and latest proposal id: {accepted_id}")

        if isinstance(self.strategy, SingleDecreePaxos):
            self.strategy.chosen_value = value
            self.strategy.proposal_id = accepted_id

        print("CONSENSUS REACHED!")
        try:
            self.logger.save_to_csv(accepted_id)
            print("SAVED TO CSV")
        except Exception as e:
            print("ERROR SAVING TO CSV")
            print(e)



    def reset_consensus_reached(self):
        print(f"reset_consensus called, last_consensus=None!")
        self.last_consensus = None

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
    def initialize_proposal_counter(self):
        last = self.storage.get_latest_proposal_id()
        if last is None:
            # Nothing seen yet; start fresh
            self._proposal_counter = 0
            return

        # Extract the counter portion from the proposal_id
        last_counter = last >> 16

        # Ensure next generated proposal_id is strictly greater
        self._proposal_counter = last_counter + 1

    def next_proposal_id(self) -> int:
        """
        Produce a new proposal id with layout:
        (monotonic_counter << 16) | (node_id & 0xffff)
        Ensures we are strictly higher than any seen latest_proposal_id stored.
        """
        latest = self.storage.get_latest_proposal_id() or 0
        try:
            latest = int(latest)
        except Exception:
            latest = 0

        latest_counter = latest >> 16

        # bump our internal counter to be above any seen counter
        if latest_counter >= self._proposal_counter:
            self._proposal_counter = latest_counter

        self._proposal_counter += 1

        return (self._proposal_counter << 16) | (self.node_id & 0xffff)
#| (self.node_id & 0xffff)
    # -----------------
    # network server
    # -----------------
    async def start_server(self):
        # For simulated environment clusters
        if self.host is None:
            self.host = "127.0.0.1"
        if self.port is None:
            self.port = 0

        # 1. Paxos server
        self.server = await asyncio.start_server(
            self.handle_connection,
            self.host,
            self.port
        )
        self.ready_event.set()  # ✅ mark as ready

        # Attempting to run both Paxos and the Control-Server instance concurrently
        async with self.server:
            await self.server.serve_forever()

    async def handle_connection(self, reader: asyncio.StreamReader, writer: asyncio.StreamWriter):
        peer = writer.get_extra_info('peername')
        info_keys = ["peername", "sockname", "sslcontext", "peercert", "ssl_object", "socket"]

        network_logger.debug(f"[Node {self.node_id}] received connection from {peer}")
        for key in info_keys:
            val = writer.get_extra_info(key)
            network_logger.debug(f"{key}: {val}")

        try:
            hdr = await reader.readexactly(MSG_HDR.size)
            (n,) = MSG_HDR.unpack(hdr)
            body = await reader.readexactly(n)
            self.logger.debug(f"Node {self.node_id} got body: {body}")

            # ✅ decode protobuf message
            try:
                msg = PaxosMessage.FromString(body)
            except Exception as e:
                raise RuntimeError(f"Failed to decode PaxosMessage: {e}")

            if not msg:
                raise RuntimeError("Received empty or invalid PaxosMessage")

            # ✅ Logging
            level = logging.DEBUG if msg.type in (PaxosMessage.HEARTBEAT, PaxosMessage.HEARTBEAT_OK) else logging.INFO
            self.logger.log(level, f"[Node {msg.sender_id} -> Node {self.node_id}] RECV {peer} type({PaxosMessage.Type.Name(msg.type)})")

            # ✅ dispatch to correct handler
            reply = await self.dispatch(msg)
            if not reply:
                print(f"Message: {msg}")
                raise RuntimeError("Dispatch returned no reply")

            # ✅ Send reply (encode back into protobuf wire format)
            data = reply.SerializeToString()
            writer.write(MSG_HDR.pack(len(data)))
            writer.write(data)
            await writer.drain()

            # ✅ Logging outbound message
            level = logging.DEBUG if reply.type == PaxosMessage.HEARTBEAT_OK else logging.INFO
            self.logger.log(level, f"[Node {self.node_id} -> Node {msg.sender_id}] SEND {peer} type({PaxosMessage.Type.Name(reply.type)})")

        except Exception as e:
            # 🧨 Rich error reporting with traceback
            tb_str = ''.join(traceback.format_exception(type(e), e, e.__traceback__))
            err_msg = f"Exception in handle_connection (Node {self.node_id}): {type(e).__name__} – {e}\n{tb_str}"
            self.logger.error(err_msg)
            print(err_msg)

            # Send back error protobuf
            try:
                err_reply = PaxosMessage(
                    type=PaxosMessage.ERR,
                    sender_id=self.node_id,
                    error_msg=str(e),
                    timestamp=self.clock.now() if hasattr(self, 'clock') else 0
                )
                data = err_reply.SerializeToString()
                writer.write(MSG_HDR.pack(len(data)))
                writer.write(data)
                await writer.drain()
            except Exception:
                pass  # avoid double fault if connection already dead

        finally:
            with contextlib.suppress(Exception):
                writer.close()
                await writer.wait_closed()

    # -----------------
    # message handlers
    # -----------------
    async def dispatch(self, msg: PaxosMessage) -> Optional[PaxosMessage]:
        try:
            # mtype = MessageType(msg.type)
            mtype = msg.type
            self.logger.debug(f"Got mtype: {mtype}")
            # print(f"Got mtype: {mtype}")
        except ValueError:
            self.logger.error("Got Unknown PaxosMsgType! Check dispatch.")
            return await self.on_unknown(msg)
        
        handlers = {
            PaxosMessage.PREPARE: self.on_prepare,
            PaxosMessage.ACCEPTED: self.on_accept,
            PaxosMessage.LEARN: self.on_learn,
            PaxosMessage.HEARTBEAT: self.on_heartbeat,
            PaxosMessage.ELECTION: self.on_election,
            PaxosMessage.ELECTION_OK: self.on_election_ok,
            PaxosMessage.COORDINATOR: self.on_coordinator,
            PaxosMessage.SYNC_REQUEST: self.on_sync_request,
            PaxosMessage.FAST_PATH: self.on_fast_path,
            PaxosMessage.FAST_PATH_OK: self.on_fast_path_ok
        }
        handler = handlers.get(mtype, self.on_unknown)

        try:
            reply = await handler(msg)
            self.logger.debug(f"Got reply of handler: {reply}")
            return reply
        except Exception as e:

            tb = traceback.format_exc()
            err = f"Node {self.node_id} handler {mtype} crashed: {e}"
            self.logger.warning(f"[Node {self.node_id}] handler failed: {e}")
            self.logger.error(
                f"[dispatch] Exception in Node {self.node_id} while handling MessageTypes {mtype}"
                f"Error: {e}\n"
                f"Traceback:\n{tb}"
            )
            # self.logger.error(err)
            # return {"type": MessageType.ERR.value, "err": f"handler_exception_{mtype.value}", "sender_id": self.node_id}
            return PaxosMessage(type=PaxosMessage.ERR, error_msg=err, sender_id=self.node_id)

    async def on_unknown(self, msg: PaxosMessage):
        err = f"Node {self.node_id} unknown message type: {msg.type}"
        self.logger.error(err)
        # return {'err': 'unknown', "sender_id": self.node_id}
        return PaxosMessage(type=PaxosMessage.ERR, error_msg=err, sender_id=self.node_id)

# -----------------
# Acceptor: prepare
# -----------------
    async def on_prepare(self, msg: PaxosMessage) -> Optional[PaxosMessage]:
        """ACCEPTOR receives PREPARE."""
        slot = self._msg_slot(msg)
        proposal_id = msg.proposal_id

        promised = self.storage.get_promised(slot)
        print(f"self.storage.get_promised(slot): {promised}")
        accepted_id, _ = self.storage.accepted(slot)

        value = msg.multi.value

        # print(f"self.storage.accepted(slot): {accepted_id}, accepted_value: {accepted_value}")
        # accepted_id, accepted_value = self.storage.get_accepted(slot)
        # accepted_value = self.storage.get_accepted(slot)

        print(f"self.storage.get_accepted(slot): promised: {promised}, accepted_value: {_}, msg.value: {value}")
        
        print("-------------"*2, "on_prepare" ,"-------------"*2)
        # print(f"on_prepare promised: {promised}")
        # print(f"on_prepare accepted_value", accepted_value)
        # print(f"Node {self.node_id} on_prepare from Node {msg.sender_id}")
        print(f"Msg:{msg}")
        self.log_action(
            action="RECEIVE_PREPARE",
            action_value=f"proposal_id={msg.proposal_id}, promised=True",
            target_node_id=str(self.node_id), # msg.sender_id,
            target_node_role=self.role.name, # self.peer_state[msg.sender_id]['role'].name if msg.sender_id in self.peer_state else self.role.name, # "PROPOSER",
            target_node_state=self.state.name, # self.peer_state[msg.sender_id]['state'].name if msg.sender_id in self.peer_state else self.state, # NodeState.UP
            consensus_reached=False
        )

        # print(f"Deciding if ERR or PROMISE...promised: {promised}, proposal_id: {proposal_id}")
        print(f"--------- CASE 1: proposal_id < promised → REJECT ---------- ({promised is not None and proposal_id < promised}) ")

        if promised is not None and proposal_id < promised:
            print(f"Promised: {promised}, proposal_id: {proposal_id}, promised: {promised}")
            print(f"Sending back error, inquire to check proposal_id and increase it to fit current dataset: a_id:{accepted_id}, ")
            self.log_action(
                action="ERROR",
                action_value=f"proposal_id={msg.proposal_id}, promised=False",
                target_node_id=msg.sender_id,
                target_node_role=self.peer_state[msg.sender_id]['role'] if msg.sender_id in self.peer_state else NodeRole.ACCEPTOR.name, # "PROPOSER",
                target_node_state=self.peer_state[msg.sender_id]['state'].name if msg.sender_id in self.peer_state else NodeState.UNKNOWN # NodeState.UP
            )

            return PaxosMessage(
                type=PaxosMessage.ERR, # REJECT,
                sender_id=self.node_id,
                proposal_id=proposal_id,
                multi=MultiPaxosPayload(
                    accepted_id=accepted_id if accepted_id is not None else None,
                    slot=slot,
                    value=value,
                    ok=True
                ),
                leader_id=self.leader_id or -1,
                timestamp=self.clock.now(),
            )
        else:
            print("Not sending back error but a Promise...")
        
        if promised is None or msg.proposal_id >= promised: # msg.multi.slot not in all_accepted and (promised is None or msg.proposal_id > promised): # accepted_id == -1 and accepted_value == None:# promised is None or msg.proposal_id > promised:
            print(f"Promised (id) on that slot is None so we can use the msg.id: {msg.proposal_id}, value: {value}")
            # self.storage.set_accepted(slot, msg.proposal_id, accepted_value)

            returnmsg = PaxosMessage(
                type=PaxosMessage.PROMISE,
                sender_id=self.node_id,
                proposal_id=msg.proposal_id, # decision[2] if decision else msg.proposal_id, # msg.proposal_id,
                multi=MultiPaxosPayload(
                    accepted_id=accepted_id, # None,# accepted_id if accepted_id is not None else None, # decision[1] if decision else msg.multi.slot,
                    slot=slot,
                    value=value, # None,# accepted_value if accepted_value is not None else None, # decision[0] if decision else msg.multi.value,
                    ok=False
                ),
                leader_id=self.leader_id or -1,
                timestamp=self.clock.now(),
            )

            print(f"Set Promised slot, id: {slot}, {msg.proposal_id}")
            self.storage.set_promised(slot, msg.proposal_id)

            print(f"returnmsg-accepted_id: {accepted_id}, returnmsg-slot: {slot}, returnmsg-value: {value}")
            print(f"Sending back Promise: {returnmsg}")
            # 1.Send back promise to not adopt proposal_id < msg.proposal_id and
            # 2. Last Consensus Value achieved before current msg.proposal_id
            # This way the Proposer can determine if it or peers are missing entries which need to be proposed first.

            self.log_action(
                action="SEND_PROMISE",
                action_value=f"proposal_id={msg.proposal_id}, promised=True",
                target_node_id=msg.sender_id,
                target_node_role=self.peer_state[msg.sender_id]['role'].name, # "PROPOSER",
                target_node_state=self.peer_state[msg.sender_id]['state'].name # NodeState.UP
            )
            return returnmsg       
        
        print("Nothing caught, this shouldnt happen.")

# -----------------
# Acceptor: accept request
# -----------------
    async def on_accept(self, msg: PaxosMessage) -> PaxosMessage:
        """
        Receive Accept -> 
        """
        proposal = Proposal(msg.sender_id, msg.proposal_id, msg.multi.value, self._msg_slot(msg))
        print("---"*5, "ON_ACCEPT (SEND_ACCEPT)", "---"*5)
        print(f"Node {self.node_id} on_accept from Node {msg.sender_id} with value: {msg.multi.value}")
        self.log_action(
            action="RECEIVE_ACCEPT",
            action_value=f"proposal_id={proposal.proposal_id}, accepted=True",
            target_node_id=str(self.node_id), # str(proposal.node_id),
            target_node_role=self.role.name,# "PROPOSER",
            target_node_state=self.state.name,#NodeState.UP
        )
        print(f"PaxosMessage: {msg}")
        promised = self.storage.get_promised(proposal.slot)
        print(f"PROMISED: {promised}")

        if promised is None or proposal.proposal_id >= promised:

            self.logger.info(f"[Node {self.node_id} | {self.role.name}] ACCEPTED pid={proposal.proposal_id} value={proposal.value} slot={proposal.slot}")
            print(f"[Node {self.node_id} | {self.role.name}] ACCEPTED pid={proposal.proposal_id} value={proposal.value} slot={proposal.slot}")
            # self.storage.set_promised(proposal.slot, proposal.proposal_id)
            self.storage.set_accepted(proposal.slot, proposal.proposal_id, proposal.value)

            got_accepted = self.storage.get_accepted(proposal.slot)
            print(f"Got Accepted: {got_accepted}")

            self.logger.info(f"[Node {self.node_id} | {self.role.name}] ACCEPTED pid={proposal.proposal_id} value={proposal.value} slot={proposal.slot}")
            self.log_action(
                action="SEND_ACCEPTED",
                action_value=f"proposal_id={proposal.proposal_id}, accepted=True",
                target_node_id=str(proposal.node_id),
                target_node_role=self.peer_state[proposal.node_id]['role'] if proposal.node_id in self.peer_state else NodeRole.ACCEPTOR.name, # "PROPOSER",
                target_node_state=self.peer_state[proposal.node_id]['state'].name if proposal.node_id in self.peer_state else NodeState.UNKNOWN, # NodeState.UP
            )
            return PaxosMessage(type=PaxosMessage.ACCEPTED, proposal_id=proposal.proposal_id, slot=proposal.slot, sender_id=self.node_id)
        else:
            print(f"Returning Rejection. Reason: promised: {promised}, proposal_id: {proposal.proposal_id}")
            self.logger.debug(f"[Node {self.node_id} | {self.role.name}] REJECT accept pid={proposal.proposal_id} promised={promised} slot={proposal.slot}")
            return PaxosMessage(type=PaxosMessage.REJECT, proposal_id=proposal.proposal_id, slot=proposal.slot, sender_id=self.node_id)
        # sender_id = msg["sender_id"]
        return self.receive_accept()# , sender_id)

# -----------------
# Learner: learn broadcast
# -----------------
    async def on_learn(self, msg: PaxosMessage) -> PaxosMessage:
        print("ON_LEARN")
        accepted_id = msg.proposal_id # ["accepted_id"]
        # sender_id = msg["sender_id"]
        return self.receive_learn(Proposal(msg.sender_id, accepted_id, msg.multi.value, msg.multi.slot))#, sender_id)

# -----------------
# Client propose
# -----------------
    async def on_client_propose(self, msg: PaxosMessage, peer) -> PaxosMessage:
        # value = msg.get('value')
        start = time.perf_counter()
        # Single-decree short-circuit
        if isinstance(self.strategy, SingleDecreePaxos):
            if self.strategy.chosen_value is not None:
                # Already decided: return immediately
                end = time.perf_counter()
                """
                self.log_event(
                    logging.INFO,
                    PaxosMessage.SINGLE_DECISION,
                    value=msg.value,
                    latency=(end - start),
                    peer=f"[Node {msg.sender_id}] -> {peer}"
                )
                """
                return PaxosMessage(type=PaxosMessage.SINGLE_DECISION, single=SinglePaxosPayload(value=msg.value))
            else:
                self.logger.info(f"[Node {self.node_id}] SingleDecreePaxos (value not chosen yet?)")

            # No leader needed for single-decree: propose directly
            ok = await self.strategy.propose(msg.value)
            end = time.perf_counter()
            return PaxosMessage(type=PaxosMessage.SINGLE_DECREE_RESULT, value=self.strategy.chosen_value, sender_id=self.node_id)
        # Multi-Paxos path requires leader
        if self.leader_id is None:
            asyncio.create_task(self.start_election())
            # return {'type': 'err', 'err': 'no_leader', "sender_id": self.node_id}
            return PaxosMessage(type=PaxosMessage.ERR, error_msg="no leader", sender_id=self.node_id)
        if self.leader_id != self.node_id:
            peer = self.peers.get(self.leader_id)
            if not peer:
                # return {'type': 'err', 'err': 'leader_unknown', "sender_id": self.node_id}
                return PaxosMessage(type=PaxosMessage.ERR, error_msg="leader unknown", sender_id=self.node_id)

            host, port = peer
            prepare_res = PaxosMessage(type=PaxosMessage.PREPARE, value=msg.value, sender_id=self.node_id)
            return await send_message(host, port, prepare_res, 2, self)

        # Multi-Paxos leader path
        if isinstance(self.strategy, MultiPaxos):
            slot = self.storage.next_slot()
            ok = await self.strategy.propose(msg.value, slot=slot)
            return {'type': 'propose_result', 'ok': ok, 'slot': slot, 'sender_id': self.node_id}
    def get_highest_up_node(self):
        up_nodes = [self.node_id] + [
            nid for nid, p in self.peer_state.items()
            if p['state'] == NodeState.UP
        ]
        return max(up_nodes)
# -----------------
# Leader Election (Bully)
# -----------------
    async def start_election(self):
        if len(self.peers) < 2:
            self.leader_id = -1
            print("Not enough peers configured to have a leader.")
            return

        if not isinstance(self.strategy, MultiPaxos):
            return

        if self._election_in_progress:
            return
        self._election_in_progress = True
        self.election_role: ElectionRole = ElectionRole.CANDIDATE

        quorum = (len(self.peers) + 1) // 2 + 1   # +1 includes self
        # Wait until a quorum of nodes is UP (including self)
        while True:
            up_nodes = 1  # self is always UP
            for pid, state in self.peer_state.items():
                if state["state"] == NodeState.UP:
                    up_nodes += 1

            if up_nodes >= quorum:
                break

            self.logger.debug(
                f"[Node {self.node_id}] waiting for quorum: {up_nodes}/{quorum} nodes UP"
            )
            await asyncio.sleep(0.1)
        # --- Determine higher nodes that are UP ---
        higher_nodes = {nid: addr for nid, addr in self.peers.items() if nid > self.node_id}
        higher_up_nodes = {nid: addr for nid, addr in higher_nodes.items()
                        if self.peer_state.get(nid, {}).get('state') == NodeState.UP}

        if not higher_up_nodes:
            # No higher node is UP → I am the new leader
            await self.announce_coordinator()
            self._election_in_progress = False
            return
        
        self.election_role: ElectionRole = ElectionRole.FOLLOWER

        self.logger.info(f"[Node {self.node_id}] starting election, sending ELECTION to {list(higher_up_nodes.keys())}")
        election_msg = PaxosMessage(type=PaxosMessage.ELECTION, sender_id=self.node_id)

        # Send election messages to higher nodes
        tasks = [send_message(host, port, election_msg, timeout=2, node=self)
                for nid, (host, port) in higher_up_nodes.items()]
        results = await asyncio.gather(*tasks, return_exceptions=True)

        someone_ok = any(isinstance(r, PaxosMessage) and r.type == PaxosMessage.ELECTION_OK
                        for r in results)

        if not someone_ok:
            # All higher nodes failed to respond → I become leader
            await self.announce_coordinator()
        else:
            # Wait for higher node to announce itself
            await asyncio.sleep(self.heartbeat_timeout)
            if self.leader_id is None:
                # Higher node didn’t announce → retry election after small backoff
                await asyncio.sleep(random_small())
                self._election_in_progress = False
                await self.start_election()
                return

        self._election_in_progress = False

    async def announce_coordinator(self):
        # self.role = NodeRole.LEADER
        self.election_role = ElectionRole.LEADER
        self.leader_id = self.node_id
        self.leader_ballot =  self.next_proposal_id()
        self.leader_last_heartbeat = self.clock.now() # time.time()
        self.logger.info(f"[Node {self.node_id} | {self.role.name}] became coordinator")
        # announcement_msg = {"type": MessageType.COORDINATOR.value, "leader_id": self.node_id, 'sender_id': self.node_id}
        announcement_msg = PaxosMessage(type=PaxosMessage.COORDINATOR, leader_id=self.node_id, sender_id=self.node_id)
        for _, (host, port) in self.peers.items():
            asyncio.create_task(send_message(host, port, announcement_msg, 2, self))
# -----------------
# election/heartbeat handlers added (missing in original)
# -----------------
    async def on_election(self, msg: PaxosMessage) -> PaxosMessage:
        sender = msg.sender_id
        self.logger.info(f"[Node {self.node_id}] received ELECTION from {sender}")

        if self.node_id > sender:
            # I am higher → I must answer OK
            asyncio.create_task(self.start_election())  # Bully: higher node takes over
            return PaxosMessage(type=PaxosMessage.ELECTION_OK, sender_id=self.node_id)
        
        # Lower node → do NOT respond
        self.logger.debug(f"[Node {self.node_id}] lower than sender {sender}, not responding")
        return None


    async def on_election_ok(self, msg: PaxosMessage):
        self.logger.debug(f"[Node {self.node_id}] received ELECTION_OK from {msg.sender_id}")
        # No response must be sent.
        # start_election() will detect this via results from send_message
        return None

    async def on_coordinator(self, msg: PaxosMessage) -> PaxosMessage:
        leader = msg.leader_id # msg.get('leader_id')
        self.logger.info(f"[Node {self.node_id}] acknowledges coordinator {leader}")
        self.leader_id = leader
        self.role = NodeRole.ACCEPTOR
        self.leader_last_heartbeat = self.clock.now()
        return PaxosMessage(type=PaxosMessage.COORDINATOR_OK, sender_id=self.node_id) # {'type': 'ok', "sender_id": self.node_id}

    # -----------------
    # lifecycle
    # -----------------
    async def start(self):
        print(f"Node {self.node_id} Start server")
        self._stopping = False
        if getattr(self, "simulated", False):
            # skip TCP server entirely
            self._server_task = None
        else:
            self._server_task = asyncio.create_task(self.start_server())

        self.set_state(NodeState.UP, "Server was started.")
        # could be here to help identify and manage-availability for consensus-backoff mechanism
        # Delay heartbeat startup until server is ready
        async def delayed_heartbeat_start():
            await self.ready_event.wait()
            await asyncio.sleep(0.3)  # small buffer
            self.tasks.append(asyncio.create_task(self.heartbeat_loop()))

        print(f"Node {self.node_id} Launch the delayed heartbeat")

        asyncio.create_task(delayed_heartbeat_start())
        # self.tasks.append(asyncio.create_task(self.heartbeat_loop()))

        # Only start heartbeat and election for Multi-Paxos
        if isinstance(self.strategy, MultiPaxos):
            # self.tasks.append(asyncio.create_task(self.heartbeat_loop()))
            # small startup election attempt
            await asyncio.sleep(0.2 + random_small())
            print(f"Node {self.node_id} Start Election.")
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
# helper
# -----------------
async def propose_to(local_node: dict, value: str, slot: int, use_worker=False):
    if use_worker:
        return await local_node["node"].proposal_queue.put((value, slot))
    return await local_node["node"].coordinate_forever(value, slot)

def random_small():
    import random
    return random.random() * 0.2

