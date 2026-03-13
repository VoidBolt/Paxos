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
