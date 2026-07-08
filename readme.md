Paxos implementation as an installable package, initial testing was done via port seperation.
Additional linux namespacing integration requires running of:
  -setup_network.py
which will create 44 different network hosts on a comparable intranet as in the university environment.


Local Environment:
since execution of commands in netns requires root, we need to enable become=yes in the ansible playbook config and then add the argument -ask-become-pass so we can execute individual namespaces commands

Remote Environment:
default behavior of ansible is to use ssh to gain shell access of a host and to be able to control the flow of actions.
  - therefore we need a functioning ssh setup in the university network

Tests:
pytest is being used to test functionality

Sample command for ssh in Lab to one of the other machines:
  - ssh -i /tmp/id_ed25519 s80697@pool-8P49D14.ris.bht-berlin.de


+----+

  Labor-Environment:
    - 1. make install
    - 2. ansible-playbook -i inventories/inventory_lab_min_self.yml playbooks/03_wol.yaml
     (this inventory excludes self, so we can execute a seperate instance that isnt just "LISTENING")
    - 3. 
        3.1 this -> python3 src/paxos/paxos_async.py --inventory inventories/inventory_lab_min.yml --repl (interactive mode with "/help")
        3.2 or -> python3 src/paxos/paxos_async.py --inventory inventories/inventory_lab_min.yml --proposal 'valueToBeStoredinSlot5' 5 'AnotherValueToSlot12' 12

+----+

Linux namespaces execution commands:
 - 1. make install && python3 setup_network.py
 - 2. ansible-playbook -i inventories/inventory_netns.yml playbooks/run_netns.yml --ask-become-pass
  (this inventory excludes self, so we can execute a seperate instance that isnt just "LISTENING")
    - 3. 
        3.1 this -> python3 src/paxos/paxos_async.py --inventory inventories/inventory_lab_min.yml --repl (interactive mode with "/help")
        3.2 or -> python3 src/paxos/paxos_async.py --inventory inventories/inventory_lab_min.yml --proposal 'valueToBeStoredinSlot5' 5 'AnotherValueToSlot12' 12

## Environment Requirements

This project requires a Linux environment with support for network namespaces.

The execution environment must provide the `ip` command (from the `iproute2` package), as the project uses:

```bash
sudo ip netns exec
```

to create and execute processes inside Linux network namespaces.

Before running the project, ensure that `ip` is installed and available:

```bash
ip -V
```

On Debian/Ubuntu systems, install it with:

```bash
sudo apt install iproute2
```

The project also requires `sudo` privileges for namespace management.

+----+


Example Output 3 Instances (after setup_network.py and using netns configs):


--------------------------------------------------------
Node 1 Namespace
--------------------------------------------------------
```console
❯ sudo ip netns exec node1 python src/paxos/paxos_async.py --inventory inventories/inventory_netns_min.yml --netns 1 --repl
[sudo] password for *****:
local_identities: ['10.10.0.1']
NetworkLogger init with base_url: http://10.10.0.100:5000/api/logger
PaxosLogger init with base_url: http://10.10.0.100:5000/api/logger
Starting PaxosNode on 10.10.0.1:5001
NodeLock created at: paxos_manager_workspace/paxos_node_1.db.lock
NodeLock acquired!
Init needed? -> True
=== SQLITE DEBUG ===
Requested path: paxos_manager_workspace/paxos_node_1.db
Absolute path: /home/*****/Documents/paxos/Paxos/paxos_manager_workspace/paxos_node_1.db
Exists before connect: False
====================
Init is needed! Creating Tables...
Executing init_meta.sql...
Executed init_meta.sql! Meta table initialized.
Executing init_global_state.sql...
Executed init_global_state.sql! Global-state table initialized.
Executing seed_global_state.sql...
Executed seed_global_state.sql! Global-state seed initialized.
Executing init_slots.sql...
Executed init_slots.sql! Slots table initialized.
Executing init_decisions.sql...
Executed init_decisions.sql! Decisions table initialized.
Peer: 2
Peer: 3
Node 1 Start server
Node 1 Launch the delayed heartbeat
Node 1 Start Election.
Node 1 started at 10.10.0.1:5001, peers: {2: ('10.10.0.2', 5002), 3: ('10.10.0.3', 5003)}
REPL!
Commands: propose <value> <slot> | state | exit
> Node 1 Heart-start!
Heartbeat loop started Node 1. self._stopping? False
self.peers? {2: ('10.10.0.2', 5002), 3: ('10.10.0.3', 5003)}
Peer 3 marked UP (heartbeat OK)
stPeer 2 marked DOWN (no heartbeat reply)
ate
Node 1: running=True leader=3
peers: {2: ('10.10.0.2', 5002), 3: ('10.10.0.3', 5003)}
peer_state: {2: {'last_heartbeat': -1, 'state': <NodeState.DOWN: 2>, 'role': <NodeRole.ACCEPTOR: 1>}, 3: {'last_heartbeat': 4, 'state': <NodeState.UP: 1>, 'role': <NodeRole.ACCEPTOR: 1>}}
  No slots have reached consensus yet.
> --------------- ON_ACCEPT (SEND_ACCEPT) ---------------
Node 1 on_accept from Node 3 with value: A
PaxosMessage: type: ACCEPTED
sender_id: 3
proposal_id: 131075
multi {
  slot: 98
  value: "A"
}

PROMISED: None
[Node 1 | ACCEPTOR] ACCEPTED pid=131075 value=A slot=98
Got Accepted: (131075, 'A')
ON_LEARN
Node 1, Received learn: Proposal(node_id=3, proposal_id=131075, value='A', slot=98)
SET ACCEPTED slot: 98, id: 131075, value: A
Setting Consensus...
CONSENSUS REACHED!
Saving CSV to logs/paxosresult_1_131075.csv
SAVED TO CSV
Saving CSV to logs/paxosresult_1_unknown.csv
--------------- ON_ACCEPT (SEND_ACCEPT) ---------------
Node 1 on_accept from Node 3 with value: B
PaxosMessage: type: ACCEPTED
sender_id: 3
proposal_id: 196611
multi {
  slot: 78
  value: "B"
}

PROMISED: None
[Node 1 | LEARNER] ACCEPTED pid=196611 value=B slot=78
Got Accepted: (196611, 'B')
ON_LEARN
Node 1, Received learn: Proposal(node_id=3, proposal_id=196611, value='B', slot=78)
SET ACCEPTED slot: 78, id: 196611, value: B
Setting Consensus...
CONSENSUS REACHED!
Saving CSV to logs/paxosresult_1_196611.csv
SAVED TO CSV
Saving CSV to logs/paxosresult_1_unknown.csv
--------------- ON_ACCEPT (SEND_ACCEPT) ---------------
Node 1 on_accept from Node 3 with value: C
PaxosMessage: type: ACCEPTED
sender_id: 3
proposal_id: 196611
multi {
  slot: 75
  value: "C"
}

PROMISED: None
[Node 1 | LEARNER] ACCEPTED pid=196611 value=C slot=75
Got Accepted: (196611, 'C')
ON_LEARN
Node 1, Received learn: Proposal(node_id=3, proposal_id=196611, value='C', slot=75)
SET ACCEPTED slot: 75, id: 196611, value: C
Setting Consensus...
CONSENSUS REACHED!
Saving CSV to logs/paxosresult_1_196611.csv
SAVED TO CSV
Saving CSV to logs/paxosresult_1_unknown.csv
Peer 2 marked DOWN (no heartbeat reply)
--------------- ON_ACCEPT (SEND_ACCEPT) ---------------
Node 1 on_accept from Node 3 with value: A
PaxosMessage: type: ACCEPTED
sender_id: 3
proposal_id: 196611
multi {
  slot: 98
  value: "A"
}

PROMISED: 131075
[Node 1 | LEARNER] ACCEPTED pid=196611 value=A slot=98
Got Accepted: (196611, 'A')
ON_LEARN
Node 1, Received learn: Proposal(node_id=3, proposal_id=196611, value='A', slot=98)
SET ACCEPTED slot: 98, id: 196611, value: A
Setting Consensus...
CONSENSUS REACHED!
Saving CSV to logs/paxosresult_1_196611.csv
SAVED TO CSV
Saving CSV to logs/paxosresult_1_unknown.csv
--------------- ON_ACCEPT (SEND_ACCEPT) ---------------
Node 1 on_accept from Node 3 with value: B
PaxosMessage: type: ACCEPTED
sender_id: 3
proposal_id: 262147
multi {
  slot: 78
  value: "B"
}

PROMISED: 196611
[Node 1 | LEARNER] ACCEPTED pid=262147 value=B slot=78
Got Accepted: (262147, 'B')
ON_LEARN
Node 1, Received learn: Proposal(node_id=3, proposal_id=262147, value='B', slot=78)
SET ACCEPTED slot: 78, id: 262147, value: B
Setting Consensus...
CONSENSUS REACHED!
Saving CSV to logs/paxosresult_1_262147.csv
SAVED TO CSV
Saving CSV to logs/paxosresult_1_unknown.csv
--------------- ON_ACCEPT (SEND_ACCEPT) ---------------
Node 1 on_accept from Node 3 with value: C
PaxosMessage: type: ACCEPTED
sender_id: 3
proposal_id: 262147
multi {
  slot: 75
  value: "C"
}

PROMISED: 196611
[Node 1 | LEARNER] ACCEPTED pid=262147 value=C slot=75
Got Accepted: (262147, 'C')
ON_LEARN
Node 1, Received learn: Proposal(node_id=3, proposal_id=262147, value='C', slot=75)
SET ACCEPTED slot: 75, id: 262147, value: C
Setting Consensus...
CONSENSUS REACHED!
Saving CSV to logs/paxosresult_1_262147.csv
SAVED TO CSV

``` 

--------------------------------------------------------
Node 2 Namespace
--------------------------------------------------------

```console
❯ sudo ip netns exec node2 python src/paxos/paxos_async.py --inventory inventories/inventory_netns_min.yml --netns 2 --proposal A 98 --proposal B 78 --proposal C 75
local_identities: ['10.10.0.2']
NetworkLogger init with base_url: http://10.10.0.100:5000/api/logger
PaxosLogger init with base_url: http://10.10.0.100:5000/api/logger
Starting PaxosNode on 10.10.0.2:5002
NodeLock created at: paxos_manager_workspace/paxos_node_2.db.lock
NodeLock acquired!
Init needed? -> True
=== SQLITE DEBUG ===
Requested path: paxos_manager_workspace/paxos_node_2.db
Absolute path: /home/*****/Documents/paxos/Paxos/paxos_manager_workspace/paxos_node_2.db
Exists before connect: True
====================
Init is needed! Creating Tables...
Executing init_meta.sql...
Executed init_meta.sql! Meta table initialized.
Executing init_global_state.sql...
Executed init_global_state.sql! Global-state table initialized.
Executing seed_global_state.sql...
Executed seed_global_state.sql! Global-state seed initialized.
Executing init_slots.sql...
Executed init_slots.sql! Slots table initialized.
Executing init_decisions.sql...
Executed init_decisions.sql! Decisions table initialized.
Peer: 1
Peer: 3
Node 2 Start server
Node 2 Launch the delayed heartbeat
Node 2 Heart-start!
Heartbeat loop started Node 2. self._stopping? False
self.peers? {1: ('10.10.0.1', 5001), 3: ('10.10.0.3', 5003)}
Node 2 Start Election.
Node 2 started at 10.10.0.2:5002, peers: {1: ('10.10.0.1', 5001), 3: ('10.10.0.3', 5003)}
NO REPL!
Creating Test-Cases to Validate functionality:
Running Coordinate with: [value, slot, skip_prepare] = [A, 98, False]
Peer 1 marked UP (heartbeat OK)
--------------- ON_ACCEPT (SEND_ACCEPT) ---------------
Node 2 on_accept from Node 3 with value: A
PaxosMessage: type: ACCEPTED
sender_id: 3
proposal_id: 196611
multi {
  slot: 98
  value: "A"
}

PROMISED: 131075
[Node 2 | ACCEPTOR] ACCEPTED pid=196611 value=A slot=98
Got Accepted: (196611, 'A')
ON_LEARN
Node 2, Received learn: Proposal(node_id=3, proposal_id=196611, value='A', slot=98)
SET ACCEPTED slot: 98, id: 196611, value: A
Setting Consensus...
CONSENSUS REACHED!
Saving CSV to logs/paxosresult_2_196611.csv
SAVED TO CSV
Saving CSV to logs/paxosresult_2_unknown.csv
Running Coordinate with: [value, slot, skip_prepare] = [B, 78, False]
--------------- ON_ACCEPT (SEND_ACCEPT) ---------------
Node 2 on_accept from Node 3 with value: B
PaxosMessage: type: ACCEPTED
sender_id: 3
proposal_id: 262147
multi {
  slot: 78
  value: "B"
}

PROMISED: 196611
[Node 2 | LEARNER] ACCEPTED pid=262147 value=B slot=78
Got Accepted: (262147, 'B')
ON_LEARN
Node 2, Received learn: Proposal(node_id=3, proposal_id=262147, value='B', slot=78)
SET ACCEPTED slot: 78, id: 262147, value: B
Setting Consensus...
CONSENSUS REACHED!
Saving CSV to logs/paxosresult_2_262147.csv
SAVED TO CSV
Saving CSV to logs/paxosresult_2_unknown.csv
Running Coordinate with: [value, slot, skip_prepare] = [C, 75, False]
--------------- ON_ACCEPT (SEND_ACCEPT) ---------------
Node 2 on_accept from Node 3 with value: C
PaxosMessage: type: ACCEPTED
sender_id: 3
proposal_id: 262147
multi {
  slot: 75
  value: "C"
}

PROMISED: 196611
[Node 2 | LEARNER] ACCEPTED pid=262147 value=C slot=75
Got Accepted: (262147, 'C')
ON_LEARN
Node 2, Received learn: Proposal(node_id=3, proposal_id=262147, value='C', slot=75)
SET ACCEPTED slot: 75, id: 262147, value: C
Setting Consensus...
CONSENSUS REACHED!
Saving CSV to logs/paxosresult_2_262147.csv
SAVED TO CSV
Saving CSV to logs/paxosresult_2_unknown.csv
  Slots with consensus:
    slot 75: accepted_id=262147, accepted_value=C
    slot 78: accepted_id=262147, accepted_value=B
    slot 98: accepted_id=196611, accepted_value=A
Peer 1 marked DOWN (no heartbeat reply)

``` 

--------------------------------------------------------
Node 3 Namespace
--------------------------------------------------------

```console
❯ sudo ip netns exec node3 python src/paxos/paxos_async.py --inventory inventories/inventory_netns_min.yml --netns 3 --repl
[sudo] password for *****:
local_identities: ['10.10.0.3']
NetworkLogger init with base_url: http://10.10.0.100:5000/api/logger
PaxosLogger init with base_url: http://10.10.0.100:5000/api/logger
Starting PaxosNode on 10.10.0.3:5003
NodeLock created at: paxos_manager_workspace/paxos_node_3.db.lock
NodeLock acquired!
Init needed? -> True
=== SQLITE DEBUG ===
Requested path: paxos_manager_workspace/paxos_node_3.db
Absolute path: /home/*****/Documents/paxos/Paxos/paxos_manager_workspace/paxos_node_3.db
Exists before connect: False
====================
Init is needed! Creating Tables...
Executing init_meta.sql...
Executed init_meta.sql! Meta table initialized.
Executing init_global_state.sql...
Executed init_global_state.sql! Global-state table initialized.
Executing seed_global_state.sql...
Executed seed_global_state.sql! Global-state seed initialized.
Executing init_slots.sql...
Executed init_slots.sql! Slots table initialized.
Executing init_decisions.sql...
Executed init_decisions.sql! Decisions table initialized.
Peer: 1
Peer: 2
Node 3 Start server
Node 3 Launch the delayed heartbeat
Node 3 Start Election.
Node 3 started at 10.10.0.3:5003, peers: {1: ('10.10.0.1', 5001), 2: ('10.10.0.2', 5002)}
REPL!
Commands: propose <value> <slot> | state | exit
> Node 3 Heart-start!
Heartbeat loop started Node 3. self._stopping? False
self.peers? {1: ('10.10.0.1', 5001), 2: ('10.10.0.2', 5002)}
Peer 1 marked DOWN (no heartbeat reply)
Peer 2 marked DOWN (no heartbeat reply)
state
Node 3: running=True leader=None
peers: {1: ('10.10.0.1', 5001), 2: ('10.10.0.2', 5002)}
peer_state: {1: {'last_heartbeat': -1, 'state': <NodeState.DOWN: 2>, 'role': <NodeRole.ACCEPTOR: 1>}, 2: {'last_heartbeat': -1, 'state': <NodeState.DOWN: 2>, 'role': <NodeRole.ACCEPTOR: 1>}}
  No slots have reached consensus yet.
> state
Node 3: running=True leader=3
peers: {1: ('10.10.0.1', 5001), 2: ('10.10.0.2', 5002)}
peer_state: {1: {'last_heartbeat': 21, 'state': <NodeState.UP: 1>, 'role': <NodeRole.ACCEPTOR: 1>}, 2: {'last_heartbeat': -1, 'state': <NodeState.DOWN: 2>, 'role': <NodeRole.ACCEPTOR: 1>}}
  No slots have reached consensus yet.
> Peer 2 marked UP (heartbeat OK)
Running Coordinate with: [value, slot, skip_prepare] = [A, 98, True]
SKIPPING PREPARE PHASE (AS MULTI PAXOS LEADER; USE LEADER_BALLOT FOR DECISIONS)
Fast foward coordinate, leader_ballot should be set (if not set it when a leader has been chosen) and it should be bigger than any proposal_id seen before..
---------------------------------------------
--------------- FAST_PATH_MULTI_PAXOS (with LEADER avail...) ---------------
---------------------------------------------
---------------------------------------------
--------------- ACCEPT ---------------
---------------------------------------------
Sending Accept-Paxos-Msg with proposal: Proposal(node_id=3, proposal_id=131075, value='A', slot=98), slot:98, value: A
Sending Accept message with proposal: Proposal(node_id=3, proposal_id=131075, value='A', slot=98)
---------------------------------------------
--------------- LEARN ---------------
---------------------------------------------
HELP COORDINATE
Setting Consensus...
CONSENSUS REACHED!
Saving CSV to logs/paxosresult_3_131075.csv
SAVED TO CSV
Node 3 send Learn! type: LEARN
sender_id: 3
proposal_id: 131075
slot: 98
multi {
  slot: 98
  value: "A"
}

Running Coordinate with: [value, slot, skip_prepare] = [B, 78, True]
SKIPPING PREPARE PHASE (AS MULTI PAXOS LEADER; USE LEADER_BALLOT FOR DECISIONS)
Fast foward coordinate, leader_ballot should be set (if not set it when a leader has been chosen) and it should be bigger than any proposal_id seen before..
---------------------------------------------
--------------- FAST_PATH_MULTI_PAXOS (with LEADER avail...) ---------------
---------------------------------------------
---------------------------------------------
--------------- ACCEPT ---------------
---------------------------------------------
Sending Accept-Paxos-Msg with proposal: Proposal(node_id=3, proposal_id=196611, value='B', slot=78), slot:78, value: B
Sending Accept message with proposal: Proposal(node_id=3, proposal_id=196611, value='B', slot=78)
---------------------------------------------
--------------- LEARN ---------------
---------------------------------------------
HELP COORDINATE
Setting Consensus...
CONSENSUS REACHED!
Saving CSV to logs/paxosresult_3_196611.csv
SAVED TO CSV
Node 3 send Learn! type: LEARN
sender_id: 3
proposal_id: 196611
slot: 78
multi {
  slot: 78
  value: "B"
}

Running Coordinate with: [value, slot, skip_prepare] = [C, 75, True]
SKIPPING PREPARE PHASE (AS MULTI PAXOS LEADER; USE LEADER_BALLOT FOR DECISIONS)
Fast foward coordinate, leader_ballot should be set (if not set it when a leader has been chosen) and it should be bigger than any proposal_id seen before..
---------------------------------------------
--------------- FAST_PATH_MULTI_PAXOS (with LEADER avail...) ---------------
---------------------------------------------
---------------------------------------------
--------------- ACCEPT ---------------
---------------------------------------------
Sending Accept-Paxos-Msg with proposal: Proposal(node_id=3, proposal_id=196611, value='C', slot=75), slot:75, value: C
Sending Accept message with proposal: Proposal(node_id=3, proposal_id=196611, value='C', slot=75)
---------------------------------------------
--------------- LEARN ---------------
---------------------------------------------
HELP COORDINATE
Setting Consensus...
CONSENSUS REACHED!
Saving CSV to logs/paxosresult_3_196611.csv
SAVED TO CSV
Node 3 send Learn! type: LEARN
sender_id: 3
proposal_id: 196611
slot: 75
multi {
  slot: 75
  value: "C"
}

Peer 2 marked DOWN (no heartbeat reply)
Peer 2 marked UP (heartbeat OK)
Running Coordinate with: [value, slot, skip_prepare] = [A, 98, True]
SKIPPING PREPARE PHASE (AS MULTI PAXOS LEADER; USE LEADER_BALLOT FOR DECISIONS)
Fast foward coordinate, leader_ballot should be set (if not set it when a leader has been chosen) and it should be bigger than any proposal_id seen before..
---------------------------------------------
--------------- FAST_PATH_MULTI_PAXOS (with LEADER avail...) ---------------
---------------------------------------------
---------------------------------------------
--------------- ACCEPT ---------------
---------------------------------------------
Sending Accept-Paxos-Msg with proposal: Proposal(node_id=3, proposal_id=196611, value='A', slot=98), slot:98, value: A
Sending Accept message with proposal: Proposal(node_id=3, proposal_id=196611, value='A', slot=98)
---------------------------------------------
--------------- LEARN ---------------
---------------------------------------------
HELP COORDINATE
Setting Consensus...
CONSENSUS REACHED!
Saving CSV to logs/paxosresult_3_196611.csv
SAVED TO CSV
Node 3 send Learn! type: LEARN
sender_id: 3
proposal_id: 196611
slot: 98
multi {
  slot: 98
  value: "A"
}

Running Coordinate with: [value, slot, skip_prepare] = [B, 78, True]
SKIPPING PREPARE PHASE (AS MULTI PAXOS LEADER; USE LEADER_BALLOT FOR DECISIONS)
Fast foward coordinate, leader_ballot should be set (if not set it when a leader has been chosen) and it should be bigger than any proposal_id seen before..
---------------------------------------------
--------------- FAST_PATH_MULTI_PAXOS (with LEADER avail...) ---------------
---------------------------------------------
---------------------------------------------
--------------- ACCEPT ---------------
---------------------------------------------
Sending Accept-Paxos-Msg with proposal: Proposal(node_id=3, proposal_id=262147, value='B', slot=78), slot:78, value: B
Sending Accept message with proposal: Proposal(node_id=3, proposal_id=262147, value='B', slot=78)
---------------------------------------------
--------------- LEARN ---------------
---------------------------------------------
HELP COORDINATE
Setting Consensus...
CONSENSUS REACHED!
Saving CSV to logs/paxosresult_3_262147.csv
SAVED TO CSV
Node 3 send Learn! type: LEARN
sender_id: 3
proposal_id: 262147
slot: 78
multi {
  slot: 78
  value: "B"
}

Running Coordinate with: [value, slot, skip_prepare] = [C, 75, True]
SKIPPING PREPARE PHASE (AS MULTI PAXOS LEADER; USE LEADER_BALLOT FOR DECISIONS)
Fast foward coordinate, leader_ballot should be set (if not set it when a leader has been chosen) and it should be bigger than any proposal_id seen before..
---------------------------------------------
--------------- FAST_PATH_MULTI_PAXOS (with LEADER avail...) ---------------
---------------------------------------------
---------------------------------------------
--------------- ACCEPT ---------------
---------------------------------------------
Sending Accept-Paxos-Msg with proposal: Proposal(node_id=3, proposal_id=262147, value='C', slot=75), slot:75, value: C
Sending Accept message with proposal: Proposal(node_id=3, proposal_id=262147, value='C', slot=75)
---------------------------------------------
--------------- LEARN ---------------
---------------------------------------------
HELP COORDINATE
Setting Consensus...
CONSENSUS REACHED!
Saving CSV to logs/paxosresult_3_262147.csv
SAVED TO CSV
Node 3 send Learn! type: LEARN
sender_id: 3
proposal_id: 262147
slot: 75
multi {
  slot: 75
  value: "C"
}

Peer 1 marked DOWN (no heartbeat reply)

# REPL-command
state
Node 3: running=True leader=3
peers: {1: ('10.10.0.1', 5001), 2: ('10.10.0.2', 5002)}
peer_state: {1: {'last_heartbeat': 173, 'state': <NodeState.DOWN: 2>, 'role': <NodeRole.LEARNER: 3>}, 2: {'last_heartbeat': 4709, 'state': <NodeState.UP: 1>, 'role': <NodeRole.LEARNER: 3>}}
  Slots with consensus:
    slot 75: accepted_id=262147, accepted_value=C
    slot 78: accepted_id=262147, accepted_value=B
    slot 98: accepted_id=196611, accepted_value=A

``` 
