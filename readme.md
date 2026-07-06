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

Linux namespaces execution commands:
 - 1. make install && python3 setup_network.py
 - 2. ansible-playbook -i inventories/inventory_netns.yml playbooks/run_netns.yml --ask-become-pass
  (this inventory excludes self, so we can execute a seperate instance that isnt just "LISTENING")
    - 3. 
        3.1 this -> python3 src/paxos/paxos_async.py --inventory inventories/inventory_lab_min.yml --repl (interactive mode with "/help")
        3.2 or -> python3 src/paxos/paxos_async.py --inventory inventories/inventory_lab_min.yml --proposal 'valueToBeStoredinSlot5' 5 'AnotherValueToSlot12' 12

+----+

  Labor-Environment:
    - 1. make install
    - 2. ansible-playbook -i inventories/inventory_lab_min_self.yml playbooks/03_wol.yaml
     (this inventory excludes self, so we can execute a seperate instance that isnt just "LISTENING")
    - 3. 
        3.1 this -> python3 src/paxos/paxos_async.py --inventory inventories/inventory_lab_min.yml --repl (interactive mode with "/help")
        3.2 or -> python3 src/paxos/paxos_async.py --inventory inventories/inventory_lab_min.yml --proposal 'valueToBeStoredinSlot5' 5 'AnotherValueToSlot12' 12


+----+
