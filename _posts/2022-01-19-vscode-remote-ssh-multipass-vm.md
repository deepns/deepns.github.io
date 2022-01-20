---
title: Using vscode remote-ssh with a multipass vm
category:
    - Tech
tags:
    - vscode
    - programming
    - productivity
header:
  teaser: /assets/images/teasers/multipass-ubuntu.png
---

When working with multipass Ubuntu VMs, the standard way is to use `multipass shell [vmname]`. I often switch between my mac and the Ubuntu VM for different experiments. I wanted to connect VSCode to my Ubuntu VM over [remote-ssh](https://code.visualstudio.com/docs/remote/ssh) so I can have relevant extensions installed directly in the VM and have more native environment. Multipass VMs are set up with key based authentication and the default keys are available at **/var/root/Library/Application\ Support/multipassd/ssh-keys/id_rsa** on macOS installations. Due to [System Integrity Protection](https://support.apple.com/en-us/HT204899), contents under **/var/** requires root access.

```console
➜  ~ ls /var
/var
➜  ~ ls /var/root/Library/Application\ Support/multipassd/ssh-keys/id_rsa
ls: /var/root/Library/Application Support/multipassd/ssh-keys/id_rsa: Permission denied
➜  ~ sudo ls -l /var/root/Library/Application\ Support/multipassd/ssh-keys/id_rsa
-r--------  1 root  wheel  1704 Aug 17  2020 /var/root/Library/Application Support/multipassd/ssh-keys/id_rsa
➜  ~ sudo ls -l /var/root/Library/Application\ Support/multipassd/ssh-keys/id_rsa
```

With the ssh key and the IP, we can then ssh into the VM.

```console
➜  ~ multipass info ubuntu-lts
Name:           ubuntu-lts
State:          Running
IPv4:           192.168.64.2
Release:        Ubuntu 20.04.3 LTS
Image hash:     9885804a77e0 (Ubuntu 20.04 LTS)
Load:           0.10 0.04 0.08
Disk usage:     2.8G out of 4.7G
Memory usage:   728.6M out of 976.9M
Mounts:         /Users/deepan => Home
                    UID map: 501:default
                    GID map: 20:default

➜  ~  sudo ssh -i "/var/root/Library/Application Support/multipassd/ssh-keys/id_rsa" ubuntu@192.168.64.2
Password:
ubuntu@ubuntu-lts:~$ uname -a
Linux ubuntu-lts 5.4.0-94-generic #106-Ubuntu SMP Thu Jan 6 23:58:14 UTC 2022 x86_64 x86_64 x86_64 GNU/Linux
ubuntu@ubuntu-lts:~$
```

This is little cumbersome though. We could copy the key to another location but will have to update the permissions to provide non-root access anyway. So I preferred to have a separate key instead of using the default one with root permissions. I created a new key pair with **ssh-keygen** and added the public key to **.ssh/authorized_keys** inside the VM. I was then able to connect to the VM over vscode remote-ssh and continue the development as usual.
