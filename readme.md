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

