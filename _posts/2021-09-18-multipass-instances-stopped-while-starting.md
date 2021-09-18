---
title: Multipass instance stopped while starting
category:
    - Tech
tags:
    - ubuntu
    - linux
header:
  teaser: /assets/images/teasers/multipass-ubuntu.png
---

[Multipass](https://multipass.run/docs) is a great framework to run Ubuntu VMs locally. Running a full fledged VM in a Virtual Box or VMWare environment is truly an overkill for many use cases. I just want my setup to be light weight, allow terminal access, spin up and spin down in a few seconds, and doesn't weigh down the host OS. Multipass ticks all of that.

Sometimes multipass instances can fail to start, especially after the host OS has gone through a crash or dirty shutdown. I saw only very minimal info on the console when I ran `multipass start` command, even with at the highest verbose level `-vvvv`.

```text
~ % multipass start -vvvv ubuntu-lts
start failed: The following errors occurred:
Instance stopped while starting

~ % multipass ls
Name                    State             IPv4             Image
ubuntu-lts              Starting          -                Ubuntu 20.04 LTS
```

I checked the multipass logs (`/Library/Logs/Multipass/multipassd.log`) at the time when I started the instance. It showed timeout errors in opening a SSH session to the instance, likely because the instance wasn't started.

```text
[2021-09-17T08:21:29.926] [debug] [ubuntu-lts] Trying SSH on 192.168.64.2:22
[2021-09-17T08:21:58.887] [info] [daemon] Cannot open ssh session on "ubuntu-lts" shutdown: ssh connection failed: 'Timeout connecting to 192.168.64.2'
[2021-09-17T08:21:58.889] [debug] [sshfs-mounts] No mounts to stop for instance "ubuntu-lts"
[2021-09-17T08:22:07.270] [debug] [ubuntu-lts] Trying SSH on 192.168.64.2:22
[2021-09-17T08:23:49.988] [info] [daemon] Cannot open ssh session on "ubuntu-lts" shutdown: ssh connection failed: 'Timeout connecting to 192.168.64.2'
```

Referring to some issues ([1447](https://github.com/canonical/multipass/issues/1447), [1929](https://github.com/canonical/multipass/issues/1929)), I learnt that the instance state might have corrupted when the host crashed last time. Restarting the multipass deamon fixed the problem.

```text
~ % ps -ef | egrep multipass
    0 35588     1   0  3:46PM ??         0:00.89 /Library/Application Support/com.canonical.multipass/bin/multipassd --verbosity debug
  501 35657 34642   0  3:49PM ttys000    0:00.00 egrep multipass
~ % sudo pkill multipassd
~ % ps -ef | egrep multipass
    0 35660     1   0  3:49PM ??         0:00.63 /Library/Application Support/com.canonical.multipass/bin/multipassd --verbosity debug
  501 35665 34642   0  3:50PM ttys000    0:00.00 egrep multipass

~ % multipass start
Starting ubuntu-lts |

~ % multipass ls
Name                    State             IPv4             Image
ubuntu-lts              Running           192.168.64.2     Ubuntu 20.04 LTS
~ %
```
