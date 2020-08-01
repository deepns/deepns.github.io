---
title: Exploring man page settings
categories:
    - Tech
tags:
    - programming
    - c
    - linux
---

When running `man` command, the pages are searched first in the path given by option `-M` if specified. If `-M` is not specified, then the path specified in `MANPATH` environment variable is looked up. If neither `-M` nor `MANPATH`is specified, then the path to man pages is inferred from the config file. In general, the default set of man pages live in `/usr/share/man/`, but applications can install in other paths too and update the `MANPATH` accordingly. The location of the config file can differ based on the distribution.

For e.g. in macOS Mojave, the man config file is at `/private/etc/man.conf`. Whereas in some distributions, it is in `/etc/man.config`.

Run `man man` to get more details regarding how these look ups are made.  [TLDP page](https://www.tldp.org/HOWTO/Man-Page/q2.html#targetText=On%20Linux%2C%20all%20man%20pages,the%20same%20format%20as%20PATH) goes in detail about this.

I was looking for man pages related to certain POSIX calls. I realized that POSIX man pages are not auto installed in some of the Linux distributions. On Ubuntu 18.04,  I manually installed them from `manpages-posix` and `manpages-posix-dev` packages.

```text
~ $ man mq_open
No manual entry for mq_open

~ $ sudo apt install manpages-posix manpages-posix-dev
Reading package lists... Done
Building dependency tree
Reading state information... Done
The following additional packages will be installed:
  manpages-dev
The following NEW packages will be installed:
  manpages-dev manpages-posix manpages-posix-dev
0 upgraded, 3 newly installed, 0 to remove and 6 not upgraded.
Need to get 4940 kB of archives.
After this operation, 7216 kB of additional disk space will be used.
Do you want to continue? [Y/n]

~ $ apt search manpages-posix
Sorting... Done
Full Text Search... Done
manpages-posix/bionic 2013a-2 all
  Manual pages about using POSIX system

manpages-posix-dev/bionic,now 2013a-2 all [residual-config]
  Manual pages about using a POSIX system for development

~ $ man -k mq_open
mq_open (2)          - open a message queue
mq_open (3)          - open a message queue
mq_open (3posix)     - open a message queue (REALTIME)
```

On Debian10, I couldn't find manpages-posix in the packages list. The man pages I was looking for showed up in `manpages-dev` though.

```text
~ $ cat /etc/debian_version
10.4
~ $ man mq_open
No manual entry for mq_open
~ $ man pthread_create
No manual entry for pthread_create
~ $ apt search manpages-posix
Sorting... Done
Full Text Search... Done
```

Installing `manpages-dev` from the repo, I was able to lookup the man pages of POSIX calls like `mq_open`, `mq_close`, `pthread_create` etc.

```text
~ $ sudo apt install manpages-posix manpages-posix-dev
Reading package lists... Done
Building dependency tree
Reading state information... Done
E: Unable to locate package manpages-posix
E: Unable to locate package manpages-posix-dev

~ $ sudo apt install manpages-dev
Reading package lists... Done
Building dependency tree
Reading state information... Done
The following NEW packages will be installed:
  manpages-dev
0 upgraded, 1 newly installed, 0 to remove and 1 not upgraded.
Need to get 2232 kB of archives.
After this operation, 3934 kB of additional disk space will be used.
Get:1 http://deb.debian.org/debian buster/main amd64 manpages-dev all 4.16-2 [2232 kB]
Fetched 2232 kB in 0s (12.9 MB/s)
Selecting previously unselected package manpages-dev.
(Reading database ... 35900 files and directories currently installed.)
Preparing to unpack .../manpages-dev_4.16-2_all.deb ...
Unpacking manpages-dev (4.16-2) ...
Setting up manpages-dev (4.16-2) ...
Processing triggers for man-db (2.8.5-2) ...

~ $ man -k mq_open
mq_open (2)          - open a message queue
mq_open (3)          - open a message queue

~ $ man -k pthread_create
pthread_create (3)   - create a new thread
```
