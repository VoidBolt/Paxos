import time
from proto.paxos_pb2 import PaxosMessage, SinglePaxosPayload, MultiPaxosPayload
from clock import VirtualClock
from paxos_node import NodeState

virtual_clock = VirtualClock()

# -------------------------------
# 1️⃣ Single Paxos (already decided)
# -------------------------------
single_chosen = PaxosMessage(
    type=PaxosMessage.SINGLE_DECISION,
    sender_id=1,
    proposal_id=123,
    leader_id=1,
    timestamp=virtual_clock.now(),
    single=SinglePaxosPayload(value="banana", ok=True)
)

print("Original SINGLE_DECISION message:")
print(single_chosen)

# Serialize / Deserialize
data = single_chosen.SerializeToString()
parsed = PaxosMessage()
parsed.ParseFromString(data)
print("\nAfter parsing:")
print("Type:", parsed.type)
print("Single payload:", parsed.single.value, parsed.single.ok)

# -------------------------------
# 2️⃣ Multi Paxos (leader proposing)
# -------------------------------
multi_propose = PaxosMessage(
    type=PaxosMessage.PREPARE,
    sender_id=2,
    proposal_id=9999,
    leader_id=2,
    timestamp=virtual_clock.now(),
    multi=MultiPaxosPayload(value="distributed_value", ok=True, slot=3)
)

print("\nOriginal Multi-Paxos PREPARE:")
print(multi_propose)

data2 = multi_propose.SerializeToString()
parsed2 = PaxosMessage()
parsed2.ParseFromString(data2)

print("\nAfter parsing Multi-Paxos:")
print("Type:", parsed2.type)
print("Slot:", parsed2.multi.slot)
print("Multi payload:", parsed2.multi.value, parsed2.multi.ok)

# -------------------------------
# 3️⃣ Error response (no leader)
# -------------------------------
err_msg = PaxosMessage(
    type=PaxosMessage.ERR,
    sender_id=5,
    error_msg="no leader available",
    timestamp=virtual_clock.now()
)

data3 = err_msg.SerializeToString()
parsed3 = PaxosMessage()
parsed3.ParseFromString(data3)
print("\nParsed error message:")
print(parsed3)


msg = PaxosMessage(
    type=PaxosMessage.HEARTBEAT,
    sender_id=1,
    proposal_id=123,
    known_slots=[1],
    state="UP",
    role="ACCEPTOR",
    leader_id=-1,
    timestamp=0,
)                
state = NodeState["UP"]
print(state)
