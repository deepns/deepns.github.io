---
title: Running Ubuntu VM with multipass
toc: true
categories:
    - Tech
tags:
    - linux
    - programming
    - ubuntu
---

While working on a sample C application on my mac, I wanted to run it on a Linux box for some comparisons and portability checks. I usually spin up a Linux instance of desired distribution in GCP to run these type of checks. It worked great as my requirements are mostly ephemeral so I don't care to keep the VM running forever and don't plan to keep anything persistent. It cost just a few dollars a month based on the usage. I stayed from running a full fledged VM through hypervisors like Virtual Box for quite sometime. I just wanted the desired linux environment for my experiments and not a full fledged machine with all bells and whistles.

I stumbled upon [Multipass](https://multipass.run/) while looking for solutions that can offer cloud like experience on my local machine. Multipass perfectly fit my needs. It is supported on all major platforms (Windows, Linux and macOS)

I downloaded the multipass application from [here](https://multipass.run/) and spun up an Ubuntu VM in just a few minutes.

## Launching a Ubuntu VM

It starts with finding the image we want to run.

```text
~ % multipass --help
Usage: multipass [options] <command>
Create, control and connect to Ubuntu instances.

This is a command line utility for multipass, a
service that manages Ubuntu instances.

Options:
  -h, --help     Display this help
  -v, --verbose  Increase logging verbosity. Repeat the 'v' in the short option
                 for more detail. Maximum verbosity is obtained with 4 (or more)
                 v's, i.e. -vvvv.

Available commands:
  delete    Delete instances
  exec      Run a command on an instance
  find      Display available images to create instances from
  get       Get a configuration setting
  help      Display help about a command
  info      Display information about instances
  launch    Create and start an Ubuntu instance
  list      List all available instances
  mount     Mount a local directory in the instance
  purge     Purge all deleted instances permanently
  recover   Recover deleted instances
  restart   Restart instances
  set       Set a configuration setting
  shell     Open a shell on a running instance
  start     Start instances
  stop      Stop running instances
  suspend   Suspend running instances
  transfer  Transfer files between the host and instances
  umount    Unmount a directory from an instance
  version   Show version details

~ % multipass find
Image                       Aliases           Version          Description
snapcraft:core              core16            20200814         Snapcraft builder for Core 16
snapcraft:core18                              20200806         Snapcraft builder for Core 18
snapcraft:core20                              20200730         Snapcraft builder for Core 20
16.04                       xenial            20200814         Ubuntu 16.04 LTS
18.04                       bionic            20200807         Ubuntu 18.04 LTS
20.04                       focal,lts         20200804         Ubuntu 20.04 LTS
```

New VMs can be created with the `launch` command. It pulls the lts image by default unless the image is explicitly specified. When an image is pulled for the first time, it takes few minutes (depending on the download speed) to download the image. Subsequent invocations of launch command launches new VMs in few seconds.

```text
~ % multipass launch --name ubuntu-demo
Launched: ubuntu-demo

~ % multipass info ubuntu-demo
Name:           ubuntu-demo
State:          Running
IPv4:           192.168.64.4
Release:        Ubuntu 20.04.1 LTS
Image hash:     896d13fcadd1 (Ubuntu 20.04 LTS)
Load:           0.33 0.33 0.14
Disk usage:     1.2G out of 4.7G
Memory usage:   134.9M out of 981.4M
```

By default, VMs are launched with **1 vCPU, 1G memory and 5G of disk space**. These parameters can be customized with appropriate options to `launch` command.

## Connecting to VM

We can open a shell prompt on the running VM with `shell` subcommand.

```text
~ % multipass shell ubuntu-demo
Welcome to Ubuntu 20.04.1 LTS (GNU/Linux 5.4.0-42-generic x86_64)

 * Documentation:  https://help.ubuntu.com
 * Management:     https://landscape.canonical.com
 * Support:        https://ubuntu.com/advantage

  System information as of Tue Aug 18 00:22:52 EDT 2020

  System load:  0.18              Processes:               114
  Usage of /:   26.6% of 4.67GB   Users logged in:         0
  Memory usage: 18%               IPv4 address for enp0s2: 192.168.64.4
  Swap usage:   0%


1 update can be installed immediately.
0 of these updates are security updates.
To see these additional updates run: apt list --upgradable


The list of available updates is more than a week old.
To check for new updates run: sudo apt update

To run a command as administrator (user "root"), use "sudo <command>".
See "man sudo_root" for details.

ubuntu@ubuntu-demo:~$ uname -a
Linux ubuntu-demo 5.4.0-42-generic #46-Ubuntu SMP Fri Jul 10 00:24:02 UTC 2020 x86_64 x86_64 x86_64 GNU/Linux
```

> multipass allows a vm to be configured as `primary` for quick operations with certain commands. Primary VM is also configured with user's home directory mounted inside the VM's home automatically when it is launched.

Directories on the host can be individually mounted into the VM with the `mount` subcommand.

```text
src % multipass mount shm_posix ubuntu-demo:/home/ubuntu/mount_sample
src % multipass info ubuntu-demo
Name:           ubuntu-demo
State:          Running
IPv4:           192.168.64.4
Release:        Ubuntu 20.04.1 LTS
Image hash:     896d13fcadd1 (Ubuntu 20.04 LTS)
Load:           0.10 0.07 0.07
Disk usage:     1.2G out of 4.7G
Memory usage:   149.4M out of 981.4M
Mounts:         /Users/deepan/src/shm_posix => /home/ubuntu/mount_sample
                    UID map: 501:default
                    GID map: 20:default
```

Once we get inside the shell, we can work just the way with any other ubuntu machine. In addition to the `shell` command, we can interact with the VM through `exec` too. The given command is run inside the VM and the output is redirected to the standard output on the host.

```text
~ % multipass exec ubuntu-demo -- uname -a
Linux ubuntu-lts 5.4.0-42-generic #46-Ubuntu SMP Fri Jul 10 00:24:02 UTC 2020 x86_64 x86_64 x86_64 GNU/Linux
~ % multipass exec ubuntu-demo -- grep ubuntu /etc/passwd
ubuntu:x:1000:1000:Ubuntu:/home/ubuntu:/bin/bash
```

## Cleaning up

It is super simple to delete existing instances and create a new one.

```text
~ % multipass list
Name                    State             IPv4             Image
ubuntu-lts              Running           192.168.64.2     Ubuntu 20.04 LTS
ubuntu-demo             Running           192.168.64.4     Ubuntu 20.04 LTS
~ % multipass stop ubuntu-demo
~ % multipass list
Name                    State             IPv4             Image
ubuntu-lts              Running           192.168.64.2     Ubuntu 20.04 LTS
ubuntu-demo             Stopped           --               Ubuntu 20.04 LTS
~ % multipass delete ubuntu-demo
~ % multipass list
Name                    State             IPv4             Image
ubuntu-lts              Running           192.168.64.2     Ubuntu 20.04 LTS
ubuntu-demo             Deleted           --               Not Available
~ % multipass purge
~ % multipass list
Name                    State             IPv4             Image
ubuntu-lts              Running           192.168.64.2     Ubuntu 20.04 LTS
```

Commands like `start`,`stop`,`suspend` and `shell` operate on the primary VM if no VM is specified to the command. The default name of the primary VM is `primary`. That can be changed using `multipass set client.primary-name`.

```text
~ % multipass get client.primary-name
primary
~ % multipass set client.primary-name=ubuntu-lts
~ % multipass get client.primary-name
ubuntu-lts
```

Additionally, multipass also supports [cloud-init](https://cloud-init.io/) too, so we can initialize the VMs with configs specified in a yaml file.

I wanted a VM to be initialized with `gcc` and `make`, so specified that list of packages in a yaml following the [cloud-init examples](https://cloudinit.readthedocs.io/en/latest/topics/examples.html).

```yaml
#cloud-config

# Install additional packages on first boot
#
# Default: none
#
# if packages are specified, this apt_update will be set to true
#
# packages may be supplied as a single package name or as a list
# with the format [<package>, <version>] wherein the specifc
# package version will be installed.
packages:
    - gcc
    - make

final_message: "The system is finally up, after $UPTIME seconds"
```

Launch the VM with `--cloud-init` set to the cloud-init config file.

```text
~ % multipass launch --name cc-test-vm --cloud-init cloud-config-packages.yaml
```

Checking the cloud-init log.

```text
~ % multipass list
Name                    State             IPv4             Image
ubuntu-lts              Running           192.168.64.2     Ubuntu 20.04 LTS
cc-test-vm              Running           192.168.64.5     Ubuntu 20.04 LTS

~ % multipass exec cc-test-vm -- tail /var/log/cloud-init-output.log
Setting up binutils-x86-64-linux-gnu (2.34-6ubuntu1) ...
Setting up binutils (2.34-6ubuntu1) ...
Setting up libgcc-9-dev:amd64 (9.3.0-10ubuntu2) ...
Setting up cpp (4:9.3.0-1ubuntu2) ...
Setting up gcc-9 (9.3.0-10ubuntu2) ...
Setting up gcc (4:9.3.0-1ubuntu2) ...
Processing triggers for man-db (2.9.1-1) ...
Processing triggers for libc-bin (2.31-0ubuntu9) ...
Cloud-init v. 20.2-45-g5f7825e2-0ubuntu1~20.04.1 running 'modules:final' at Wed, 19 Aug 2020 04:39:20 +0000. Up 44.34 seconds.
The system is finally up, after 99.14 seconds
```
