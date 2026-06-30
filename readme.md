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


Lab Issues establishing ssh, via password and copying public-key

(venv) s80697@pool-hp49d14-l:~/Paxos$ ansible-playbook -i inventories/inventory_lab.yml playbooks/ping_nodes_lab.yml 

PLAY [Ping every lab machine] **************************************************************************

TASK [Ping every other host] ***************************************************************************
fatal: [pool-8P49D14]: FAILED! => {"msg": "to use the 'ssh' connection type with passwords or pkcs11_provider, you must install the sshpass program"}
...ignoring
fatal: [pool-8Q49D14]: FAILED! => {"msg": "to use the 'ssh' connection type with passwords or pkcs11_provider, you must install the sshpass program"}
...ignoring
fatal: [pool-9N49D14]: FAILED! => {"msg": "to use the 'ssh' connection type with passwords or pkcs11_provider, you must install the sshpass program"}
...ignoring
fatal: [pool-9P49D14]: FAILED! => {"msg": "to use the 'ssh' connection type with passwords or pkcs11_provider, you must install the sshpass program"}
...ignoring
fatal: [pool-9Q49D14]: FAILED! => {"msg": "to use the 'ssh' connection type with passwords or pkcs11_provider, you must install the sshpass program"}
...ignoring
fatal: [pool-BN49D14]: FAILED! => {"msg": "to use the 'ssh' connection type with passwords or pkcs11_provider, you must install the sshpass program"}
...ignoring
fatal: [pool-BP49D14]: FAILED! => {"msg": "to use the 'ssh' connection type with passwords or pkcs11_provider, you must install the sshpass program"}
...ignoring
fatal: [pool-BQ49D14]: FAILED! => {"msg": "to use the 'ssh' connection type with passwords or pkcs11_provider, you must install the sshpass program"}
...ignoring
fatal: [pool-CN49D14]: FAILED! => {"msg": "to use the 'ssh' connection type with passwords or pkcs11_provider, you must install the sshpass program"}
...ignoring
fatal: [pool-CP49D14]: FAILED! => {"msg": "to use the 'ssh' connection type with passwords or pkcs11_provider, you must install the sshpass program"}
...ignoring
fatal: [pool-CQ49D14]: FAILED! => {"msg": "to use the 'ssh' connection type with passwords or pkcs11_provider, you must install the sshpass program"}
...ignoring
fatal: [pool-DN49D14]: FAILED! => {"msg": "to use the 'ssh' connection type with passwords or pkcs11_provider, you must install the sshpass program"}
...ignoring
fatal: [pool-DP49D14]: FAILED! => {"msg": "to use the 'ssh' connection type with passwords or pkcs11_provider, you must install the sshpass program"}
...ignoring
fatal: [pool-JN49D14]: FAILED! => {"msg": "to use the 'ssh' connection type with passwords or pkcs11_provider, you must install the sshpass program"}
...ignoring
fatal: [pool-FP49D14]: FAILED! => {"msg": "to use the 'ssh' connection type with passwords or pkcs11_provider, you must install the sshpass program"}
...ignoring
fatal: [pool-GM49D14]: FAILED! => {"msg": "to use the 'ssh' connection type with passwords or pkcs11_provider, you must install the sshpass program"}
...ignoring
fatal: [pool-GN49D14]: FAILED! => {"msg": "to use the 'ssh' connection type with passwords or pkcs11_provider, you must install the sshpass program"}
...ignoring
fatal: [pool-GP49D14]: FAILED! => {"msg": "to use the 'ssh' connection type with passwords or pkcs11_provider, you must install the sshpass program"}
...ignoring
fatal: [pool-HM49D14]: FAILED! => {"msg": "to use the 'ssh' connection type with passwords or pkcs11_provider, you must install the sshpass program"}
...ignoring
fatal: [pool-HN49D14]: FAILED! => {"msg": "to use the 'ssh' connection type with passwords or pkcs11_provider, you must install the sshpass program"}
...ignoring
fatal: [pool-HP49D14]: FAILED! => {"msg": "to use the 'ssh' connection type with passwords or pkcs11_provider, you must install the sshpass program"}
...ignoring
fatal: [pool-JM49D14]: FAILED! => {"msg": "to use the 'ssh' connection type with passwords or pkcs11_provider, you must install the sshpass program"}
...ignoring
fatal: [pool-1N49D14]: FAILED! => {"msg": "to use the 'ssh' connection type with passwords or pkcs11_provider, you must install the sshpass program"}
...ignoring
fatal: [pool-1P49D14]: FAILED! => {"msg": "to use the 'ssh' connection type with passwords or pkcs11_provider, you must install the sshpass program"}
...ignoring
fatal: [pool-1Q49D14]: FAILED! => {"msg": "to use the 'ssh' connection type with passwords or pkcs11_provider, you must install the sshpass program"}
...ignoring
fatal: [pool-2N49D14]: FAILED! => {"msg": "to use the 'ssh' connection type with passwords or pkcs11_provider, you must install the sshpass program"}
...ignoring
fatal: [pool-2P49D14]: FAILED! => {"msg": "to use the 'ssh' connection type with passwords or pkcs11_provider, you must install the sshpass program"}
...ignoring
fatal: [pool-2Q49D14]: FAILED! => {"msg": "to use the 'ssh' connection type with passwords or pkcs11_provider, you must install the sshpass program"}
...ignoring
fatal: [pool-3N49D14]: FAILED! => {"msg": "to use the 'ssh' connection type with passwords or pkcs11_provider, you must install the sshpass program"}
...ignoring
fatal: [pool-3P49D14]: FAILED! => {"msg": "to use the 'ssh' connection type with passwords or pkcs11_provider, you must install the sshpass program"}
...ignoring
fatal: [pool-3Q49D14]: FAILED! => {"msg": "to use the 'ssh' connection type with passwords or pkcs11_provider, you must install the sshpass program"}
...ignoring
fatal: [pool-4N49D14]: FAILED! => {"msg": "to use the 'ssh' connection type with passwords or pkcs11_provider, you must install the sshpass program"}
...ignoring
fatal: [pool-4P49D14]: FAILED! => {"msg": "to use the 'ssh' connection type with passwords or pkcs11_provider, you must install the sshpass program"}
...ignoring
fatal: [pool-4Q49D14]: FAILED! => {"msg": "to use the 'ssh' connection type with passwords or pkcs11_provider, you must install the sshpass program"}
...ignoring
fatal: [pool-5N49D14]: FAILED! => {"msg": "to use the 'ssh' connection type with passwords or pkcs11_provider, you must install the sshpass program"}
...ignoring
fatal: [pool-5P49D14]: FAILED! => {"msg": "to use the 'ssh' connection type with passwords or pkcs11_provider, you must install the sshpass program"}
...ignoring
fatal: [pool-5Q49D14]: FAILED! => {"msg": "to use the 'ssh' connection type with passwords or pkcs11_provider, you must install the sshpass program"}
...ignoring
fatal: [pool-6N49D14]: FAILED! => {"msg": "to use the 'ssh' connection type with passwords or pkcs11_provider, you must install the sshpass program"}
...ignoring
fatal: [pool-6P49D14]: FAILED! => {"msg": "to use the 'ssh' connection type with passwords or pkcs11_provider, you must install the sshpass program"}
...ignoring
fatal: [pool-6Q49D14]: FAILED! => {"msg": "to use the 'ssh' connection type with passwords or pkcs11_provider, you must install the sshpass program"}
...ignoring
fatal: [pool-7N49D14]: FAILED! => {"msg": "to use the 'ssh' connection type with passwords or pkcs11_provider, you must install the sshpass program"}
...ignoring
fatal: [pool-7P49D14]: FAILED! => {"msg": "to use the 'ssh' connection type with passwords or pkcs11_provider, you must install the sshpass program"}
...ignoring
fatal: [pool-7Q49D14]: FAILED! => {"msg": "to use the 'ssh' connection type with passwords or pkcs11_provider, you must install the sshpass program"}
...ignoring
fatal: [pool-8N49D14]: FAILED! => {"msg": "to use the 'ssh' connection type with passwords or pkcs11_provider, you must install the sshpass program"}
...ignoring

TASK [debug] *******************************************************************************************
fatal: [pool-8P49D14]: FAILED! => {"msg": "'dict object' has no attribute 'results'. 'dict object' has no attribute 'results'"}
fatal: [pool-8Q49D14]: FAILED! => {"msg": "'dict object' has no attribute 'results'. 'dict object' has no attribute 'results'"}
fatal: [pool-9N49D14]: FAILED! => {"msg": "'dict object' has no attribute 'results'. 'dict object' has no attribute 'results'"}
fatal: [pool-9P49D14]: FAILED! => {"msg": "'dict object' has no attribute 'results'. 'dict object' has no attribute 'results'"}
fatal: [pool-9Q49D14]: FAILED! => {"msg": "'dict object' has no attribute 'results'. 'dict object' has no attribute 'results'"}
fatal: [pool-BN49D14]: FAILED! => {"msg": "'dict object' has no attribute 'results'. 'dict object' has no attribute 'results'"}
fatal: [pool-BP49D14]: FAILED! => {"msg": "'dict object' has no attribute 'results'. 'dict object' has no attribute 'results'"}
fatal: [pool-BQ49D14]: FAILED! => {"msg": "'dict object' has no attribute 'results'. 'dict object' has no attribute 'results'"}
fatal: [pool-CN49D14]: FAILED! => {"msg": "'dict object' has no attribute 'results'. 'dict object' has no attribute 'results'"}
fatal: [pool-CP49D14]: FAILED! => {"msg": "'dict object' has no attribute 'results'. 'dict object' has no attribute 'results'"}
fatal: [pool-CQ49D14]: FAILED! => {"msg": "'dict object' has no attribute 'results'. 'dict object' has no attribute 'results'"}
fatal: [pool-DN49D14]: FAILED! => {"msg": "'dict object' has no attribute 'results'. 'dict object' has no attribute 'results'"}
fatal: [pool-DP49D14]: FAILED! => {"msg": "'dict object' has no attribute 'results'. 'dict object' has no attribute 'results'"}
fatal: [pool-JN49D14]: FAILED! => {"msg": "'dict object' has no attribute 'results'. 'dict object' has no attribute 'results'"}
fatal: [pool-FP49D14]: FAILED! => {"msg": "'dict object' has no attribute 'results'. 'dict object' has no attribute 'results'"}
fatal: [pool-GM49D14]: FAILED! => {"msg": "'dict object' has no attribute 'results'. 'dict object' has no attribute 'results'"}
fatal: [pool-GN49D14]: FAILED! => {"msg": "'dict object' has no attribute 'results'. 'dict object' has no attribute 'results'"}
fatal: [pool-GP49D14]: FAILED! => {"msg": "'dict object' has no attribute 'results'. 'dict object' has no attribute 'results'"}
fatal: [pool-HM49D14]: FAILED! => {"msg": "'dict object' has no attribute 'results'. 'dict object' has no attribute 'results'"}
fatal: [pool-HN49D14]: FAILED! => {"msg": "'dict object' has no attribute 'results'. 'dict object' has no attribute 'results'"}
fatal: [pool-HP49D14]: FAILED! => {"msg": "'dict object' has no attribute 'results'. 'dict object' has no attribute 'results'"}
fatal: [pool-JM49D14]: FAILED! => {"msg": "'dict object' has no attribute 'results'. 'dict object' has no attribute 'results'"}
fatal: [pool-1N49D14]: FAILED! => {"msg": "'dict object' has no attribute 'results'. 'dict object' has no attribute 'results'"}
fatal: [pool-1P49D14]: FAILED! => {"msg": "'dict object' has no attribute 'results'. 'dict object' has no attribute 'results'"}
fatal: [pool-1Q49D14]: FAILED! => {"msg": "'dict object' has no attribute 'results'. 'dict object' has no attribute 'results'"}
fatal: [pool-2N49D14]: FAILED! => {"msg": "'dict object' has no attribute 'results'. 'dict object' has no attribute 'results'"}
fatal: [pool-2P49D14]: FAILED! => {"msg": "'dict object' has no attribute 'results'. 'dict object' has no attribute 'results'"}
fatal: [pool-2Q49D14]: FAILED! => {"msg": "'dict object' has no attribute 'results'. 'dict object' has no attribute 'results'"}
fatal: [pool-3N49D14]: FAILED! => {"msg": "'dict object' has no attribute 'results'. 'dict object' has no attribute 'results'"}
fatal: [pool-3P49D14]: FAILED! => {"msg": "'dict object' has no attribute 'results'. 'dict object' has no attribute 'results'"}
fatal: [pool-3Q49D14]: FAILED! => {"msg": "'dict object' has no attribute 'results'. 'dict object' has no attribute 'results'"}
fatal: [pool-4N49D14]: FAILED! => {"msg": "'dict object' has no attribute 'results'. 'dict object' has no attribute 'results'"}
fatal: [pool-4P49D14]: FAILED! => {"msg": "'dict object' has no attribute 'results'. 'dict object' has no attribute 'results'"}
fatal: [pool-4Q49D14]: FAILED! => {"msg": "'dict object' has no attribute 'results'. 'dict object' has no attribute 'results'"}
fatal: [pool-5N49D14]: FAILED! => {"msg": "'dict object' has no attribute 'results'. 'dict object' has no attribute 'results'"}
fatal: [pool-5P49D14]: FAILED! => {"msg": "'dict object' has no attribute 'results'. 'dict object' has no attribute 'results'"}
fatal: [pool-5Q49D14]: FAILED! => {"msg": "'dict object' has no attribute 'results'. 'dict object' has no attribute 'results'"}
fatal: [pool-6N49D14]: FAILED! => {"msg": "'dict object' has no attribute 'results'. 'dict object' has no attribute 'results'"}
fatal: [pool-6P49D14]: FAILED! => {"msg": "'dict object' has no attribute 'results'. 'dict object' has no attribute 'results'"}
fatal: [pool-6Q49D14]: FAILED! => {"msg": "'dict object' has no attribute 'results'. 'dict object' has no attribute 'results'"}
fatal: [pool-7N49D14]: FAILED! => {"msg": "'dict object' has no attribute 'results'. 'dict object' has no attribute 'results'"}
fatal: [pool-7P49D14]: FAILED! => {"msg": "'dict object' has no attribute 'results'. 'dict object' has no attribute 'results'"}
fatal: [pool-7Q49D14]: FAILED! => {"msg": "'dict object' has no attribute 'results'. 'dict object' has no attribute 'results'"}
fatal: [pool-8N49D14]: FAILED! => {"msg": "'dict object' has no attribute 'results'. 'dict object' has no attribute 'results'"}

PLAY RECAP *********************************************************************************************
pool-1N49D14               : ok=1    changed=0    unreachable=0    failed=1    skipped=0    rescued=0    ignored=1   
pool-1P49D14               : ok=1    changed=0    unreachable=0    failed=1    skipped=0    rescued=0    ignored=1   
pool-1Q49D14               : ok=1    changed=0    unreachable=0    failed=1    skipped=0    rescued=0    ignored=1   
pool-2N49D14               : ok=1    changed=0    unreachable=0    failed=1    skipped=0    rescued=0    ignored=1   
pool-2P49D14               : ok=1    changed=0    unreachable=0    failed=1    skipped=0    rescued=0    ignored=1   
pool-2Q49D14               : ok=1    changed=0    unreachable=0    failed=1    skipped=0    rescued=0    ignored=1   
pool-3N49D14               : ok=1    changed=0    unreachable=0    failed=1    skipped=0    rescued=0    ignored=1   
pool-3P49D14               : ok=1    changed=0    unreachable=0    failed=1    skipped=0    rescued=0    ignored=1   
pool-3Q49D14               : ok=1    changed=0    unreachable=0    failed=1    skipped=0    rescued=0    ignored=1   
pool-4N49D14               : ok=1    changed=0    unreachable=0    failed=1    skipped=0    rescued=0    ignored=1   
pool-4P49D14               : ok=1    changed=0    unreachable=0    failed=1    skipped=0    rescued=0    ignored=1   
pool-4Q49D14               : ok=1    changed=0    unreachable=0    failed=1    skipped=0    rescued=0    ignored=1   
pool-5N49D14               : ok=1    changed=0    unreachable=0    failed=1    skipped=0    rescued=0    ignored=1   
pool-5P49D14               : ok=1    changed=0    unreachable=0    failed=1    skipped=0    rescued=0    ignored=1   
pool-5Q49D14               : ok=1    changed=0    unreachable=0    failed=1    skipped=0    rescued=0    ignored=1   
pool-6N49D14               : ok=1    changed=0    unreachable=0    failed=1    skipped=0    rescued=0    ignored=1   
pool-6P49D14               : ok=1    changed=0    unreachable=0    failed=1    skipped=0    rescued=0    ignored=1   
pool-6Q49D14               : ok=1    changed=0    unreachable=0    failed=1    skipped=0    rescued=0    ignored=1   
pool-7N49D14               : ok=1    changed=0    unreachable=0    failed=1    skipped=0    rescued=0    ignored=1   
pool-7P49D14               : ok=1    changed=0    unreachable=0    failed=1    skipped=0    rescued=0    ignored=1   
pool-7Q49D14               : ok=1    changed=0    unreachable=0    failed=1    skipped=0    rescued=0    ignored=1   
pool-8N49D14               : ok=1    changed=0    unreachable=0    failed=1    skipped=0    rescued=0    ignored=1   
pool-8P49D14               : ok=1    changed=0    unreachable=0    failed=1    skipped=0    rescued=0    ignored=1   
pool-8Q49D14               : ok=1    changed=0    unreachable=0    failed=1    skipped=0    rescued=0    ignored=1   
pool-9N49D14               : ok=1    changed=0    unreachable=0    failed=1    skipped=0    rescued=0    ignored=1   
pool-9P49D14               : ok=1    changed=0    unreachable=0    failed=1    skipped=0    rescued=0    ignored=1   
pool-9Q49D14               : ok=1    changed=0    unreachable=0    failed=1    skipped=0    rescued=0    ignored=1   
pool-BN49D14               : ok=1    changed=0    unreachable=0    failed=1    skipped=0    rescued=0    ignored=1   
pool-BP49D14               : ok=1    changed=0    unreachable=0    failed=1    skipped=0    rescued=0    ignored=1   
pool-BQ49D14               : ok=1    changed=0    unreachable=0    failed=1    skipped=0    rescued=0    ignored=1   
pool-CN49D14               : ok=1    changed=0    unreachable=0    failed=1    skipped=0    rescued=0    ignored=1   
pool-CP49D14               : ok=1    changed=0    unreachable=0    failed=1    skipped=0    rescued=0    ignored=1   
pool-CQ49D14               : ok=1    changed=0    unreachable=0    failed=1    skipped=0    rescued=0    ignored=1   
pool-DN49D14               : ok=1    changed=0    unreachable=0    failed=1    skipped=0    rescued=0    ignored=1   
pool-DP49D14               : ok=1    changed=0    unreachable=0    failed=1    skipped=0    rescued=0    ignored=1   
pool-FP49D14               : ok=1    changed=0    unreachable=0    failed=1    skipped=0    rescued=0    ignored=1   
pool-GM49D14               : ok=1    changed=0    unreachable=0    failed=1    skipped=0    rescued=0    ignored=1   
pool-GN49D14               : ok=1    changed=0    unreachable=0    failed=1    skipped=0    rescued=0    ignored=1   
pool-GP49D14               : ok=1    changed=0    unreachable=0    failed=1    skipped=0    rescued=0    ignored=1   
pool-HM49D14               : ok=1    changed=0    unreachable=0    failed=1    skipped=0    rescued=0    ignored=1   
pool-HN49D14               : ok=1    changed=0    unreachable=0    failed=1    skipped=0    rescued=0    ignored=1   
pool-HP49D14               : ok=1    changed=0    unreachable=0    failed=1    skipped=0    rescued=0    ignored=1   
pool-JM49D14               : ok=1    changed=0    unreachable=0    failed=1    skipped=0    rescued=0    ignored=1   
pool-JN49D14               : ok=1    changed=0    unreachable=0    failed=1    skipped=0    rescued=0    ignored=1   

(venv) s80697@pool-hp49d14-l:~/Paxos$ ssh s80697@pool-8P49D14.ris.bht-berlin.de
sign_and_send_pubkey: signing failed for ED25519 "/home/campus/s80697/.ssh/id_ed25519" from agent: agent refused operation
s80697@pool-8p49d14.ris.bht-berlin.de's password: 

(venv) s80697@pool-hp49d14-l:~/Paxos$ ssh s80697@pool-8P49D14.ris.bht-berlin.de^C
(venv) s80697@pool-hp49d14-l:~/Paxos$ ssh -i /tmp/id_ed25519 s80697@pool-8P49D14.ris.bht-berlin.de
Warning: Identity file /tmp/id_ed25519 not accessible: No such file or directory.
sign_and_send_pubkey: signing failed for ED25519 "/home/campus/s80697/.ssh/id_ed25519" from agent: agent refused operation
s80697@pool-8p49d14.ris.bht-berlin.de's password: 

(venv) s80697@pool-hp49d14-l:~/Paxos$ ^C
(venv) s80697@pool-hp49d14-l:~/Paxos$ ^C
(venv) s80697@pool-hp49d14-l:~/Paxos$ ssh-keygen
Generating public/private rsa key pair.
Enter file in which to save the key (/home/campus/s80697/.ssh/id_rsa): ^C
(venv) s80697@pool-hp49d14-l:~/Paxos$ ^C
(venv) s80697@pool-hp49d14-l:~/Paxos$ ^C
(venv) s80697@pool-hp49d14-l:~/Paxos$ ssh-keygen -t ed25519 -f /tmp/id_25519 -N ""
Generating public/private ed25519 key pair.
Your identification has been saved in /tmp/id_25519
Your public key has been saved in /tmp/id_25519.pub
The key fingerprint is:
SHA256:D8FGpwnPUDezfyG+43VMP9cmO7ABVX4uTL2r/8i2NfQ s80697@pool-hp49d14-l
The key's randomart image is:
+--[ED25519 256]--+
|      o.o =  ..  |
|       B = +.. . |
|        O ... + o|
|       . ..o + +.|
|        S  .o +oo|
|         o  oo.+=|
|          . o+o+E|
|           ..++B+|
|            .o*+o|
+----[SHA256]-----+
(venv) s80697@pool-hp49d14-l:~/Paxos$ ls /tmp/
adcli-krb5-dX6oOP
id_25519
id_25519.pub
krb5cc_276862935_BJcLBu
snap-private-tmp
systemd-private-2f2918868b3a445cbefa00c6d7b7d147-bluetooth.service-X6JLmS
systemd-private-2f2918868b3a445cbefa00c6d7b7d147-colord.service-w6csAv
systemd-private-2f2918868b3a445cbefa00c6d7b7d147-fwupd.service-jl26Nj
systemd-private-2f2918868b3a445cbefa00c6d7b7d147-geoclue.service-UuhBbm
systemd-private-2f2918868b3a445cbefa00c6d7b7d147-lldpd.service-pDVtoU
systemd-private-2f2918868b3a445cbefa00c6d7b7d147-low-memory-monitor.service-5S4Een
systemd-private-2f2918868b3a445cbefa00c6d7b7d147-ModemManager.service-1UGDxK
systemd-private-2f2918868b3a445cbefa00c6d7b7d147-power-profiles-daemon.service-fbYSga
systemd-private-2f2918868b3a445cbefa00c6d7b7d147-switcheroo-control.service-VNIPaR
systemd-private-2f2918868b3a445cbefa00c6d7b7d147-systemd-logind.service-LkDNDd
systemd-private-2f2918868b3a445cbefa00c6d7b7d147-systemd-timesyncd.service-w1i3ga
systemd-private-2f2918868b3a445cbefa00c6d7b7d147-upower.service-vVHofc
tracker-extract-3-files.114
(venv) s80697@pool-hp49d14-l:~/Paxos$ ssh-copy-id -i /tmp/id_25519.pub s80697@pool-8P49D14.ris.bht-berlin.de
/usr/bin/ssh-copy-id: INFO: Source of key(s) to be installed: "/tmp/id_25519.pub"
/usr/bin/ssh-copy-id: INFO: attempting to log in with the new key(s), to filter out any that are already installed
/usr/bin/ssh-copy-id: INFO: 1 key(s) remain to be installed -- if you are prompted now it is to install the new keys
sign_and_send_pubkey: signing failed for ED25519 "/home/campus/s80697/.ssh/id_ed25519" from agent: agent refused operation
s80697@pool-8p49d14.ris.bht-berlin.de's password: 

Number of key(s) added: 1

Now try logging into the machine, with:   "ssh 's80697@pool-8P49D14.ris.bht-berlin.de'"
and check to make sure that only the key(s) you wanted were added.

(venv) s80697@pool-hp49d14-l:~/Paxos$ ssh 's80697@pool-8P49D14.ris.bht-berlin.de'
sign_and_send_pubkey: signing failed for ED25519 "/home/campus/s80697/.ssh/id_ed25519" from agent: agent refused operation
s80697@pool-8p49d14.ris.bht-berlin.de's password: 
Linux pool-8P49D14-l 6.1.0-47-amd64 #1 SMP PREEMPT_DYNAMIC Debian 6.1.170-3 (2026-05-08) x86_64

The programs included with the Debian GNU/Linux system are free software;
the exact distribution terms for each program are described in the
individual files in /usr/share/doc/*/copyright.

Debian GNU/Linux comes with ABSOLUTELY NO WARRANTY, to the extent
permitted by applicable law.
Last login: Mon Jun 29 15:34:31 2026 from 141.64.89.80
s80697@pool-8P49D14-l:~$ ls /tmp/
adcli-krb5-ZvE9UX
dbus-eohptyeI9Z
krb5cc_276862935_ejCLyi
snap-private-tmp
systemd-private-895a5a802aaf429d9da279553e380d81-bluetooth.service-rvcvnA
systemd-private-895a5a802aaf429d9da279553e380d81-colord.service-lpVOuV
systemd-private-895a5a802aaf429d9da279553e380d81-lldpd.service-lQ4KaB
systemd-private-895a5a802aaf429d9da279553e380d81-low-memory-monitor.service-Vcghmf
systemd-private-895a5a802aaf429d9da279553e380d81-ModemManager.service-cVTarW
systemd-private-895a5a802aaf429d9da279553e380d81-power-profiles-daemon.service-LBmcC1
systemd-private-895a5a802aaf429d9da279553e380d81-switcheroo-control.service-44uEOS
systemd-private-895a5a802aaf429d9da279553e380d81-systemd-logind.service-ZCtgum
systemd-private-895a5a802aaf429d9da279553e380d81-systemd-timesyncd.service-cTFFTj
systemd-private-895a5a802aaf429d9da279553e380d81-upower.service-iktX0h
tracker-extract-3-files.114
s80697@pool-8P49D14-l:~$ ^C
s80697@pool-8P49D14-l:~$ ^C
s80697@pool-8P49D14-l:~$ ^C
s80697@pool-8P49D14-l:~$ 
Abgemeldet
Connection to pool-8p49d14.ris.bht-berlin.de closed.
(venv) s80697@pool-hp49d14-l:~/Paxos$ ls /tmp/
adcli-krb5-dX6oOP
id_25519
id_25519.pub
krb5cc_276862935_BJcLBu
snap-private-tmp
systemd-private-2f2918868b3a445cbefa00c6d7b7d147-bluetooth.service-X6JLmS
systemd-private-2f2918868b3a445cbefa00c6d7b7d147-colord.service-w6csAv
systemd-private-2f2918868b3a445cbefa00c6d7b7d147-fwupd.service-jl26Nj
systemd-private-2f2918868b3a445cbefa00c6d7b7d147-geoclue.service-UuhBbm
systemd-private-2f2918868b3a445cbefa00c6d7b7d147-lldpd.service-pDVtoU
systemd-private-2f2918868b3a445cbefa00c6d7b7d147-low-memory-monitor.service-5S4Een
systemd-private-2f2918868b3a445cbefa00c6d7b7d147-ModemManager.service-1UGDxK
systemd-private-2f2918868b3a445cbefa00c6d7b7d147-power-profiles-daemon.service-fbYSga
systemd-private-2f2918868b3a445cbefa00c6d7b7d147-switcheroo-control.service-VNIPaR
systemd-private-2f2918868b3a445cbefa00c6d7b7d147-systemd-logind.service-LkDNDd
systemd-private-2f2918868b3a445cbefa00c6d7b7d147-systemd-timesyncd.service-w1i3ga
systemd-private-2f2918868b3a445cbefa00c6d7b7d147-upower.service-vVHofc
tracker-extract-3-files.114

(venv) s80697@pool-hp49d14-l:~/Paxos$ ssh-keygen -t ed25519 -f /tmp/id_ed25519 -N ""
Generating public/private ed25519 key pair.
Your identification has been saved in /tmp/id_ed25519
Your public key has been saved in /tmp/id_ed25519.pub
The key fingerprint is:
SHA256:/b099QgTNVFICU+U3rdGz0dM2GTvzSw+MZVs/b7pGEE s80697@pool-hp49d14-l
The key's randomart image is:
+--[ED25519 256]--+
|            .+=X+|
|             oO.*|
|             E.O+|
|         .  o o*B|
|        S .  o=oX|
|           .oo.B=|
|            .+=.=|
|              +=+|
|             .o+o|
+----[SHA256]-----+
(venv) s80697@pool-hp49d14-l:~/Paxos$ ssh-keygen -t ed25519 -f /tmp/id_ed25519 -N ""^C
(venv) s80697@pool-hp49d14-l:~/Paxos$ ssh-copy-id -i /tmp/id_ed25519.pub s80697@pool-8P49D14.ris.bht-berlin.de
/usr/bin/ssh-copy-id: INFO: Source of key(s) to be installed: "/tmp/id_ed25519.pub"
/usr/bin/ssh-copy-id: INFO: attempting to log in with the new key(s), to filter out any that are already installed
/usr/bin/ssh-copy-id: INFO: 1 key(s) remain to be installed -- if you are prompted now it is to install the new keys
sign_and_send_pubkey: signing failed for ED25519 "/home/campus/s80697/.ssh/id_ed25519" from agent: agent refused operation
s80697@pool-8p49d14.ris.bht-berlin.de's password: 

Number of key(s) added: 1

Now try logging into the machine, with:   "ssh 's80697@pool-8P49D14.ris.bht-berlin.de'"
and check to make sure that only the key(s) you wanted were added.

(venv) s80697@pool-hp49d14-l:~/Paxos$ 



Numerous Issues with connecting with a publickey made it hard to establish a working environment in the lab to collect data with my Algorithm.

-----------------------------------------------------------

SUCCESS -> Some of the machines were still not reachable so i commented them out from the inventory.

So I created a seperate "inventories/inventory_lab_min.yml" which contained all the machines reachable.

I then removed myself (Machine: pool-HP49D14) from the inventory file, which allows me to be the proposer during execution, now at the current working stage there always has been a REPL execution established for the Server to keep running, I assume that ansible will just exit without allowing this to happen. So I will have to add some Mechanism for the instances to keep running after orchestration.

Ping-Execution-Result:

s80697@pool-hp49d14-l:~/Dokumente/Projekte/Paxos$ ansible-playbook -i inventories/inventory_lab_min.yml playbooks/ping_nodes_lab.yml

PLAY [Ping every lab machine] **************************************************************************

TASK [Ping every other host] ***************************************************************************
changed: [pool-8Q49D14] => (item=pool-8P49D14)
changed: [pool-BN49D14] => (item=pool-8P49D14)
changed: [pool-8P49D14] => (item=pool-8P49D14)
changed: [pool-BP49D14] => (item=pool-8P49D14)
changed: [pool-9N49D14] => (item=pool-8P49D14)
changed: [pool-8P49D14] => (item=pool-8Q49D14)
changed: [pool-BN49D14] => (item=pool-8Q49D14)
changed: [pool-BP49D14] => (item=pool-8Q49D14)
changed: [pool-8Q49D14] => (item=pool-8Q49D14)
changed: [pool-9N49D14] => (item=pool-8Q49D14)
changed: [pool-8P49D14] => (item=pool-9N49D14)
changed: [pool-BP49D14] => (item=pool-9N49D14)
changed: [pool-BN49D14] => (item=pool-9N49D14)
changed: [pool-8Q49D14] => (item=pool-9N49D14)
changed: [pool-9N49D14] => (item=pool-9N49D14)
changed: [pool-BP49D14] => (item=pool-BN49D14)
changed: [pool-8Q49D14] => (item=pool-BN49D14)
changed: [pool-BN49D14] => (item=pool-BN49D14)
changed: [pool-8P49D14] => (item=pool-BN49D14)
changed: [pool-9N49D14] => (item=pool-BN49D14)
changed: [pool-8P49D14] => (item=pool-BP49D14)
changed: [pool-9N49D14] => (item=pool-BP49D14)
changed: [pool-BN49D14] => (item=pool-BP49D14)
changed: [pool-8Q49D14] => (item=pool-BP49D14)
changed: [pool-BP49D14] => (item=pool-BP49D14)
changed: [pool-8P49D14] => (item=pool-HN49D14)
changed: [pool-BN49D14] => (item=pool-HN49D14)
changed: [pool-8Q49D14] => (item=pool-HN49D14)
changed: [pool-BP49D14] => (item=pool-HN49D14)
changed: [pool-9N49D14] => (item=pool-HN49D14)
changed: [pool-BP49D14] => (item=pool-HP49D14)
changed: [pool-9N49D14] => (item=pool-HP49D14)
changed: [pool-BN49D14] => (item=pool-HP49D14)
changed: [pool-8Q49D14] => (item=pool-HP49D14)
changed: [pool-8P49D14] => (item=pool-HP49D14)
changed: [pool-HP49D14] => (item=pool-8P49D14)
changed: [pool-HP49D14] => (item=pool-8Q49D14)
changed: [pool-HN49D14] => (item=pool-8P49D14)
changed: [pool-HP49D14] => (item=pool-9N49D14)
changed: [pool-HN49D14] => (item=pool-8Q49D14)
changed: [pool-HP49D14] => (item=pool-BN49D14)
changed: [pool-HN49D14] => (item=pool-9N49D14)
changed: [pool-HP49D14] => (item=pool-BP49D14)
changed: [pool-HN49D14] => (item=pool-BN49D14)
changed: [pool-HP49D14] => (item=pool-HN49D14)
changed: [pool-HN49D14] => (item=pool-BP49D14)
changed: [pool-HP49D14] => (item=pool-HP49D14)
changed: [pool-HN49D14] => (item=pool-HN49D14)
changed: [pool-HN49D14] => (item=pool-HP49D14)

TASK [debug] *******************************************************************************************
ok: [pool-8P49D14] => (item={'changed': True, 'stdout': 'PING pool-8P49D14.ris.bht-berlin.de (141.64.89.60) 56(84) bytes of data.\n64 bytes from pool-8p49d14.ris.bht-berlin.de (141.64.89.60): icmp_seq=1 ttl=64 time=0.014 ms\n\n--- pool-8P49D14.ris.bht-berlin.de ping statistics ---\n1 packets transmitted, 1 received, 0% packet loss, time 0ms\nrtt min/avg/max/mdev = 0.014/0.014/0.014/0.000 ms', 'stderr': '', 'rc': 0, 'cmd': ['ping', '-c1', '-W1', 'pool-8P49D14.ris.bht-berlin.de'], 'start': '2026-06-30 18:35:29.377814', 'end': '2026-06-30 18:35:29.381416', 'delta': '0:00:00.003602', 'msg': '', 'invocation': {'module_args': {'_raw_params': 'ping -c1 -W1 pool-8P49D14.ris.bht-berlin.de\n', '_uses_shell': False, 'stdin_add_newline': True, 'strip_empty_ends': True, 'argv': None, 'chdir': None, 'executable': None, 'creates': None, 'removes': None, 'stdin': None}}, 'stdout_lines': ['PING pool-8P49D14.ris.bht-berlin.de (141.64.89.60) 56(84) bytes of data.', '64 bytes from pool-8p49d14.ris.bht-berlin.de (141.64.89.60): icmp_seq=1 ttl=64 time=0.014 ms', '', '--- pool-8P49D14.ris.bht-berlin.de ping statistics ---', '1 packets transmitted, 1 received, 0% packet loss, time 0ms', 'rtt min/avg/max/mdev = 0.014/0.014/0.014/0.000 ms'], 'stderr_lines': [], 'ansible_facts': {'discovered_interpreter_python': '/usr/bin/python3'}, 'failed': False, 'item': 'pool-8P49D14', 'ansible_loop_var': 'item'}) => {
    "msg": "pool-8P49D14 -> pool-8P49D14.ris.bht-berlin.de OK\n"
}
ok: [pool-8Q49D14] => (item={'changed': True, 'stdout': 'PING pool-8P49D14.ris.bht-berlin.de (141.64.89.60) 56(84) bytes of data.\n64 bytes from pool-8p49d14.ris.bht-berlin.de (141.64.89.60): icmp_seq=1 ttl=64 time=1.64 ms\n\n--- pool-8P49D14.ris.bht-berlin.de ping statistics ---\n1 packets transmitted, 1 received, 0% packet loss, time 0ms\nrtt min/avg/max/mdev = 1.643/1.643/1.643/0.000 ms', 'stderr': '', 'rc': 0, 'cmd': ['ping', '-c1', '-W1', 'pool-8P49D14.ris.bht-berlin.de'], 'start': '2026-06-30 18:35:29.374828', 'end': '2026-06-30 18:35:29.379734', 'delta': '0:00:00.004906', 'msg': '', 'invocation': {'module_args': {'_raw_params': 'ping -c1 -W1 pool-8P49D14.ris.bht-berlin.de\n', '_uses_shell': False, 'stdin_add_newline': True, 'strip_empty_ends': True, 'argv': None, 'chdir': None, 'executable': None, 'creates': None, 'removes': None, 'stdin': None}}, 'stdout_lines': ['PING pool-8P49D14.ris.bht-berlin.de (141.64.89.60) 56(84) bytes of data.', '64 bytes from pool-8p49d14.ris.bht-berlin.de (141.64.89.60): icmp_seq=1 ttl=64 time=1.64 ms', '', '--- pool-8P49D14.ris.bht-berlin.de ping statistics ---', '1 packets transmitted, 1 received, 0% packet loss, time 0ms', 'rtt min/avg/max/mdev = 1.643/1.643/1.643/0.000 ms'], 'stderr_lines': [], 'ansible_facts': {'discovered_interpreter_python': '/usr/bin/python3'}, 'failed': False, 'item': 'pool-8P49D14', 'ansible_loop_var': 'item'}) => {
    "msg": "pool-8Q49D14 -> pool-8P49D14.ris.bht-berlin.de OK\n"
}
ok: [pool-9N49D14] => (item={'changed': True, 'stdout': 'PING pool-8P49D14.ris.bht-berlin.de (141.64.89.60) 56(84) bytes of data.\n64 bytes from pool-8p49d14.ris.bht-berlin.de (141.64.89.60): icmp_seq=1 ttl=64 time=0.288 ms\n\n--- pool-8P49D14.ris.bht-berlin.de ping statistics ---\n1 packets transmitted, 1 received, 0% packet loss, time 0ms\nrtt min/avg/max/mdev = 0.288/0.288/0.288/0.000 ms', 'stderr': '', 'rc': 0, 'cmd': ['ping', '-c1', '-W1', 'pool-8P49D14.ris.bht-berlin.de'], 'start': '2026-06-30 18:35:29.447326', 'end': '2026-06-30 18:35:29.450801', 'delta': '0:00:00.003475', 'msg': '', 'invocation': {'module_args': {'_raw_params': 'ping -c1 -W1 pool-8P49D14.ris.bht-berlin.de\n', '_uses_shell': False, 'stdin_add_newline': True, 'strip_empty_ends': True, 'argv': None, 'chdir': None, 'executable': None, 'creates': None, 'removes': None, 'stdin': None}}, 'stdout_lines': ['PING pool-8P49D14.ris.bht-berlin.de (141.64.89.60) 56(84) bytes of data.', '64 bytes from pool-8p49d14.ris.bht-berlin.de (141.64.89.60): icmp_seq=1 ttl=64 time=0.288 ms', '', '--- pool-8P49D14.ris.bht-berlin.de ping statistics ---', '1 packets transmitted, 1 received, 0% packet loss, time 0ms', 'rtt min/avg/max/mdev = 0.288/0.288/0.288/0.000 ms'], 'stderr_lines': [], 'ansible_facts': {'discovered_interpreter_python': '/usr/bin/python3'}, 'failed': False, 'item': 'pool-8P49D14', 'ansible_loop_var': 'item'}) => {
    "msg": "pool-9N49D14 -> pool-8P49D14.ris.bht-berlin.de OK\n"
}
ok: [pool-8P49D14] => (item={'changed': True, 'stdout': 'PING pool-8Q49D14.ris.bht-berlin.de (141.64.89.61) 56(84) bytes of data.\n64 bytes from sun61.bht-berlin.de (141.64.89.61): icmp_seq=1 ttl=64 time=0.269 ms\n\n--- pool-8Q49D14.ris.bht-berlin.de ping statistics ---\n1 packets transmitted, 1 received, 0% packet loss, time 0ms\nrtt min/avg/max/mdev = 0.269/0.269/0.269/0.000 ms', 'stderr': '', 'rc': 0, 'cmd': ['ping', '-c1', '-W1', 'pool-8Q49D14.ris.bht-berlin.de'], 'start': '2026-06-30 18:35:29.546888', 'end': '2026-06-30 18:35:29.549949', 'delta': '0:00:00.003061', 'msg': '', 'invocation': {'module_args': {'_raw_params': 'ping -c1 -W1 pool-8Q49D14.ris.bht-berlin.de\n', '_uses_shell': False, 'stdin_add_newline': True, 'strip_empty_ends': True, 'argv': None, 'chdir': None, 'executable': None, 'creates': None, 'removes': None, 'stdin': None}}, 'stdout_lines': ['PING pool-8Q49D14.ris.bht-berlin.de (141.64.89.61) 56(84) bytes of data.', '64 bytes from sun61.bht-berlin.de (141.64.89.61): icmp_seq=1 ttl=64 time=0.269 ms', '', '--- pool-8Q49D14.ris.bht-berlin.de ping statistics ---', '1 packets transmitted, 1 received, 0% packet loss, time 0ms', 'rtt min/avg/max/mdev = 0.269/0.269/0.269/0.000 ms'], 'stderr_lines': [], 'failed': False, 'item': 'pool-8Q49D14', 'ansible_loop_var': 'item'}) => {
    "msg": "pool-8P49D14 -> pool-8Q49D14.ris.bht-berlin.de OK\n"
}
ok: [pool-8Q49D14] => (item={'changed': True, 'stdout': 'PING pool-8Q49D14.ris.bht-berlin.de (141.64.89.61) 56(84) bytes of data.\n64 bytes from sun61.bht-berlin.de (141.64.89.61): icmp_seq=1 ttl=64 time=0.017 ms\n\n--- pool-8Q49D14.ris.bht-berlin.de ping statistics ---\n1 packets transmitted, 1 received, 0% packet loss, time 0ms\nrtt min/avg/max/mdev = 0.017/0.017/0.017/0.000 ms', 'stderr': '', 'rc': 0, 'cmd': ['ping', '-c1', '-W1', 'pool-8Q49D14.ris.bht-berlin.de'], 'start': '2026-06-30 18:35:29.554595', 'end': '2026-06-30 18:35:29.557840', 'delta': '0:00:00.003245', 'msg': '', 'invocation': {'module_args': {'_raw_params': 'ping -c1 -W1 pool-8Q49D14.ris.bht-berlin.de\n', '_uses_shell': False, 'stdin_add_newline': True, 'strip_empty_ends': True, 'argv': None, 'chdir': None, 'executable': None, 'creates': None, 'removes': None, 'stdin': None}}, 'stdout_lines': ['PING pool-8Q49D14.ris.bht-berlin.de (141.64.89.61) 56(84) bytes of data.', '64 bytes from sun61.bht-berlin.de (141.64.89.61): icmp_seq=1 ttl=64 time=0.017 ms', '', '--- pool-8Q49D14.ris.bht-berlin.de ping statistics ---', '1 packets transmitted, 1 received, 0% packet loss, time 0ms', 'rtt min/avg/max/mdev = 0.017/0.017/0.017/0.000 ms'], 'stderr_lines': [], 'failed': False, 'item': 'pool-8Q49D14', 'ansible_loop_var': 'item'}) => {
    "msg": "pool-8Q49D14 -> pool-8Q49D14.ris.bht-berlin.de OK\n"
}
ok: [pool-BN49D14] => (item={'changed': True, 'stdout': 'PING pool-8P49D14.ris.bht-berlin.de (141.64.89.60) 56(84) bytes of data.\n64 bytes from pool-8p49d14.ris.bht-berlin.de (141.64.89.60): icmp_seq=1 ttl=64 time=0.232 ms\n\n--- pool-8P49D14.ris.bht-berlin.de ping statistics ---\n1 packets transmitted, 1 received, 0% packet loss, time 0ms\nrtt min/avg/max/mdev = 0.232/0.232/0.232/0.000 ms', 'stderr': '', 'rc': 0, 'cmd': ['ping', '-c1', '-W1', 'pool-8P49D14.ris.bht-berlin.de'], 'start': '2026-06-30 18:35:29.381921', 'end': '2026-06-30 18:35:29.385112', 'delta': '0:00:00.003191', 'msg': '', 'invocation': {'module_args': {'_raw_params': 'ping -c1 -W1 pool-8P49D14.ris.bht-berlin.de\n', '_uses_shell': False, 'stdin_add_newline': True, 'strip_empty_ends': True, 'argv': None, 'chdir': None, 'executable': None, 'creates': None, 'removes': None, 'stdin': None}}, 'stdout_lines': ['PING pool-8P49D14.ris.bht-berlin.de (141.64.89.60) 56(84) bytes of data.', '64 bytes from pool-8p49d14.ris.bht-berlin.de (141.64.89.60): icmp_seq=1 ttl=64 time=0.232 ms', '', '--- pool-8P49D14.ris.bht-berlin.de ping statistics ---', '1 packets transmitted, 1 received, 0% packet loss, time 0ms', 'rtt min/avg/max/mdev = 0.232/0.232/0.232/0.000 ms'], 'stderr_lines': [], 'ansible_facts': {'discovered_interpreter_python': '/usr/bin/python3'}, 'failed': False, 'item': 'pool-8P49D14', 'ansible_loop_var': 'item'}) => {
    "msg": "pool-BN49D14 -> pool-8P49D14.ris.bht-berlin.de OK\n"
}
ok: [pool-8P49D14] => (item={'changed': True, 'stdout': 'PING pool-9N49D14.ris.bht-berlin.de (141.64.89.62) 56(84) bytes of data.\n64 bytes from sun62.bht-berlin.de (141.64.89.62): icmp_seq=1 ttl=64 time=0.152 ms\n\n--- pool-9N49D14.ris.bht-berlin.de ping statistics ---\n1 packets transmitted, 1 received, 0% packet loss, time 0ms\nrtt min/avg/max/mdev = 0.152/0.152/0.152/0.000 ms', 'stderr': '', 'rc': 0, 'cmd': ['ping', '-c1', '-W1', 'pool-9N49D14.ris.bht-berlin.de'], 'start': '2026-06-30 18:35:29.707809', 'end': '2026-06-30 18:35:29.710944', 'delta': '0:00:00.003135', 'msg': '', 'invocation': {'module_args': {'_raw_params': 'ping -c1 -W1 pool-9N49D14.ris.bht-berlin.de\n', '_uses_shell': False, 'stdin_add_newline': True, 'strip_empty_ends': True, 'argv': None, 'chdir': None, 'executable': None, 'creates': None, 'removes': None, 'stdin': None}}, 'stdout_lines': ['PING pool-9N49D14.ris.bht-berlin.de (141.64.89.62) 56(84) bytes of data.', '64 bytes from sun62.bht-berlin.de (141.64.89.62): icmp_seq=1 ttl=64 time=0.152 ms', '', '--- pool-9N49D14.ris.bht-berlin.de ping statistics ---', '1 packets transmitted, 1 received, 0% packet loss, time 0ms', 'rtt min/avg/max/mdev = 0.152/0.152/0.152/0.000 ms'], 'stderr_lines': [], 'failed': False, 'item': 'pool-9N49D14', 'ansible_loop_var': 'item'}) => {
    "msg": "pool-8P49D14 -> pool-9N49D14.ris.bht-berlin.de OK\n"
}
ok: [pool-9N49D14] => (item={'changed': True, 'stdout': 'PING pool-8Q49D14.ris.bht-berlin.de (141.64.89.61) 56(84) bytes of data.\n64 bytes from sun61.bht-berlin.de (141.64.89.61): icmp_seq=1 ttl=64 time=0.336 ms\n\n--- pool-8Q49D14.ris.bht-berlin.de ping statistics ---\n1 packets transmitted, 1 received, 0% packet loss, time 0ms\nrtt min/avg/max/mdev = 0.336/0.336/0.336/0.000 ms', 'stderr': '', 'rc': 0, 'cmd': ['ping', '-c1', '-W1', 'pool-8Q49D14.ris.bht-berlin.de'], 'start': '2026-06-30 18:35:29.605891', 'end': '2026-06-30 18:35:29.608963', 'delta': '0:00:00.003072', 'msg': '', 'invocation': {'module_args': {'_raw_params': 'ping -c1 -W1 pool-8Q49D14.ris.bht-berlin.de\n', '_uses_shell': False, 'stdin_add_newline': True, 'strip_empty_ends': True, 'argv': None, 'chdir': None, 'executable': None, 'creates': None, 'removes': None, 'stdin': None}}, 'stdout_lines': ['PING pool-8Q49D14.ris.bht-berlin.de (141.64.89.61) 56(84) bytes of data.', '64 bytes from sun61.bht-berlin.de (141.64.89.61): icmp_seq=1 ttl=64 time=0.336 ms', '', '--- pool-8Q49D14.ris.bht-berlin.de ping statistics ---', '1 packets transmitted, 1 received, 0% packet loss, time 0ms', 'rtt min/avg/max/mdev = 0.336/0.336/0.336/0.000 ms'], 'stderr_lines': [], 'failed': False, 'item': 'pool-8Q49D14', 'ansible_loop_var': 'item'}) => {
    "msg": "pool-9N49D14 -> pool-8Q49D14.ris.bht-berlin.de OK\n"
}
ok: [pool-8Q49D14] => (item={'changed': True, 'stdout': 'PING pool-9N49D14.ris.bht-berlin.de (141.64.89.62) 56(84) bytes of data.\n64 bytes from sun62.bht-berlin.de (141.64.89.62): icmp_seq=1 ttl=64 time=0.262 ms\n\n--- pool-9N49D14.ris.bht-berlin.de ping statistics ---\n1 packets transmitted, 1 received, 0% packet loss, time 0ms\nrtt min/avg/max/mdev = 0.262/0.262/0.262/0.000 ms', 'stderr': '', 'rc': 0, 'cmd': ['ping', '-c1', '-W1', 'pool-9N49D14.ris.bht-berlin.de'], 'start': '2026-06-30 18:35:29.717845', 'end': '2026-06-30 18:35:29.720747', 'delta': '0:00:00.002902', 'msg': '', 'invocation': {'module_args': {'_raw_params': 'ping -c1 -W1 pool-9N49D14.ris.bht-berlin.de\n', '_uses_shell': False, 'stdin_add_newline': True, 'strip_empty_ends': True, 'argv': None, 'chdir': None, 'executable': None, 'creates': None, 'removes': None, 'stdin': None}}, 'stdout_lines': ['PING pool-9N49D14.ris.bht-berlin.de (141.64.89.62) 56(84) bytes of data.', '64 bytes from sun62.bht-berlin.de (141.64.89.62): icmp_seq=1 ttl=64 time=0.262 ms', '', '--- pool-9N49D14.ris.bht-berlin.de ping statistics ---', '1 packets transmitted, 1 received, 0% packet loss, time 0ms', 'rtt min/avg/max/mdev = 0.262/0.262/0.262/0.000 ms'], 'stderr_lines': [], 'failed': False, 'item': 'pool-9N49D14', 'ansible_loop_var': 'item'}) => {
    "msg": "pool-8Q49D14 -> pool-9N49D14.ris.bht-berlin.de OK\n"
}
ok: [pool-BP49D14] => (item={'changed': True, 'stdout': 'PING pool-8P49D14.ris.bht-berlin.de (141.64.89.60) 56(84) bytes of data.\n64 bytes from pool-8p49d14.ris.bht-berlin.de (141.64.89.60): icmp_seq=1 ttl=64 time=0.390 ms\n\n--- pool-8P49D14.ris.bht-berlin.de ping statistics ---\n1 packets transmitted, 1 received, 0% packet loss, time 0ms\nrtt min/avg/max/mdev = 0.390/0.390/0.390/0.000 ms', 'stderr': '', 'rc': 0, 'cmd': ['ping', '-c1', '-W1', 'pool-8P49D14.ris.bht-berlin.de'], 'start': '2026-06-30 18:35:29.380705', 'end': '2026-06-30 18:35:29.384429', 'delta': '0:00:00.003724', 'msg': '', 'invocation': {'module_args': {'_raw_params': 'ping -c1 -W1 pool-8P49D14.ris.bht-berlin.de\n', '_uses_shell': False, 'stdin_add_newline': True, 'strip_empty_ends': True, 'argv': None, 'chdir': None, 'executable': None, 'creates': None, 'removes': None, 'stdin': None}}, 'stdout_lines': ['PING pool-8P49D14.ris.bht-berlin.de (141.64.89.60) 56(84) bytes of data.', '64 bytes from pool-8p49d14.ris.bht-berlin.de (141.64.89.60): icmp_seq=1 ttl=64 time=0.390 ms', '', '--- pool-8P49D14.ris.bht-berlin.de ping statistics ---', '1 packets transmitted, 1 received, 0% packet loss, time 0ms', 'rtt min/avg/max/mdev = 0.390/0.390/0.390/0.000 ms'], 'stderr_lines': [], 'ansible_facts': {'discovered_interpreter_python': '/usr/bin/python3'}, 'failed': False, 'item': 'pool-8P49D14', 'ansible_loop_var': 'item'}) => {
    "msg": "pool-BP49D14 -> pool-8P49D14.ris.bht-berlin.de OK\n"
}
ok: [pool-BN49D14] => (item={'changed': True, 'stdout': 'PING pool-8Q49D14.ris.bht-berlin.de (141.64.89.61) 56(84) bytes of data.\n64 bytes from sun61.bht-berlin.de (141.64.89.61): icmp_seq=1 ttl=64 time=0.273 ms\n\n--- pool-8Q49D14.ris.bht-berlin.de ping statistics ---\n1 packets transmitted, 1 received, 0% packet loss, time 0ms\nrtt min/avg/max/mdev = 0.273/0.273/0.273/0.000 ms', 'stderr': '', 'rc': 0, 'cmd': ['ping', '-c1', '-W1', 'pool-8Q49D14.ris.bht-berlin.de'], 'start': '2026-06-30 18:35:29.555061', 'end': '2026-06-30 18:35:29.558017', 'delta': '0:00:00.002956', 'msg': '', 'invocation': {'module_args': {'_raw_params': 'ping -c1 -W1 pool-8Q49D14.ris.bht-berlin.de\n', '_uses_shell': False, 'stdin_add_newline': True, 'strip_empty_ends': True, 'argv': None, 'chdir': None, 'executable': None, 'creates': None, 'removes': None, 'stdin': None}}, 'stdout_lines': ['PING pool-8Q49D14.ris.bht-berlin.de (141.64.89.61) 56(84) bytes of data.', '64 bytes from sun61.bht-berlin.de (141.64.89.61): icmp_seq=1 ttl=64 time=0.273 ms', '', '--- pool-8Q49D14.ris.bht-berlin.de ping statistics ---', '1 packets transmitted, 1 received, 0% packet loss, time 0ms', 'rtt min/avg/max/mdev = 0.273/0.273/0.273/0.000 ms'], 'stderr_lines': [], 'failed': False, 'item': 'pool-8Q49D14', 'ansible_loop_var': 'item'}) => {
    "msg": "pool-BN49D14 -> pool-8Q49D14.ris.bht-berlin.de OK\n"
}
ok: [pool-8P49D14] => (item={'changed': True, 'stdout': 'PING pool-BN49D14.ris.bht-berlin.de (141.64.89.65) 56(84) bytes of data.\n64 bytes from pool-bn49d14.ris.bht-berlin.de (141.64.89.65): icmp_seq=1 ttl=64 time=0.226 ms\n\n--- pool-BN49D14.ris.bht-berlin.de ping statistics ---\n1 packets transmitted, 1 received, 0% packet loss, time 0ms\nrtt min/avg/max/mdev = 0.226/0.226/0.226/0.000 ms', 'stderr': '', 'rc': 0, 'cmd': ['ping', '-c1', '-W1', 'pool-BN49D14.ris.bht-berlin.de'], 'start': '2026-06-30 18:35:29.901082', 'end': '2026-06-30 18:35:29.904423', 'delta': '0:00:00.003341', 'msg': '', 'invocation': {'module_args': {'_raw_params': 'ping -c1 -W1 pool-BN49D14.ris.bht-berlin.de\n', '_uses_shell': False, 'stdin_add_newline': True, 'strip_empty_ends': True, 'argv': None, 'chdir': None, 'executable': None, 'creates': None, 'removes': None, 'stdin': None}}, 'stdout_lines': ['PING pool-BN49D14.ris.bht-berlin.de (141.64.89.65) 56(84) bytes of data.', '64 bytes from pool-bn49d14.ris.bht-berlin.de (141.64.89.65): icmp_seq=1 ttl=64 time=0.226 ms', '', '--- pool-BN49D14.ris.bht-berlin.de ping statistics ---', '1 packets transmitted, 1 received, 0% packet loss, time 0ms', 'rtt min/avg/max/mdev = 0.226/0.226/0.226/0.000 ms'], 'stderr_lines': [], 'failed': False, 'item': 'pool-BN49D14', 'ansible_loop_var': 'item'}) => {
    "msg": "pool-8P49D14 -> pool-BN49D14.ris.bht-berlin.de OK\n"
}
ok: [pool-9N49D14] => (item={'changed': True, 'stdout': 'PING pool-9N49D14.ris.bht-berlin.de (141.64.89.62) 56(84) bytes of data.\n64 bytes from sun62.bht-berlin.de (141.64.89.62): icmp_seq=1 ttl=64 time=0.018 ms\n\n--- pool-9N49D14.ris.bht-berlin.de ping statistics ---\n1 packets transmitted, 1 received, 0% packet loss, time 0ms\nrtt min/avg/max/mdev = 0.018/0.018/0.018/0.000 ms', 'stderr': '', 'rc': 0, 'cmd': ['ping', '-c1', '-W1', 'pool-9N49D14.ris.bht-berlin.de'], 'start': '2026-06-30 18:35:29.764625', 'end': '2026-06-30 18:35:29.767701', 'delta': '0:00:00.003076', 'msg': '', 'invocation': {'module_args': {'_raw_params': 'ping -c1 -W1 pool-9N49D14.ris.bht-berlin.de\n', '_uses_shell': False, 'stdin_add_newline': True, 'strip_empty_ends': True, 'argv': None, 'chdir': None, 'executable': None, 'creates': None, 'removes': None, 'stdin': None}}, 'stdout_lines': ['PING pool-9N49D14.ris.bht-berlin.de (141.64.89.62) 56(84) bytes of data.', '64 bytes from sun62.bht-berlin.de (141.64.89.62): icmp_seq=1 ttl=64 time=0.018 ms', '', '--- pool-9N49D14.ris.bht-berlin.de ping statistics ---', '1 packets transmitted, 1 received, 0% packet loss, time 0ms', 'rtt min/avg/max/mdev = 0.018/0.018/0.018/0.000 ms'], 'stderr_lines': [], 'failed': False, 'item': 'pool-9N49D14', 'ansible_loop_var': 'item'}) => {
    "msg": "pool-9N49D14 -> pool-9N49D14.ris.bht-berlin.de OK\n"
}
ok: [pool-8Q49D14] => (item={'changed': True, 'stdout': 'PING pool-BN49D14.ris.bht-berlin.de (141.64.89.65) 56(84) bytes of data.\n64 bytes from pool-bn49d14.ris.bht-berlin.de (141.64.89.65): icmp_seq=1 ttl=64 time=0.237 ms\n\n--- pool-BN49D14.ris.bht-berlin.de ping statistics ---\n1 packets transmitted, 1 received, 0% packet loss, time 0ms\nrtt min/avg/max/mdev = 0.237/0.237/0.237/0.000 ms', 'stderr': '', 'rc': 0, 'cmd': ['ping', '-c1', '-W1', 'pool-BN49D14.ris.bht-berlin.de'], 'start': '2026-06-30 18:35:29.895058', 'end': '2026-06-30 18:35:29.898113', 'delta': '0:00:00.003055', 'msg': '', 'invocation': {'module_args': {'_raw_params': 'ping -c1 -W1 pool-BN49D14.ris.bht-berlin.de\n', '_uses_shell': False, 'stdin_add_newline': True, 'strip_empty_ends': True, 'argv': None, 'chdir': None, 'executable': None, 'creates': None, 'removes': None, 'stdin': None}}, 'stdout_lines': ['PING pool-BN49D14.ris.bht-berlin.de (141.64.89.65) 56(84) bytes of data.', '64 bytes from pool-bn49d14.ris.bht-berlin.de (141.64.89.65): icmp_seq=1 ttl=64 time=0.237 ms', '', '--- pool-BN49D14.ris.bht-berlin.de ping statistics ---', '1 packets transmitted, 1 received, 0% packet loss, time 0ms', 'rtt min/avg/max/mdev = 0.237/0.237/0.237/0.000 ms'], 'stderr_lines': [], 'failed': False, 'item': 'pool-BN49D14', 'ansible_loop_var': 'item'}) => {
    "msg": "pool-8Q49D14 -> pool-BN49D14.ris.bht-berlin.de OK\n"
}
ok: [pool-9N49D14] => (item={'changed': True, 'stdout': 'PING pool-BN49D14.ris.bht-berlin.de (141.64.89.65) 56(84) bytes of data.\n64 bytes from pool-bn49d14.ris.bht-berlin.de (141.64.89.65): icmp_seq=1 ttl=64 time=0.442 ms\n\n--- pool-BN49D14.ris.bht-berlin.de ping statistics ---\n1 packets transmitted, 1 received, 0% packet loss, time 0ms\nrtt min/avg/max/mdev = 0.442/0.442/0.442/0.000 ms', 'stderr': '', 'rc': 0, 'cmd': ['ping', '-c1', '-W1', 'pool-BN49D14.ris.bht-berlin.de'], 'start': '2026-06-30 18:35:29.911765', 'end': '2026-06-30 18:35:29.915074', 'delta': '0:00:00.003309', 'msg': '', 'invocation': {'module_args': {'_raw_params': 'ping -c1 -W1 pool-BN49D14.ris.bht-berlin.de\n', '_uses_shell': False, 'stdin_add_newline': True, 'strip_empty_ends': True, 'argv': None, 'chdir': None, 'executable': None, 'creates': None, 'removes': None, 'stdin': None}}, 'stdout_lines': ['PING pool-BN49D14.ris.bht-berlin.de (141.64.89.65) 56(84) bytes of data.', '64 bytes from pool-bn49d14.ris.bht-berlin.de (141.64.89.65): icmp_seq=1 ttl=64 time=0.442 ms', '', '--- pool-BN49D14.ris.bht-berlin.de ping statistics ---', '1 packets transmitted, 1 received, 0% packet loss, time 0ms', 'rtt min/avg/max/mdev = 0.442/0.442/0.442/0.000 ms'], 'stderr_lines': [], 'failed': False, 'item': 'pool-BN49D14', 'ansible_loop_var': 'item'}) => {
    "msg": "pool-9N49D14 -> pool-BN49D14.ris.bht-berlin.de OK\n"
}
ok: [pool-8Q49D14] => (item={'changed': True, 'stdout': 'PING pool-BP49D14.ris.bht-berlin.de (141.64.89.66) 56(84) bytes of data.\n64 bytes from sun66.beuth-hochschule.de (141.64.89.66): icmp_seq=1 ttl=64 time=0.465 ms\n\n--- pool-BP49D14.ris.bht-berlin.de ping statistics ---\n1 packets transmitted, 1 received, 0% packet loss, time 0ms\nrtt min/avg/max/mdev = 0.465/0.465/0.465/0.000 ms', 'stderr': '', 'rc': 0, 'cmd': ['ping', '-c1', '-W1', 'pool-BP49D14.ris.bht-berlin.de'], 'start': '2026-06-30 18:35:30.102183', 'end': '2026-06-30 18:35:30.105488', 'delta': '0:00:00.003305', 'msg': '', 'invocation': {'module_args': {'_raw_params': 'ping -c1 -W1 pool-BP49D14.ris.bht-berlin.de\n', '_uses_shell': False, 'stdin_add_newline': True, 'strip_empty_ends': True, 'argv': None, 'chdir': None, 'executable': None, 'creates': None, 'removes': None, 'stdin': None}}, 'stdout_lines': ['PING pool-BP49D14.ris.bht-berlin.de (141.64.89.66) 56(84) bytes of data.', '64 bytes from sun66.beuth-hochschule.de (141.64.89.66): icmp_seq=1 ttl=64 time=0.465 ms', '', '--- pool-BP49D14.ris.bht-berlin.de ping statistics ---', '1 packets transmitted, 1 received, 0% packet loss, time 0ms', 'rtt min/avg/max/mdev = 0.465/0.465/0.465/0.000 ms'], 'stderr_lines': [], 'failed': False, 'item': 'pool-BP49D14', 'ansible_loop_var': 'item'}) => {
    "msg": "pool-8Q49D14 -> pool-BP49D14.ris.bht-berlin.de OK\n"
}
ok: [pool-8P49D14] => (item={'changed': True, 'stdout': 'PING pool-BP49D14.ris.bht-berlin.de (141.64.89.66) 56(84) bytes of data.\n64 bytes from sun66.beuth-hochschule.de (141.64.89.66): icmp_seq=1 ttl=64 time=0.338 ms\n\n--- pool-BP49D14.ris.bht-berlin.de ping statistics ---\n1 packets transmitted, 1 received, 0% packet loss, time 0ms\nrtt min/avg/max/mdev = 0.338/0.338/0.338/0.000 ms', 'stderr': '', 'rc': 0, 'cmd': ['ping', '-c1', '-W1', 'pool-BP49D14.ris.bht-berlin.de'], 'start': '2026-06-30 18:35:30.096106', 'end': '2026-06-30 18:35:30.099086', 'delta': '0:00:00.002980', 'msg': '', 'invocation': {'module_args': {'_raw_params': 'ping -c1 -W1 pool-BP49D14.ris.bht-berlin.de\n', '_uses_shell': False, 'stdin_add_newline': True, 'strip_empty_ends': True, 'argv': None, 'chdir': None, 'executable': None, 'creates': None, 'removes': None, 'stdin': None}}, 'stdout_lines': ['PING pool-BP49D14.ris.bht-berlin.de (141.64.89.66) 56(84) bytes of data.', '64 bytes from sun66.beuth-hochschule.de (141.64.89.66): icmp_seq=1 ttl=64 time=0.338 ms', '', '--- pool-BP49D14.ris.bht-berlin.de ping statistics ---', '1 packets transmitted, 1 received, 0% packet loss, time 0ms', 'rtt min/avg/max/mdev = 0.338/0.338/0.338/0.000 ms'], 'stderr_lines': [], 'failed': False, 'item': 'pool-BP49D14', 'ansible_loop_var': 'item'}) => {
    "msg": "pool-8P49D14 -> pool-BP49D14.ris.bht-berlin.de OK\n"
}
ok: [pool-BP49D14] => (item={'changed': True, 'stdout': 'PING pool-8Q49D14.ris.bht-berlin.de (141.64.89.61) 56(84) bytes of data.\n64 bytes from sun61.bht-berlin.de (141.64.89.61): icmp_seq=1 ttl=64 time=0.305 ms\n\n--- pool-8Q49D14.ris.bht-berlin.de ping statistics ---\n1 packets transmitted, 1 received, 0% packet loss, time 0ms\nrtt min/avg/max/mdev = 0.305/0.305/0.305/0.000 ms', 'stderr': '', 'rc': 0, 'cmd': ['ping', '-c1', '-W1', 'pool-8Q49D14.ris.bht-berlin.de'], 'start': '2026-06-30 18:35:29.555518', 'end': '2026-06-30 18:35:29.558738', 'delta': '0:00:00.003220', 'msg': '', 'invocation': {'module_args': {'_raw_params': 'ping -c1 -W1 pool-8Q49D14.ris.bht-berlin.de\n', '_uses_shell': False, 'stdin_add_newline': True, 'strip_empty_ends': True, 'argv': None, 'chdir': None, 'executable': None, 'creates': None, 'removes': None, 'stdin': None}}, 'stdout_lines': ['PING pool-8Q49D14.ris.bht-berlin.de (141.64.89.61) 56(84) bytes of data.', '64 bytes from sun61.bht-berlin.de (141.64.89.61): icmp_seq=1 ttl=64 time=0.305 ms', '', '--- pool-8Q49D14.ris.bht-berlin.de ping statistics ---', '1 packets transmitted, 1 received, 0% packet loss, time 0ms', 'rtt min/avg/max/mdev = 0.305/0.305/0.305/0.000 ms'], 'stderr_lines': [], 'failed': False, 'item': 'pool-8Q49D14', 'ansible_loop_var': 'item'}) => {
    "msg": "pool-BP49D14 -> pool-8Q49D14.ris.bht-berlin.de OK\n"
}
ok: [pool-BN49D14] => (item={'changed': True, 'stdout': 'PING pool-9N49D14.ris.bht-berlin.de (141.64.89.62) 56(84) bytes of data.\n64 bytes from sun62.bht-berlin.de (141.64.89.62): icmp_seq=1 ttl=64 time=0.220 ms\n\n--- pool-9N49D14.ris.bht-berlin.de ping statistics ---\n1 packets transmitted, 1 received, 0% packet loss, time 0ms\nrtt min/avg/max/mdev = 0.220/0.220/0.220/0.000 ms', 'stderr': '', 'rc': 0, 'cmd': ['ping', '-c1', '-W1', 'pool-9N49D14.ris.bht-berlin.de'], 'start': '2026-06-30 18:35:29.711386', 'end': '2026-06-30 18:35:29.713985', 'delta': '0:00:00.002599', 'msg': '', 'invocation': {'module_args': {'_raw_params': 'ping -c1 -W1 pool-9N49D14.ris.bht-berlin.de\n', '_uses_shell': False, 'stdin_add_newline': True, 'strip_empty_ends': True, 'argv': None, 'chdir': None, 'executable': None, 'creates': None, 'removes': None, 'stdin': None}}, 'stdout_lines': ['PING pool-9N49D14.ris.bht-berlin.de (141.64.89.62) 56(84) bytes of data.', '64 bytes from sun62.bht-berlin.de (141.64.89.62): icmp_seq=1 ttl=64 time=0.220 ms', '', '--- pool-9N49D14.ris.bht-berlin.de ping statistics ---', '1 packets transmitted, 1 received, 0% packet loss, time 0ms', 'rtt min/avg/max/mdev = 0.220/0.220/0.220/0.000 ms'], 'stderr_lines': [], 'failed': False, 'item': 'pool-9N49D14', 'ansible_loop_var': 'item'}) => {
    "msg": "pool-BN49D14 -> pool-9N49D14.ris.bht-berlin.de OK\n"
}
ok: [pool-9N49D14] => (item={'changed': True, 'stdout': 'PING pool-BP49D14.ris.bht-berlin.de (141.64.89.66) 56(84) bytes of data.\n64 bytes from sun66.beuth-hochschule.de (141.64.89.66): icmp_seq=1 ttl=64 time=0.443 ms\n\n--- pool-BP49D14.ris.bht-berlin.de ping statistics ---\n1 packets transmitted, 1 received, 0% packet loss, time 0ms\nrtt min/avg/max/mdev = 0.443/0.443/0.443/0.000 ms', 'stderr': '', 'rc': 0, 'cmd': ['ping', '-c1', '-W1', 'pool-BP49D14.ris.bht-berlin.de'], 'start': '2026-06-30 18:35:30.103570', 'end': '2026-06-30 18:35:30.106794', 'delta': '0:00:00.003224', 'msg': '', 'invocation': {'module_args': {'_raw_params': 'ping -c1 -W1 pool-BP49D14.ris.bht-berlin.de\n', '_uses_shell': False, 'stdin_add_newline': True, 'strip_empty_ends': True, 'argv': None, 'chdir': None, 'executable': None, 'creates': None, 'removes': None, 'stdin': None}}, 'stdout_lines': ['PING pool-BP49D14.ris.bht-berlin.de (141.64.89.66) 56(84) bytes of data.', '64 bytes from sun66.beuth-hochschule.de (141.64.89.66): icmp_seq=1 ttl=64 time=0.443 ms', '', '--- pool-BP49D14.ris.bht-berlin.de ping statistics ---', '1 packets transmitted, 1 received, 0% packet loss, time 0ms', 'rtt min/avg/max/mdev = 0.443/0.443/0.443/0.000 ms'], 'stderr_lines': [], 'failed': False, 'item': 'pool-BP49D14', 'ansible_loop_var': 'item'}) => {
    "msg": "pool-9N49D14 -> pool-BP49D14.ris.bht-berlin.de OK\n"
}
ok: [pool-8Q49D14] => (item={'changed': True, 'stdout': 'PING pool-HN49D14.ris.bht-berlin.de (141.64.89.79) 56(84) bytes of data.\n64 bytes from sun79.bht-berlin.de (141.64.89.79): icmp_seq=1 ttl=64 time=0.649 ms\n\n--- pool-HN49D14.ris.bht-berlin.de ping statistics ---\n1 packets transmitted, 1 received, 0% packet loss, time 0ms\nrtt min/avg/max/mdev = 0.649/0.649/0.649/0.000 ms', 'stderr': '', 'rc': 0, 'cmd': ['ping', '-c1', '-W1', 'pool-HN49D14.ris.bht-berlin.de'], 'start': '2026-06-30 18:35:30.316264', 'end': '2026-06-30 18:35:30.319825', 'delta': '0:00:00.003561', 'msg': '', 'invocation': {'module_args': {'_raw_params': 'ping -c1 -W1 pool-HN49D14.ris.bht-berlin.de\n', '_uses_shell': False, 'stdin_add_newline': True, 'strip_empty_ends': True, 'argv': None, 'chdir': None, 'executable': None, 'creates': None, 'removes': None, 'stdin': None}}, 'stdout_lines': ['PING pool-HN49D14.ris.bht-berlin.de (141.64.89.79) 56(84) bytes of data.', '64 bytes from sun79.bht-berlin.de (141.64.89.79): icmp_seq=1 ttl=64 time=0.649 ms', '', '--- pool-HN49D14.ris.bht-berlin.de ping statistics ---', '1 packets transmitted, 1 received, 0% packet loss, time 0ms', 'rtt min/avg/max/mdev = 0.649/0.649/0.649/0.000 ms'], 'stderr_lines': [], 'failed': False, 'item': 'pool-HN49D14', 'ansible_loop_var': 'item'}) => {
    "msg": "pool-8Q49D14 -> pool-HN49D14.ris.bht-berlin.de OK\n"
}
ok: [pool-BP49D14] => (item={'changed': True, 'stdout': 'PING pool-9N49D14.ris.bht-berlin.de (141.64.89.62) 56(84) bytes of data.\n64 bytes from sun62.bht-berlin.de (141.64.89.62): icmp_seq=1 ttl=64 time=0.137 ms\n\n--- pool-9N49D14.ris.bht-berlin.de ping statistics ---\n1 packets transmitted, 1 received, 0% packet loss, time 0ms\nrtt min/avg/max/mdev = 0.137/0.137/0.137/0.000 ms', 'stderr': '', 'rc': 0, 'cmd': ['ping', '-c1', '-W1', 'pool-9N49D14.ris.bht-berlin.de'], 'start': '2026-06-30 18:35:29.711108', 'end': '2026-06-30 18:35:29.713480', 'delta': '0:00:00.002372', 'msg': '', 'invocation': {'module_args': {'_raw_params': 'ping -c1 -W1 pool-9N49D14.ris.bht-berlin.de\n', '_uses_shell': False, 'stdin_add_newline': True, 'strip_empty_ends': True, 'argv': None, 'chdir': None, 'executable': None, 'creates': None, 'removes': None, 'stdin': None}}, 'stdout_lines': ['PING pool-9N49D14.ris.bht-berlin.de (141.64.89.62) 56(84) bytes of data.', '64 bytes from sun62.bht-berlin.de (141.64.89.62): icmp_seq=1 ttl=64 time=0.137 ms', '', '--- pool-9N49D14.ris.bht-berlin.de ping statistics ---', '1 packets transmitted, 1 received, 0% packet loss, time 0ms', 'rtt min/avg/max/mdev = 0.137/0.137/0.137/0.000 ms'], 'stderr_lines': [], 'failed': False, 'item': 'pool-9N49D14', 'ansible_loop_var': 'item'}) => {
    "msg": "pool-BP49D14 -> pool-9N49D14.ris.bht-berlin.de OK\n"
}
ok: [pool-8P49D14] => (item={'changed': True, 'stdout': 'PING pool-HN49D14.ris.bht-berlin.de (141.64.89.79) 56(84) bytes of data.\n64 bytes from sun79.bht-berlin.de (141.64.89.79): icmp_seq=1 ttl=64 time=0.697 ms\n\n--- pool-HN49D14.ris.bht-berlin.de ping statistics ---\n1 packets transmitted, 1 received, 0% packet loss, time 0ms\nrtt min/avg/max/mdev = 0.697/0.697/0.697/0.000 ms', 'stderr': '', 'rc': 0, 'cmd': ['ping', '-c1', '-W1', 'pool-HN49D14.ris.bht-berlin.de'], 'start': '2026-06-30 18:35:30.308056', 'end': '2026-06-30 18:35:30.312173', 'delta': '0:00:00.004117', 'msg': '', 'invocation': {'module_args': {'_raw_params': 'ping -c1 -W1 pool-HN49D14.ris.bht-berlin.de\n', '_uses_shell': False, 'stdin_add_newline': True, 'strip_empty_ends': True, 'argv': None, 'chdir': None, 'executable': None, 'creates': None, 'removes': None, 'stdin': None}}, 'stdout_lines': ['PING pool-HN49D14.ris.bht-berlin.de (141.64.89.79) 56(84) bytes of data.', '64 bytes from sun79.bht-berlin.de (141.64.89.79): icmp_seq=1 ttl=64 time=0.697 ms', '', '--- pool-HN49D14.ris.bht-berlin.de ping statistics ---', '1 packets transmitted, 1 received, 0% packet loss, time 0ms', 'rtt min/avg/max/mdev = 0.697/0.697/0.697/0.000 ms'], 'stderr_lines': [], 'failed': False, 'item': 'pool-HN49D14', 'ansible_loop_var': 'item'}) => {
    "msg": "pool-8P49D14 -> pool-HN49D14.ris.bht-berlin.de OK\n"
}
ok: [pool-8Q49D14] => (item={'changed': True, 'stdout': 'PING pool-HP49D14.ris.bht-berlin.de (141.64.89.80) 56(84) bytes of data.\n64 bytes from sun80.beuth-hochschule.de (141.64.89.80): icmp_seq=1 ttl=64 time=0.319 ms\n\n--- pool-HP49D14.ris.bht-berlin.de ping statistics ---\n1 packets transmitted, 1 received, 0% packet loss, time 0ms\nrtt min/avg/max/mdev = 0.319/0.319/0.319/0.000 ms', 'stderr': '', 'rc': 0, 'cmd': ['ping', '-c1', '-W1', 'pool-HP49D14.ris.bht-berlin.de'], 'start': '2026-06-30 18:35:30.539526', 'end': '2026-06-30 18:35:30.542821', 'delta': '0:00:00.003295', 'msg': '', 'invocation': {'module_args': {'_raw_params': 'ping -c1 -W1 pool-HP49D14.ris.bht-berlin.de\n', '_uses_shell': False, 'stdin_add_newline': True, 'strip_empty_ends': True, 'argv': None, 'chdir': None, 'executable': None, 'creates': None, 'removes': None, 'stdin': None}}, 'stdout_lines': ['PING pool-HP49D14.ris.bht-berlin.de (141.64.89.80) 56(84) bytes of data.', '64 bytes from sun80.beuth-hochschule.de (141.64.89.80): icmp_seq=1 ttl=64 time=0.319 ms', '', '--- pool-HP49D14.ris.bht-berlin.de ping statistics ---', '1 packets transmitted, 1 received, 0% packet loss, time 0ms', 'rtt min/avg/max/mdev = 0.319/0.319/0.319/0.000 ms'], 'stderr_lines': [], 'failed': False, 'item': 'pool-HP49D14', 'ansible_loop_var': 'item'}) => {
    "msg": "pool-8Q49D14 -> pool-HP49D14.ris.bht-berlin.de OK\n"
}
ok: [pool-BN49D14] => (item={'changed': True, 'stdout': 'PING pool-BN49D14.ris.bht-berlin.de (141.64.89.65) 56(84) bytes of data.\n64 bytes from pool-bn49d14.ris.bht-berlin.de (141.64.89.65): icmp_seq=1 ttl=64 time=0.017 ms\n\n--- pool-BN49D14.ris.bht-berlin.de ping statistics ---\n1 packets transmitted, 1 received, 0% packet loss, time 0ms\nrtt min/avg/max/mdev = 0.017/0.017/0.017/0.000 ms', 'stderr': '', 'rc': 0, 'cmd': ['ping', '-c1', '-W1', 'pool-BN49D14.ris.bht-berlin.de'], 'start': '2026-06-30 18:35:29.893984', 'end': '2026-06-30 18:35:29.897289', 'delta': '0:00:00.003305', 'msg': '', 'invocation': {'module_args': {'_raw_params': 'ping -c1 -W1 pool-BN49D14.ris.bht-berlin.de\n', '_uses_shell': False, 'stdin_add_newline': True, 'strip_empty_ends': True, 'argv': None, 'chdir': None, 'executable': None, 'creates': None, 'removes': None, 'stdin': None}}, 'stdout_lines': ['PING pool-BN49D14.ris.bht-berlin.de (141.64.89.65) 56(84) bytes of data.', '64 bytes from pool-bn49d14.ris.bht-berlin.de (141.64.89.65): icmp_seq=1 ttl=64 time=0.017 ms', '', '--- pool-BN49D14.ris.bht-berlin.de ping statistics ---', '1 packets transmitted, 1 received, 0% packet loss, time 0ms', 'rtt min/avg/max/mdev = 0.017/0.017/0.017/0.000 ms'], 'stderr_lines': [], 'failed': False, 'item': 'pool-BN49D14', 'ansible_loop_var': 'item'}) => {
    "msg": "pool-BN49D14 -> pool-BN49D14.ris.bht-berlin.de OK\n"
}
ok: [pool-9N49D14] => (item={'changed': True, 'stdout': 'PING pool-HN49D14.ris.bht-berlin.de (141.64.89.79) 56(84) bytes of data.\n64 bytes from sun79.bht-berlin.de (141.64.89.79): icmp_seq=1 ttl=64 time=0.680 ms\n\n--- pool-HN49D14.ris.bht-berlin.de ping statistics ---\n1 packets transmitted, 1 received, 0% packet loss, time 0ms\nrtt min/avg/max/mdev = 0.680/0.680/0.680/0.000 ms', 'stderr': '', 'rc': 0, 'cmd': ['ping', '-c1', '-W1', 'pool-HN49D14.ris.bht-berlin.de'], 'start': '2026-06-30 18:35:30.328824', 'end': '2026-06-30 18:35:30.332488', 'delta': '0:00:00.003664', 'msg': '', 'invocation': {'module_args': {'_raw_params': 'ping -c1 -W1 pool-HN49D14.ris.bht-berlin.de\n', '_uses_shell': False, 'stdin_add_newline': True, 'strip_empty_ends': True, 'argv': None, 'chdir': None, 'executable': None, 'creates': None, 'removes': None, 'stdin': None}}, 'stdout_lines': ['PING pool-HN49D14.ris.bht-berlin.de (141.64.89.79) 56(84) bytes of data.', '64 bytes from sun79.bht-berlin.de (141.64.89.79): icmp_seq=1 ttl=64 time=0.680 ms', '', '--- pool-HN49D14.ris.bht-berlin.de ping statistics ---', '1 packets transmitted, 1 received, 0% packet loss, time 0ms', 'rtt min/avg/max/mdev = 0.680/0.680/0.680/0.000 ms'], 'stderr_lines': [], 'failed': False, 'item': 'pool-HN49D14', 'ansible_loop_var': 'item'}) => {
    "msg": "pool-9N49D14 -> pool-HN49D14.ris.bht-berlin.de OK\n"
}
ok: [pool-BP49D14] => (item={'changed': True, 'stdout': 'PING pool-BN49D14.ris.bht-berlin.de (141.64.89.65) 56(84) bytes of data.\n64 bytes from pool-bn49d14.ris.bht-berlin.de (141.64.89.65): icmp_seq=1 ttl=64 time=0.237 ms\n\n--- pool-BN49D14.ris.bht-berlin.de ping statistics ---\n1 packets transmitted, 1 received, 0% packet loss, time 0ms\nrtt min/avg/max/mdev = 0.237/0.237/0.237/0.000 ms', 'stderr': '', 'rc': 0, 'cmd': ['ping', '-c1', '-W1', 'pool-BN49D14.ris.bht-berlin.de'], 'start': '2026-06-30 18:35:29.897514', 'end': '2026-06-30 18:35:29.901051', 'delta': '0:00:00.003537', 'msg': '', 'invocation': {'module_args': {'_raw_params': 'ping -c1 -W1 pool-BN49D14.ris.bht-berlin.de\n', '_uses_shell': False, 'stdin_add_newline': True, 'strip_empty_ends': True, 'argv': None, 'chdir': None, 'executable': None, 'creates': None, 'removes': None, 'stdin': None}}, 'stdout_lines': ['PING pool-BN49D14.ris.bht-berlin.de (141.64.89.65) 56(84) bytes of data.', '64 bytes from pool-bn49d14.ris.bht-berlin.de (141.64.89.65): icmp_seq=1 ttl=64 time=0.237 ms', '', '--- pool-BN49D14.ris.bht-berlin.de ping statistics ---', '1 packets transmitted, 1 received, 0% packet loss, time 0ms', 'rtt min/avg/max/mdev = 0.237/0.237/0.237/0.000 ms'], 'stderr_lines': [], 'failed': False, 'item': 'pool-BN49D14', 'ansible_loop_var': 'item'}) => {
    "msg": "pool-BP49D14 -> pool-BN49D14.ris.bht-berlin.de OK\n"
}
ok: [pool-8P49D14] => (item={'changed': True, 'stdout': 'PING pool-HP49D14.ris.bht-berlin.de (141.64.89.80) 56(84) bytes of data.\n64 bytes from sun80.beuth-hochschule.de (141.64.89.80): icmp_seq=1 ttl=64 time=0.287 ms\n\n--- pool-HP49D14.ris.bht-berlin.de ping statistics ---\n1 packets transmitted, 1 received, 0% packet loss, time 0ms\nrtt min/avg/max/mdev = 0.287/0.287/0.287/0.000 ms', 'stderr': '', 'rc': 0, 'cmd': ['ping', '-c1', '-W1', 'pool-HP49D14.ris.bht-berlin.de'], 'start': '2026-06-30 18:35:30.541942', 'end': '2026-06-30 18:35:30.545283', 'delta': '0:00:00.003341', 'msg': '', 'invocation': {'module_args': {'_raw_params': 'ping -c1 -W1 pool-HP49D14.ris.bht-berlin.de\n', '_uses_shell': False, 'stdin_add_newline': True, 'strip_empty_ends': True, 'argv': None, 'chdir': None, 'executable': None, 'creates': None, 'removes': None, 'stdin': None}}, 'stdout_lines': ['PING pool-HP49D14.ris.bht-berlin.de (141.64.89.80) 56(84) bytes of data.', '64 bytes from sun80.beuth-hochschule.de (141.64.89.80): icmp_seq=1 ttl=64 time=0.287 ms', '', '--- pool-HP49D14.ris.bht-berlin.de ping statistics ---', '1 packets transmitted, 1 received, 0% packet loss, time 0ms', 'rtt min/avg/max/mdev = 0.287/0.287/0.287/0.000 ms'], 'stderr_lines': [], 'failed': False, 'item': 'pool-HP49D14', 'ansible_loop_var': 'item'}) => {
    "msg": "pool-8P49D14 -> pool-HP49D14.ris.bht-berlin.de OK\n"
}
ok: [pool-BP49D14] => (item={'changed': True, 'stdout': 'PING pool-BP49D14.ris.bht-berlin.de (141.64.89.66) 56(84) bytes of data.\n64 bytes from sun66.beuth-hochschule.de (141.64.89.66): icmp_seq=1 ttl=64 time=0.017 ms\n\n--- pool-BP49D14.ris.bht-berlin.de ping statistics ---\n1 packets transmitted, 1 received, 0% packet loss, time 0ms\nrtt min/avg/max/mdev = 0.017/0.017/0.017/0.000 ms', 'stderr': '', 'rc': 0, 'cmd': ['ping', '-c1', '-W1', 'pool-BP49D14.ris.bht-berlin.de'], 'start': '2026-06-30 18:35:30.118688', 'end': '2026-06-30 18:35:30.121578', 'delta': '0:00:00.002890', 'msg': '', 'invocation': {'module_args': {'_raw_params': 'ping -c1 -W1 pool-BP49D14.ris.bht-berlin.de\n', '_uses_shell': False, 'stdin_add_newline': True, 'strip_empty_ends': True, 'argv': None, 'chdir': None, 'executable': None, 'creates': None, 'removes': None, 'stdin': None}}, 'stdout_lines': ['PING pool-BP49D14.ris.bht-berlin.de (141.64.89.66) 56(84) bytes of data.', '64 bytes from sun66.beuth-hochschule.de (141.64.89.66): icmp_seq=1 ttl=64 time=0.017 ms', '', '--- pool-BP49D14.ris.bht-berlin.de ping statistics ---', '1 packets transmitted, 1 received, 0% packet loss, time 0ms', 'rtt min/avg/max/mdev = 0.017/0.017/0.017/0.000 ms'], 'stderr_lines': [], 'failed': False, 'item': 'pool-BP49D14', 'ansible_loop_var': 'item'}) => {
    "msg": "pool-BP49D14 -> pool-BP49D14.ris.bht-berlin.de OK\n"
}
ok: [pool-9N49D14] => (item={'changed': True, 'stdout': 'PING pool-HP49D14.ris.bht-berlin.de (141.64.89.80) 56(84) bytes of data.\n64 bytes from sun80.beuth-hochschule.de (141.64.89.80): icmp_seq=1 ttl=64 time=0.314 ms\n\n--- pool-HP49D14.ris.bht-berlin.de ping statistics ---\n1 packets transmitted, 1 received, 0% packet loss, time 0ms\nrtt min/avg/max/mdev = 0.314/0.314/0.314/0.000 ms', 'stderr': '', 'rc': 0, 'cmd': ['ping', '-c1', '-W1', 'pool-HP49D14.ris.bht-berlin.de'], 'start': '2026-06-30 18:35:30.535821', 'end': '2026-06-30 18:35:30.539300', 'delta': '0:00:00.003479', 'msg': '', 'invocation': {'module_args': {'_raw_params': 'ping -c1 -W1 pool-HP49D14.ris.bht-berlin.de\n', '_uses_shell': False, 'stdin_add_newline': True, 'strip_empty_ends': True, 'argv': None, 'chdir': None, 'executable': None, 'creates': None, 'removes': None, 'stdin': None}}, 'stdout_lines': ['PING pool-HP49D14.ris.bht-berlin.de (141.64.89.80) 56(84) bytes of data.', '64 bytes from sun80.beuth-hochschule.de (141.64.89.80): icmp_seq=1 ttl=64 time=0.314 ms', '', '--- pool-HP49D14.ris.bht-berlin.de ping statistics ---', '1 packets transmitted, 1 received, 0% packet loss, time 0ms', 'rtt min/avg/max/mdev = 0.314/0.314/0.314/0.000 ms'], 'stderr_lines': [], 'failed': False, 'item': 'pool-HP49D14', 'ansible_loop_var': 'item'}) => {
    "msg": "pool-9N49D14 -> pool-HP49D14.ris.bht-berlin.de OK\n"
}
ok: [pool-BN49D14] => (item={'changed': True, 'stdout': 'PING pool-BP49D14.ris.bht-berlin.de (141.64.89.66) 56(84) bytes of data.\n64 bytes from sun66.beuth-hochschule.de (141.64.89.66): icmp_seq=1 ttl=64 time=0.409 ms\n\n--- pool-BP49D14.ris.bht-berlin.de ping statistics ---\n1 packets transmitted, 1 received, 0% packet loss, time 0ms\nrtt min/avg/max/mdev = 0.409/0.409/0.409/0.000 ms', 'stderr': '', 'rc': 0, 'cmd': ['ping', '-c1', '-W1', 'pool-BP49D14.ris.bht-berlin.de'], 'start': '2026-06-30 18:35:30.102211', 'end': '2026-06-30 18:35:30.105498', 'delta': '0:00:00.003287', 'msg': '', 'invocation': {'module_args': {'_raw_params': 'ping -c1 -W1 pool-BP49D14.ris.bht-berlin.de\n', '_uses_shell': False, 'stdin_add_newline': True, 'strip_empty_ends': True, 'argv': None, 'chdir': None, 'executable': None, 'creates': None, 'removes': None, 'stdin': None}}, 'stdout_lines': ['PING pool-BP49D14.ris.bht-berlin.de (141.64.89.66) 56(84) bytes of data.', '64 bytes from sun66.beuth-hochschule.de (141.64.89.66): icmp_seq=1 ttl=64 time=0.409 ms', '', '--- pool-BP49D14.ris.bht-berlin.de ping statistics ---', '1 packets transmitted, 1 received, 0% packet loss, time 0ms', 'rtt min/avg/max/mdev = 0.409/0.409/0.409/0.000 ms'], 'stderr_lines': [], 'failed': False, 'item': 'pool-BP49D14', 'ansible_loop_var': 'item'}) => {
    "msg": "pool-BN49D14 -> pool-BP49D14.ris.bht-berlin.de OK\n"
}
ok: [pool-HN49D14] => (item={'changed': True, 'stdout': 'PING pool-8P49D14.ris.bht-berlin.de (141.64.89.60) 56(84) bytes of data.\n64 bytes from pool-8p49d14.ris.bht-berlin.de (141.64.89.60): icmp_seq=1 ttl=64 time=0.423 ms\n\n--- pool-8P49D14.ris.bht-berlin.de ping statistics ---\n1 packets transmitted, 1 received, 0% packet loss, time 0ms\nrtt min/avg/max/mdev = 0.423/0.423/0.423/0.000 ms', 'stderr': '', 'rc': 0, 'cmd': ['ping', '-c1', '-W1', 'pool-8P49D14.ris.bht-berlin.de'], 'start': '2026-06-30 18:35:31.484271', 'end': '2026-06-30 18:35:31.487868', 'delta': '0:00:00.003597', 'msg': '', 'invocation': {'module_args': {'_raw_params': 'ping -c1 -W1 pool-8P49D14.ris.bht-berlin.de\n', '_uses_shell': False, 'stdin_add_newline': True, 'strip_empty_ends': True, 'argv': None, 'chdir': None, 'executable': None, 'creates': None, 'removes': None, 'stdin': None}}, 'stdout_lines': ['PING pool-8P49D14.ris.bht-berlin.de (141.64.89.60) 56(84) bytes of data.', '64 bytes from pool-8p49d14.ris.bht-berlin.de (141.64.89.60): icmp_seq=1 ttl=64 time=0.423 ms', '', '--- pool-8P49D14.ris.bht-berlin.de ping statistics ---', '1 packets transmitted, 1 received, 0% packet loss, time 0ms', 'rtt min/avg/max/mdev = 0.423/0.423/0.423/0.000 ms'], 'stderr_lines': [], 'ansible_facts': {'discovered_interpreter_python': '/usr/bin/python3'}, 'failed': False, 'item': 'pool-8P49D14', 'ansible_loop_var': 'item'}) => {
    "msg": "pool-HN49D14 -> pool-8P49D14.ris.bht-berlin.de OK\n"
}
ok: [pool-BP49D14] => (item={'changed': True, 'stdout': 'PING pool-HN49D14.ris.bht-berlin.de (141.64.89.79) 56(84) bytes of data.\n64 bytes from sun79.bht-berlin.de (141.64.89.79): icmp_seq=1 ttl=64 time=0.657 ms\n\n--- pool-HN49D14.ris.bht-berlin.de ping statistics ---\n1 packets transmitted, 1 received, 0% packet loss, time 0ms\nrtt min/avg/max/mdev = 0.657/0.657/0.657/0.000 ms', 'stderr': '', 'rc': 0, 'cmd': ['ping', '-c1', '-W1', 'pool-HN49D14.ris.bht-berlin.de'], 'start': '2026-06-30 18:35:30.319591', 'end': '2026-06-30 18:35:30.323225', 'delta': '0:00:00.003634', 'msg': '', 'invocation': {'module_args': {'_raw_params': 'ping -c1 -W1 pool-HN49D14.ris.bht-berlin.de\n', '_uses_shell': False, 'stdin_add_newline': True, 'strip_empty_ends': True, 'argv': None, 'chdir': None, 'executable': None, 'creates': None, 'removes': None, 'stdin': None}}, 'stdout_lines': ['PING pool-HN49D14.ris.bht-berlin.de (141.64.89.79) 56(84) bytes of data.', '64 bytes from sun79.bht-berlin.de (141.64.89.79): icmp_seq=1 ttl=64 time=0.657 ms', '', '--- pool-HN49D14.ris.bht-berlin.de ping statistics ---', '1 packets transmitted, 1 received, 0% packet loss, time 0ms', 'rtt min/avg/max/mdev = 0.657/0.657/0.657/0.000 ms'], 'stderr_lines': [], 'failed': False, 'item': 'pool-HN49D14', 'ansible_loop_var': 'item'}) => {
    "msg": "pool-BP49D14 -> pool-HN49D14.ris.bht-berlin.de OK\n"
}
ok: [pool-HN49D14] => (item={'changed': True, 'stdout': 'PING pool-8Q49D14.ris.bht-berlin.de (141.64.89.61) 56(84) bytes of data.\n64 bytes from sun61.bht-berlin.de (141.64.89.61): icmp_seq=1 ttl=64 time=0.640 ms\n\n--- pool-8Q49D14.ris.bht-berlin.de ping statistics ---\n1 packets transmitted, 1 received, 0% packet loss, time 0ms\nrtt min/avg/max/mdev = 0.640/0.640/0.640/0.000 ms', 'stderr': '', 'rc': 0, 'cmd': ['ping', '-c1', '-W1', 'pool-8Q49D14.ris.bht-berlin.de'], 'start': '2026-06-30 18:35:31.613848', 'end': '2026-06-30 18:35:31.617333', 'delta': '0:00:00.003485', 'msg': '', 'invocation': {'module_args': {'_raw_params': 'ping -c1 -W1 pool-8Q49D14.ris.bht-berlin.de\n', '_uses_shell': False, 'stdin_add_newline': True, 'strip_empty_ends': True, 'argv': None, 'chdir': None, 'executable': None, 'creates': None, 'removes': None, 'stdin': None}}, 'stdout_lines': ['PING pool-8Q49D14.ris.bht-berlin.de (141.64.89.61) 56(84) bytes of data.', '64 bytes from sun61.bht-berlin.de (141.64.89.61): icmp_seq=1 ttl=64 time=0.640 ms', '', '--- pool-8Q49D14.ris.bht-berlin.de ping statistics ---', '1 packets transmitted, 1 received, 0% packet loss, time 0ms', 'rtt min/avg/max/mdev = 0.640/0.640/0.640/0.000 ms'], 'stderr_lines': [], 'failed': False, 'item': 'pool-8Q49D14', 'ansible_loop_var': 'item'}) => {
    "msg": "pool-HN49D14 -> pool-8Q49D14.ris.bht-berlin.de OK\n"
}
ok: [pool-BP49D14] => (item={'changed': True, 'stdout': 'PING pool-HP49D14.ris.bht-berlin.de (141.64.89.80) 56(84) bytes of data.\n64 bytes from sun80.beuth-hochschule.de (141.64.89.80): icmp_seq=1 ttl=64 time=0.460 ms\n\n--- pool-HP49D14.ris.bht-berlin.de ping statistics ---\n1 packets transmitted, 1 received, 0% packet loss, time 0ms\nrtt min/avg/max/mdev = 0.460/0.460/0.460/0.000 ms', 'stderr': '', 'rc': 0, 'cmd': ['ping', '-c1', '-W1', 'pool-HP49D14.ris.bht-berlin.de'], 'start': '2026-06-30 18:35:30.530772', 'end': '2026-06-30 18:35:30.534241', 'delta': '0:00:00.003469', 'msg': '', 'invocation': {'module_args': {'_raw_params': 'ping -c1 -W1 pool-HP49D14.ris.bht-berlin.de\n', '_uses_shell': False, 'stdin_add_newline': True, 'strip_empty_ends': True, 'argv': None, 'chdir': None, 'executable': None, 'creates': None, 'removes': None, 'stdin': None}}, 'stdout_lines': ['PING pool-HP49D14.ris.bht-berlin.de (141.64.89.80) 56(84) bytes of data.', '64 bytes from sun80.beuth-hochschule.de (141.64.89.80): icmp_seq=1 ttl=64 time=0.460 ms', '', '--- pool-HP49D14.ris.bht-berlin.de ping statistics ---', '1 packets transmitted, 1 received, 0% packet loss, time 0ms', 'rtt min/avg/max/mdev = 0.460/0.460/0.460/0.000 ms'], 'stderr_lines': [], 'failed': False, 'item': 'pool-HP49D14', 'ansible_loop_var': 'item'}) => {
    "msg": "pool-BP49D14 -> pool-HP49D14.ris.bht-berlin.de OK\n"
}
ok: [pool-BN49D14] => (item={'changed': True, 'stdout': 'PING pool-HN49D14.ris.bht-berlin.de (141.64.89.79) 56(84) bytes of data.\n64 bytes from sun79.bht-berlin.de (141.64.89.79): icmp_seq=1 ttl=64 time=0.715 ms\n\n--- pool-HN49D14.ris.bht-berlin.de ping statistics ---\n1 packets transmitted, 1 received, 0% packet loss, time 0ms\nrtt min/avg/max/mdev = 0.715/0.715/0.715/0.000 ms', 'stderr': '', 'rc': 0, 'cmd': ['ping', '-c1', '-W1', 'pool-HN49D14.ris.bht-berlin.de'], 'start': '2026-06-30 18:35:30.315531', 'end': '2026-06-30 18:35:30.319209', 'delta': '0:00:00.003678', 'msg': '', 'invocation': {'module_args': {'_raw_params': 'ping -c1 -W1 pool-HN49D14.ris.bht-berlin.de\n', '_uses_shell': False, 'stdin_add_newline': True, 'strip_empty_ends': True, 'argv': None, 'chdir': None, 'executable': None, 'creates': None, 'removes': None, 'stdin': None}}, 'stdout_lines': ['PING pool-HN49D14.ris.bht-berlin.de (141.64.89.79) 56(84) bytes of data.', '64 bytes from sun79.bht-berlin.de (141.64.89.79): icmp_seq=1 ttl=64 time=0.715 ms', '', '--- pool-HN49D14.ris.bht-berlin.de ping statistics ---', '1 packets transmitted, 1 received, 0% packet loss, time 0ms', 'rtt min/avg/max/mdev = 0.715/0.715/0.715/0.000 ms'], 'stderr_lines': [], 'failed': False, 'item': 'pool-HN49D14', 'ansible_loop_var': 'item'}) => {
    "msg": "pool-BN49D14 -> pool-HN49D14.ris.bht-berlin.de OK\n"
}
ok: [pool-HP49D14] => (item={'changed': True, 'stdout': 'PING pool-8P49D14.ris.bht-berlin.de (141.64.89.60) 56(84) bytes of data.\n64 bytes from pool-8p49d14.ris.bht-berlin.de (141.64.89.60): icmp_seq=1 ttl=64 time=0.458 ms\n\n--- pool-8P49D14.ris.bht-berlin.de ping statistics ---\n1 packets transmitted, 1 received, 0% packet loss, time 0ms\nrtt min/avg/max/mdev = 0.458/0.458/0.458/0.000 ms', 'stderr': '', 'rc': 0, 'cmd': ['ping', '-c1', '-W1', 'pool-8P49D14.ris.bht-berlin.de'], 'start': '2026-06-30 18:35:31.285115', 'end': '2026-06-30 18:35:31.288712', 'delta': '0:00:00.003597', 'msg': '', 'invocation': {'module_args': {'_raw_params': 'ping -c1 -W1 pool-8P49D14.ris.bht-berlin.de\n', '_uses_shell': False, 'stdin_add_newline': True, 'strip_empty_ends': True, 'argv': None, 'chdir': None, 'executable': None, 'creates': None, 'removes': None, 'stdin': None}}, 'stdout_lines': ['PING pool-8P49D14.ris.bht-berlin.de (141.64.89.60) 56(84) bytes of data.', '64 bytes from pool-8p49d14.ris.bht-berlin.de (141.64.89.60): icmp_seq=1 ttl=64 time=0.458 ms', '', '--- pool-8P49D14.ris.bht-berlin.de ping statistics ---', '1 packets transmitted, 1 received, 0% packet loss, time 0ms', 'rtt min/avg/max/mdev = 0.458/0.458/0.458/0.000 ms'], 'stderr_lines': [], 'ansible_facts': {'discovered_interpreter_python': '/usr/bin/python3'}, 'failed': False, 'item': 'pool-8P49D14', 'ansible_loop_var': 'item'}) => {
    "msg": "pool-HP49D14 -> pool-8P49D14.ris.bht-berlin.de OK\n"
}
ok: [pool-HN49D14] => (item={'changed': True, 'stdout': 'PING pool-9N49D14.ris.bht-berlin.de (141.64.89.62) 56(84) bytes of data.\n64 bytes from sun62.bht-berlin.de (141.64.89.62): icmp_seq=1 ttl=64 time=0.581 ms\n\n--- pool-9N49D14.ris.bht-berlin.de ping statistics ---\n1 packets transmitted, 1 received, 0% packet loss, time 0ms\nrtt min/avg/max/mdev = 0.581/0.581/0.581/0.000 ms', 'stderr': '', 'rc': 0, 'cmd': ['ping', '-c1', '-W1', 'pool-9N49D14.ris.bht-berlin.de'], 'start': '2026-06-30 18:35:31.756552', 'end': '2026-06-30 18:35:31.760441', 'delta': '0:00:00.003889', 'msg': '', 'invocation': {'module_args': {'_raw_params': 'ping -c1 -W1 pool-9N49D14.ris.bht-berlin.de\n', '_uses_shell': False, 'stdin_add_newline': True, 'strip_empty_ends': True, 'argv': None, 'chdir': None, 'executable': None, 'creates': None, 'removes': None, 'stdin': None}}, 'stdout_lines': ['PING pool-9N49D14.ris.bht-berlin.de (141.64.89.62) 56(84) bytes of data.', '64 bytes from sun62.bht-berlin.de (141.64.89.62): icmp_seq=1 ttl=64 time=0.581 ms', '', '--- pool-9N49D14.ris.bht-berlin.de ping statistics ---', '1 packets transmitted, 1 received, 0% packet loss, time 0ms', 'rtt min/avg/max/mdev = 0.581/0.581/0.581/0.000 ms'], 'stderr_lines': [], 'failed': False, 'item': 'pool-9N49D14', 'ansible_loop_var': 'item'}) => {
    "msg": "pool-HN49D14 -> pool-9N49D14.ris.bht-berlin.de OK\n"
}
ok: [pool-BN49D14] => (item={'changed': True, 'stdout': 'PING pool-HP49D14.ris.bht-berlin.de (141.64.89.80) 56(84) bytes of data.\n64 bytes from sun80.beuth-hochschule.de (141.64.89.80): icmp_seq=1 ttl=64 time=0.293 ms\n\n--- pool-HP49D14.ris.bht-berlin.de ping statistics ---\n1 packets transmitted, 1 received, 0% packet loss, time 0ms\nrtt min/avg/max/mdev = 0.293/0.293/0.293/0.000 ms', 'stderr': '', 'rc': 0, 'cmd': ['ping', '-c1', '-W1', 'pool-HP49D14.ris.bht-berlin.de'], 'start': '2026-06-30 18:35:30.537163', 'end': '2026-06-30 18:35:30.540668', 'delta': '0:00:00.003505', 'msg': '', 'invocation': {'module_args': {'_raw_params': 'ping -c1 -W1 pool-HP49D14.ris.bht-berlin.de\n', '_uses_shell': False, 'stdin_add_newline': True, 'strip_empty_ends': True, 'argv': None, 'chdir': None, 'executable': None, 'creates': None, 'removes': None, 'stdin': None}}, 'stdout_lines': ['PING pool-HP49D14.ris.bht-berlin.de (141.64.89.80) 56(84) bytes of data.', '64 bytes from sun80.beuth-hochschule.de (141.64.89.80): icmp_seq=1 ttl=64 time=0.293 ms', '', '--- pool-HP49D14.ris.bht-berlin.de ping statistics ---', '1 packets transmitted, 1 received, 0% packet loss, time 0ms', 'rtt min/avg/max/mdev = 0.293/0.293/0.293/0.000 ms'], 'stderr_lines': [], 'failed': False, 'item': 'pool-HP49D14', 'ansible_loop_var': 'item'}) => {
    "msg": "pool-BN49D14 -> pool-HP49D14.ris.bht-berlin.de OK\n"
}
ok: [pool-HP49D14] => (item={'changed': True, 'stdout': 'PING pool-8Q49D14.ris.bht-berlin.de (141.64.89.61) 56(84) bytes of data.\n64 bytes from sun61.bht-berlin.de (141.64.89.61): icmp_seq=1 ttl=64 time=0.701 ms\n\n--- pool-8Q49D14.ris.bht-berlin.de ping statistics ---\n1 packets transmitted, 1 received, 0% packet loss, time 0ms\nrtt min/avg/max/mdev = 0.701/0.701/0.701/0.000 ms', 'stderr': '', 'rc': 0, 'cmd': ['ping', '-c1', '-W1', 'pool-8Q49D14.ris.bht-berlin.de'], 'start': '2026-06-30 18:35:31.411051', 'end': '2026-06-30 18:35:31.414636', 'delta': '0:00:00.003585', 'msg': '', 'invocation': {'module_args': {'_raw_params': 'ping -c1 -W1 pool-8Q49D14.ris.bht-berlin.de\n', '_uses_shell': False, 'stdin_add_newline': True, 'strip_empty_ends': True, 'argv': None, 'chdir': None, 'executable': None, 'creates': None, 'removes': None, 'stdin': None}}, 'stdout_lines': ['PING pool-8Q49D14.ris.bht-berlin.de (141.64.89.61) 56(84) bytes of data.', '64 bytes from sun61.bht-berlin.de (141.64.89.61): icmp_seq=1 ttl=64 time=0.701 ms', '', '--- pool-8Q49D14.ris.bht-berlin.de ping statistics ---', '1 packets transmitted, 1 received, 0% packet loss, time 0ms', 'rtt min/avg/max/mdev = 0.701/0.701/0.701/0.000 ms'], 'stderr_lines': [], 'failed': False, 'item': 'pool-8Q49D14', 'ansible_loop_var': 'item'}) => {
    "msg": "pool-HP49D14 -> pool-8Q49D14.ris.bht-berlin.de OK\n"
}
ok: [pool-HN49D14] => (item={'changed': True, 'stdout': 'PING pool-BN49D14.ris.bht-berlin.de (141.64.89.65) 56(84) bytes of data.\n64 bytes from pool-bn49d14.ris.bht-berlin.de (141.64.89.65): icmp_seq=1 ttl=64 time=0.615 ms\n\n--- pool-BN49D14.ris.bht-berlin.de ping statistics ---\n1 packets transmitted, 1 received, 0% packet loss, time 0ms\nrtt min/avg/max/mdev = 0.615/0.615/0.615/0.000 ms', 'stderr': '', 'rc': 0, 'cmd': ['ping', '-c1', '-W1', 'pool-BN49D14.ris.bht-berlin.de'], 'start': '2026-06-30 18:35:31.906228', 'end': '2026-06-30 18:35:31.910404', 'delta': '0:00:00.004176', 'msg': '', 'invocation': {'module_args': {'_raw_params': 'ping -c1 -W1 pool-BN49D14.ris.bht-berlin.de\n', '_uses_shell': False, 'stdin_add_newline': True, 'strip_empty_ends': True, 'argv': None, 'chdir': None, 'executable': None, 'creates': None, 'removes': None, 'stdin': None}}, 'stdout_lines': ['PING pool-BN49D14.ris.bht-berlin.de (141.64.89.65) 56(84) bytes of data.', '64 bytes from pool-bn49d14.ris.bht-berlin.de (141.64.89.65): icmp_seq=1 ttl=64 time=0.615 ms', '', '--- pool-BN49D14.ris.bht-berlin.de ping statistics ---', '1 packets transmitted, 1 received, 0% packet loss, time 0ms', 'rtt min/avg/max/mdev = 0.615/0.615/0.615/0.000 ms'], 'stderr_lines': [], 'failed': False, 'item': 'pool-BN49D14', 'ansible_loop_var': 'item'}) => {
    "msg": "pool-HN49D14 -> pool-BN49D14.ris.bht-berlin.de OK\n"
}
ok: [pool-HP49D14] => (item={'changed': True, 'stdout': 'PING pool-9N49D14.ris.bht-berlin.de (141.64.89.62) 56(84) bytes of data.\n64 bytes from sun62.bht-berlin.de (141.64.89.62): icmp_seq=1 ttl=64 time=0.551 ms\n\n--- pool-9N49D14.ris.bht-berlin.de ping statistics ---\n1 packets transmitted, 1 received, 0% packet loss, time 0ms\nrtt min/avg/max/mdev = 0.551/0.551/0.551/0.000 ms', 'stderr': '', 'rc': 0, 'cmd': ['ping', '-c1', '-W1', 'pool-9N49D14.ris.bht-berlin.de'], 'start': '2026-06-30 18:35:31.536246', 'end': '2026-06-30 18:35:31.539313', 'delta': '0:00:00.003067', 'msg': '', 'invocation': {'module_args': {'_raw_params': 'ping -c1 -W1 pool-9N49D14.ris.bht-berlin.de\n', '_uses_shell': False, 'stdin_add_newline': True, 'strip_empty_ends': True, 'argv': None, 'chdir': None, 'executable': None, 'creates': None, 'removes': None, 'stdin': None}}, 'stdout_lines': ['PING pool-9N49D14.ris.bht-berlin.de (141.64.89.62) 56(84) bytes of data.', '64 bytes from sun62.bht-berlin.de (141.64.89.62): icmp_seq=1 ttl=64 time=0.551 ms', '', '--- pool-9N49D14.ris.bht-berlin.de ping statistics ---', '1 packets transmitted, 1 received, 0% packet loss, time 0ms', 'rtt min/avg/max/mdev = 0.551/0.551/0.551/0.000 ms'], 'stderr_lines': [], 'failed': False, 'item': 'pool-9N49D14', 'ansible_loop_var': 'item'}) => {
    "msg": "pool-HP49D14 -> pool-9N49D14.ris.bht-berlin.de OK\n"
}
ok: [pool-HN49D14] => (item={'changed': True, 'stdout': 'PING pool-BP49D14.ris.bht-berlin.de (141.64.89.66) 56(84) bytes of data.\n64 bytes from sun66.beuth-hochschule.de (141.64.89.66): icmp_seq=1 ttl=64 time=0.636 ms\n\n--- pool-BP49D14.ris.bht-berlin.de ping statistics ---\n1 packets transmitted, 1 received, 0% packet loss, time 0ms\nrtt min/avg/max/mdev = 0.636/0.636/0.636/0.000 ms', 'stderr': '', 'rc': 0, 'cmd': ['ping', '-c1', '-W1', 'pool-BP49D14.ris.bht-berlin.de'], 'start': '2026-06-30 18:35:32.057023', 'end': '2026-06-30 18:35:32.060912', 'delta': '0:00:00.003889', 'msg': '', 'invocation': {'module_args': {'_raw_params': 'ping -c1 -W1 pool-BP49D14.ris.bht-berlin.de\n', '_uses_shell': False, 'stdin_add_newline': True, 'strip_empty_ends': True, 'argv': None, 'chdir': None, 'executable': None, 'creates': None, 'removes': None, 'stdin': None}}, 'stdout_lines': ['PING pool-BP49D14.ris.bht-berlin.de (141.64.89.66) 56(84) bytes of data.', '64 bytes from sun66.beuth-hochschule.de (141.64.89.66): icmp_seq=1 ttl=64 time=0.636 ms', '', '--- pool-BP49D14.ris.bht-berlin.de ping statistics ---', '1 packets transmitted, 1 received, 0% packet loss, time 0ms', 'rtt min/avg/max/mdev = 0.636/0.636/0.636/0.000 ms'], 'stderr_lines': [], 'failed': False, 'item': 'pool-BP49D14', 'ansible_loop_var': 'item'}) => {
    "msg": "pool-HN49D14 -> pool-BP49D14.ris.bht-berlin.de OK\n"
}
ok: [pool-HN49D14] => (item={'changed': True, 'stdout': 'PING pool-HN49D14.ris.bht-berlin.de (141.64.89.79) 56(84) bytes of data.\n64 bytes from sun79.bht-berlin.de (141.64.89.79): icmp_seq=1 ttl=64 time=0.018 ms\n\n--- pool-HN49D14.ris.bht-berlin.de ping statistics ---\n1 packets transmitted, 1 received, 0% packet loss, time 0ms\nrtt min/avg/max/mdev = 0.018/0.018/0.018/0.000 ms', 'stderr': '', 'rc': 0, 'cmd': ['ping', '-c1', '-W1', 'pool-HN49D14.ris.bht-berlin.de'], 'start': '2026-06-30 18:35:32.236960', 'end': '2026-06-30 18:35:32.239872', 'delta': '0:00:00.002912', 'msg': '', 'invocation': {'module_args': {'_raw_params': 'ping -c1 -W1 pool-HN49D14.ris.bht-berlin.de\n', '_uses_shell': False, 'stdin_add_newline': True, 'strip_empty_ends': True, 'argv': None, 'chdir': None, 'executable': None, 'creates': None, 'removes': None, 'stdin': None}}, 'stdout_lines': ['PING pool-HN49D14.ris.bht-berlin.de (141.64.89.79) 56(84) bytes of data.', '64 bytes from sun79.bht-berlin.de (141.64.89.79): icmp_seq=1 ttl=64 time=0.018 ms', '', '--- pool-HN49D14.ris.bht-berlin.de ping statistics ---', '1 packets transmitted, 1 received, 0% packet loss, time 0ms', 'rtt min/avg/max/mdev = 0.018/0.018/0.018/0.000 ms'], 'stderr_lines': [], 'failed': False, 'item': 'pool-HN49D14', 'ansible_loop_var': 'item'}) => {
    "msg": "pool-HN49D14 -> pool-HN49D14.ris.bht-berlin.de OK\n"
}
ok: [pool-HP49D14] => (item={'changed': True, 'stdout': 'PING pool-BN49D14.ris.bht-berlin.de (141.64.89.65) 56(84) bytes of data.\n64 bytes from pool-bn49d14.ris.bht-berlin.de (141.64.89.65): icmp_seq=1 ttl=64 time=0.502 ms\n\n--- pool-BN49D14.ris.bht-berlin.de ping statistics ---\n1 packets transmitted, 1 received, 0% packet loss, time 0ms\nrtt min/avg/max/mdev = 0.502/0.502/0.502/0.000 ms', 'stderr': '', 'rc': 0, 'cmd': ['ping', '-c1', '-W1', 'pool-BN49D14.ris.bht-berlin.de'], 'start': '2026-06-30 18:35:31.690005', 'end': '2026-06-30 18:35:31.693125', 'delta': '0:00:00.003120', 'msg': '', 'invocation': {'module_args': {'_raw_params': 'ping -c1 -W1 pool-BN49D14.ris.bht-berlin.de\n', '_uses_shell': False, 'stdin_add_newline': True, 'strip_empty_ends': True, 'argv': None, 'chdir': None, 'executable': None, 'creates': None, 'removes': None, 'stdin': None}}, 'stdout_lines': ['PING pool-BN49D14.ris.bht-berlin.de (141.64.89.65) 56(84) bytes of data.', '64 bytes from pool-bn49d14.ris.bht-berlin.de (141.64.89.65): icmp_seq=1 ttl=64 time=0.502 ms', '', '--- pool-BN49D14.ris.bht-berlin.de ping statistics ---', '1 packets transmitted, 1 received, 0% packet loss, time 0ms', 'rtt min/avg/max/mdev = 0.502/0.502/0.502/0.000 ms'], 'stderr_lines': [], 'failed': False, 'item': 'pool-BN49D14', 'ansible_loop_var': 'item'}) => {
    "msg": "pool-HP49D14 -> pool-BN49D14.ris.bht-berlin.de OK\n"
}
ok: [pool-HN49D14] => (item={'changed': True, 'stdout': 'PING pool-HP49D14.ris.bht-berlin.de (141.64.89.80) 56(84) bytes of data.\n64 bytes from sun80.beuth-hochschule.de (141.64.89.80): icmp_seq=1 ttl=64 time=0.508 ms\n\n--- pool-HP49D14.ris.bht-berlin.de ping statistics ---\n1 packets transmitted, 1 received, 0% packet loss, time 0ms\nrtt min/avg/max/mdev = 0.508/0.508/0.508/0.000 ms', 'stderr': '', 'rc': 0, 'cmd': ['ping', '-c1', '-W1', 'pool-HP49D14.ris.bht-berlin.de'], 'start': '2026-06-30 18:35:32.414564', 'end': '2026-06-30 18:35:32.418236', 'delta': '0:00:00.003672', 'msg': '', 'invocation': {'module_args': {'_raw_params': 'ping -c1 -W1 pool-HP49D14.ris.bht-berlin.de\n', '_uses_shell': False, 'stdin_add_newline': True, 'strip_empty_ends': True, 'argv': None, 'chdir': None, 'executable': None, 'creates': None, 'removes': None, 'stdin': None}}, 'stdout_lines': ['PING pool-HP49D14.ris.bht-berlin.de (141.64.89.80) 56(84) bytes of data.', '64 bytes from sun80.beuth-hochschule.de (141.64.89.80): icmp_seq=1 ttl=64 time=0.508 ms', '', '--- pool-HP49D14.ris.bht-berlin.de ping statistics ---', '1 packets transmitted, 1 received, 0% packet loss, time 0ms', 'rtt min/avg/max/mdev = 0.508/0.508/0.508/0.000 ms'], 'stderr_lines': [], 'failed': False, 'item': 'pool-HP49D14', 'ansible_loop_var': 'item'}) => {
    "msg": "pool-HN49D14 -> pool-HP49D14.ris.bht-berlin.de OK\n"
}
ok: [pool-HP49D14] => (item={'changed': True, 'stdout': 'PING pool-BP49D14.ris.bht-berlin.de (141.64.89.66) 56(84) bytes of data.\n64 bytes from sun66.beuth-hochschule.de (141.64.89.66): icmp_seq=1 ttl=64 time=0.366 ms\n\n--- pool-BP49D14.ris.bht-berlin.de ping statistics ---\n1 packets transmitted, 1 received, 0% packet loss, time 0ms\nrtt min/avg/max/mdev = 0.366/0.366/0.366/0.000 ms', 'stderr': '', 'rc': 0, 'cmd': ['ping', '-c1', '-W1', 'pool-BP49D14.ris.bht-berlin.de'], 'start': '2026-06-30 18:35:31.819712', 'end': '2026-06-30 18:35:31.822825', 'delta': '0:00:00.003113', 'msg': '', 'invocation': {'module_args': {'_raw_params': 'ping -c1 -W1 pool-BP49D14.ris.bht-berlin.de\n', '_uses_shell': False, 'stdin_add_newline': True, 'strip_empty_ends': True, 'argv': None, 'chdir': None, 'executable': None, 'creates': None, 'removes': None, 'stdin': None}}, 'stdout_lines': ['PING pool-BP49D14.ris.bht-berlin.de (141.64.89.66) 56(84) bytes of data.', '64 bytes from sun66.beuth-hochschule.de (141.64.89.66): icmp_seq=1 ttl=64 time=0.366 ms', '', '--- pool-BP49D14.ris.bht-berlin.de ping statistics ---', '1 packets transmitted, 1 received, 0% packet loss, time 0ms', 'rtt min/avg/max/mdev = 0.366/0.366/0.366/0.000 ms'], 'stderr_lines': [], 'failed': False, 'item': 'pool-BP49D14', 'ansible_loop_var': 'item'}) => {
    "msg": "pool-HP49D14 -> pool-BP49D14.ris.bht-berlin.de OK\n"
}
ok: [pool-HP49D14] => (item={'changed': True, 'stdout': 'PING pool-HN49D14.ris.bht-berlin.de (141.64.89.79) 56(84) bytes of data.\n64 bytes from sun79.bht-berlin.de (141.64.89.79): icmp_seq=1 ttl=64 time=0.225 ms\n\n--- pool-HN49D14.ris.bht-berlin.de ping statistics ---\n1 packets transmitted, 1 received, 0% packet loss, time 0ms\nrtt min/avg/max/mdev = 0.225/0.225/0.225/0.000 ms', 'stderr': '', 'rc': 0, 'cmd': ['ping', '-c1', '-W1', 'pool-HN49D14.ris.bht-berlin.de'], 'start': '2026-06-30 18:35:31.958303', 'end': '2026-06-30 18:35:31.961542', 'delta': '0:00:00.003239', 'msg': '', 'invocation': {'module_args': {'_raw_params': 'ping -c1 -W1 pool-HN49D14.ris.bht-berlin.de\n', '_uses_shell': False, 'stdin_add_newline': True, 'strip_empty_ends': True, 'argv': None, 'chdir': None, 'executable': None, 'creates': None, 'removes': None, 'stdin': None}}, 'stdout_lines': ['PING pool-HN49D14.ris.bht-berlin.de (141.64.89.79) 56(84) bytes of data.', '64 bytes from sun79.bht-berlin.de (141.64.89.79): icmp_seq=1 ttl=64 time=0.225 ms', '', '--- pool-HN49D14.ris.bht-berlin.de ping statistics ---', '1 packets transmitted, 1 received, 0% packet loss, time 0ms', 'rtt min/avg/max/mdev = 0.225/0.225/0.225/0.000 ms'], 'stderr_lines': [], 'failed': False, 'item': 'pool-HN49D14', 'ansible_loop_var': 'item'}) => {
    "msg": "pool-HP49D14 -> pool-HN49D14.ris.bht-berlin.de OK\n"
}
ok: [pool-HP49D14] => (item={'changed': True, 'stdout': 'PING pool-HP49D14.ris.bht-berlin.de (141.64.89.80) 56(84) bytes of data.\n64 bytes from sun80.beuth-hochschule.de (141.64.89.80): icmp_seq=1 ttl=64 time=0.017 ms\n\n--- pool-HP49D14.ris.bht-berlin.de ping statistics ---\n1 packets transmitted, 1 received, 0% packet loss, time 0ms\nrtt min/avg/max/mdev = 0.017/0.017/0.017/0.000 ms', 'stderr': '', 'rc': 0, 'cmd': ['ping', '-c1', '-W1', 'pool-HP49D14.ris.bht-berlin.de'], 'start': '2026-06-30 18:35:32.079404', 'end': '2026-06-30 18:35:32.082255', 'delta': '0:00:00.002851', 'msg': '', 'invocation': {'module_args': {'_raw_params': 'ping -c1 -W1 pool-HP49D14.ris.bht-berlin.de\n', '_uses_shell': False, 'stdin_add_newline': True, 'strip_empty_ends': True, 'argv': None, 'chdir': None, 'executable': None, 'creates': None, 'removes': None, 'stdin': None}}, 'stdout_lines': ['PING pool-HP49D14.ris.bht-berlin.de (141.64.89.80) 56(84) bytes of data.', '64 bytes from sun80.beuth-hochschule.de (141.64.89.80): icmp_seq=1 ttl=64 time=0.017 ms', '', '--- pool-HP49D14.ris.bht-berlin.de ping statistics ---', '1 packets transmitted, 1 received, 0% packet loss, time 0ms', 'rtt min/avg/max/mdev = 0.017/0.017/0.017/0.000 ms'], 'stderr_lines': [], 'failed': False, 'item': 'pool-HP49D14', 'ansible_loop_var': 'item'}) => {
    "msg": "pool-HP49D14 -> pool-HP49D14.ris.bht-berlin.de OK\n"
}

PLAY RECAP *********************************************************************************************
pool-8P49D14               : ok=2    changed=1    unreachable=0    failed=0    skipped=0    rescued=0    ignored=0   
pool-8Q49D14               : ok=2    changed=1    unreachable=0    failed=0    skipped=0    rescued=0    ignored=0   
pool-9N49D14               : ok=2    changed=1    unreachable=0    failed=0    skipped=0    rescued=0    ignored=0   
pool-BN49D14               : ok=2    changed=1    unreachable=0    failed=0    skipped=0    rescued=0    ignored=0   
pool-BP49D14               : ok=2    changed=1    unreachable=0    failed=0    skipped=0    rescued=0    ignored=0   
pool-HN49D14               : ok=2    changed=1    unreachable=0    failed=0    skipped=0    rescued=0    ignored=0   
pool-HP49D14               : ok=2    changed=1    unreachable=0    failed=0    skipped=0    rescued=0    ignored=0   


