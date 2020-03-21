---
title: Some notes on filesystems - part 2
categories:
    - Tech
tags:
    - filesystems
    - linux
---

Outline

- A summary from last post. A one or tow liner description about each filesystem that I posted in the last update
  - autofs
  - cgroupfs
  - devpts
  - ramfs
  - rootfs
  - tmpfs
- what is going to be covered in this post?
- overlayfs
- mqueuefs
- squashfs
- end summary

## Todo

- [ ] Refine overlayfs notes
- [ ] Add code to the sample mqueuefs application and add a link here

## overlayfs

As the name implies, this file system overlays one file system on top of other and provides a unified view at a new mount point.  So we have two file systems here: one is referred as **lowerdir** and other one is referrred as **upperdir**. In practice, the lower and upper can be two different file systems or different directories on the same file system.

Why do we even this type of merged file system?

When we combine two file system and if both are allowed to be modified, we don't benefit much other than getting a unified view. By keeping the lower file system as read-only and the upper file system as writable, it serves in variety of use cases that aren't possible when the file systems are maintained separately. This of course comes with its own challenges. Merging the **lowerdir** and **upperdir** into a **merged** directory may run into conflicts if a file or directory exists in both lower and upper directories under the same identity. If the conflict is with a directory, then the contents of the two directories will be merged into one in the unified layout. If the conflict is with a file, then the file in the upper directory will be used.

In addition to lower, upper and merged options, overlay requires us a **workdir** which acts as a scratch space for the operating system to provide the functionality of overlayfs.

Here is a simple example demonstrating the mounting process of a overlay file system.

```text
# listing the lower and upper directories

overlay_ex $ ls lower/ upper/
lower/:
common.txt  lower.txt

upper/:
common.txt  upper.txt

# mounting the lower and upper directory into a unified one

overlay_ex $ sudo mount -t overlay -o \
> lowerdir=./lower,\
> upperdir=./upper,\
> workdir=./work \
> overlayfs_ex ./merged

overlay_ex $ mount | grep overlayfs_ex
overlayfs_ex on /home/deepan_seeralan/overlay_ex/merged type overlay (rw,relatime,lowerdir=./lower,upperdir=./upper,workdir=./work)

overlay_ex $ tree .
.
├── lower
│   ├── common.txt
│   └── lower.txt
├── merged
│   ├── common.txt
│   ├── lower.txt
│   └── upper.txt
├── upper
│   ├── common.txt
│   └── upper.txt
└── work
    └── work [error opening dir]
```

Renaming a file common to both lower/ and upper/ applies the changes only to upper/, leaving lower/ undisturbed.

```text
merged $ mv common.txt common_renamed.txt
merged $ tree ../
../
├── lower
│   ├── common.txt
│   └── lower.txt
├── merged
│   ├── common_renamed.txt
│   ├── lower.txt
│   └── upper.txt
├── upper
│   ├── common_renamed.txt
│   ├── common.txt
│   └── upper.txt
└── work
    └── work [error opening dir]

5 directories, 8 files
merged $ ls -l ../upper/
total 8
-rw-r--r-- 1 deepan_seeralan deepan_seeralan   24 Feb 28 18:02 common_renamed.txt
c--------- 1 root            root            0, 0 Feb 28 18:13 common.txt
-rw-r--r-- 1 deepan_seeralan deepan_seeralan   24 Feb 28 18:01 upper.txt

```

When deleting a file in an overlay filesystem, the behavior depends on the file's existence in the lower and upper directories. If a file exists only in the upperdir, the deletion process is as usual. If a file exists in both lowerdir and upperdir, a character device called **whiteout** file is created in the upper directory to denote that file is removed only from the upper file system. The file in lowerdir is still preserved as it is read-only. **Is the same applicable to directories as well?**

Where is it applicable?

One use case is to implement copy-on-write like functionality where reads can be served from the lower directory until a modification comes in. When file contents (and in some cases metadata too) need to be changed, the file needing the change will be first copied from the lower filesystem into the upper filesystem. Any changes will be applied only to the copy created in the upper file system. There is a downside to this approach too. Because of this copy operation, it may take a long time if the file size is large. So application has to be aware of modifying large files when backed by a overlay file system and designed to take steps accordingly.

A very common and more prevalent use case of overlay fs is in the container world.  When running containers, many containers often run in the same host. Having a separate image for each container will be too much space wastage.  Also, images are generally read only files. Makes it easier and space effective to share. **Needs rephrasing**. Runtime will create upper mount where changes made by the container will be applied and retained during the lifetime of the container. I think the runtime exposes only the merged directory to the container.

When running multiple containers of a same image, Docker creates a overlay filesystem for each container that uses the base image as the lower directory and a writable directory to save any changes to base image temporarily. This avoid unnecessary copy of the base image thereby preserving space and also takes advantage of the kernel page cache in sharing the base image pages. - Is that true?

The lower directory (and upper too?) can be another overlay fs too. How many layers are supported?

Some examples from docker.

## squashfs

Squashfs is a compressed read-only filesystem mostly used in space constrained environments (such as embedded,IOT) and in cases where files are accessed only for reads (e.g. archives). Since filesystem blocks have to be uncompressed before serving the reads, Squashfs lags in performance when compared to regular filesystems. There are some optimizations built in the filesystem implementation to improve the caching and thereby reducing the uncompress requests. The read-only nature of this filesystem makes this a suitable candidate to the lower layer of Overlayfs.

There are number of places where Squashfs is under use. Squashfs was also [used in Android](https://source.android.com/devices/architecture/kernel/squashfs) until kernel version 4.14. [Snap, the package manager](https://snapcraft.io/docs/snap-format) for Ubuntu also uses Squashfs to mount the application files in a readonly filesystem for each app. SDKs like aws-cli, google-cloud also uses this fileystem on linux distributions to install their CLI and related functionalities.

Here is a snippet from my Ubuntu VM running inside GCP.

```text
~ $ snap list
Name              Version    Rev   Tracking  Publisher          Notes
core              16-2.43.3  8689  stable    canonical✓         core
google-cloud-sdk  284.0.0    121   stable/…  google-cloud-sdk✓  classic
```

The compressed snap files are stored in `/var/lib/snapd/snaps` and are then mounted at `/snap/<snap-name>/<version>/` using a loopback device for every snap file. In my VM, I had only two package installed, each having two different versions.

```text
~ $ cat /snap/README

This directory presents installed snap packages.

It has the following structure:

/snap/bin                   - Symlinks to snap applications.
/snap/<snapname>/<revision> - Mountpoint for snap content.
/snap/<snapname>/current    - Symlink to current revision, if enabled.

DISK SPACE USAGE

The disk space consumed by the content under this directory is
minimal as the real snap content never leaves the .snap file.
Snaps are *mounted* rather than unpacked.

For further details please visit
https://forum.snapcraft.io/t/the-snap-directory/2817

~ $ ls /var/lib/snapd/
apparmor    auto-import  desktop  environment  firstboot  mount    seed      snaps       system-key
assertions  cookie       device   features     lib        seccomp  sequence  state.json  void
~ $ ls /var/lib/snapd/snaps
core_8592.snap  core_8689.snap  google-cloud-sdk_120.snap  google-cloud-sdk_121.snap  partial
```

Lets see where they are mounted. The default mount point is `/snap/<snap-name>/<version>/`.

```text
~ $ lsblk
NAME    MAJ:MIN RM  SIZE RO TYPE MOUNTPOINT
loop0     7:0    0 91.3M  1 loop /snap/core/8592
loop2     7:2    0 91.4M  1 loop /snap/core/8689
loop3     7:3    0 91.4M  1 loop /snap/google-cloud-sdk/119
loop4     7:4    0 91.5M  1 loop /snap/google-cloud-sdk/120
sda       8:0    0   10G  0 disk
├─sda1    8:1    0  9.9G  0 part /
├─sda14   8:14   0    4M  0 part
└─sda15   8:15   0  106M  0 part /boot/efi

~ $ mount | grep squashfs
/var/lib/snapd/snaps/google-cloud-sdk_120.snap on /snap/google-cloud-sdk/120 type squashfs (ro,nodev,relatime,x-gdu.hide)
/var/lib/snapd/snaps/google-cloud-sdk_121.snap on /snap/google-cloud-sdk/121 type squashfs (ro,nodev,relatime,x-gdu.hide)
/var/lib/snapd/snaps/core_8592.snap on /snap/core/8592 type squashfs (ro,nodev,relatime,x-gdu.hide)
/var/lib/snapd/snaps/core_8689.snap on /snap/core/8689 type squashfs (ro,nodev,relatime,x-gdu.hide)

~ $ ls /snap/google-cloud-sdk/121/
LICENSE        bin                     completion.bash.inc  etc          lib            path.zsh.inc  usr
README         command-bq.wrapper      completion.zsh.inc   help         meta           platform
RELEASE_NOTES  command-gcloud.wrapper  data                 install.bat  path.bash.inc  properties
VERSION        command-gsutil.wrapper  deb                  install.sh   path.fish.inc  rpm

~ $ ls /snap/google-cloud-sdk/121/
LICENSE        bin                     completion.bash.inc  etc          lib            path.zsh.inc  usr
README         command-bq.wrapper      completion.zsh.inc   help         meta           platform
RELEASE_NOTES  command-gcloud.wrapper  data                 install.bat  path.bash.inc  properties
VERSION        command-gsutil.wrapper  deb                  install.sh   path.fish.inc  rpm
```

## mqueuefs

This file system is used by **POSIX message queues** to provide a view of the message queues in the system. POSIX message queues provide a means for the processes to communicate through data exchange. A quick overview of the message queues can be seen [here](https://linux.die.net/man/7/mq_overview). The message queue operations are handled through the system calls  (e.g. **mq_open, mq_send, mq_receive, mq_close** etc.) in general. The file system interface for message queues provides a way to get a basic listing and some stats of the message queues. It also supports creation and deletion through the FS interface, although it is generally discouraged.

```text
~ $ mount | grep mqueue
mqueue on /dev/mqueue type mqueue (rw,relatime)
~ $ ls -l /dev/mqueue/
total 0
```

I started a sample application to demo the usage of message queues and then access the mqueuefs mount point as below. Reading the file in mqueuefs mount point shows some stats about the message queue.

```text
~ $ ls /dev/mqueue/
app-health_checker  app-notifier

~ $ cat /dev/mqueue/app-notifier
QSIZE:32         NOTIFY:0     SIGNO:0     NOTIFY_PID:0
```

We can also create and delete message queues through this interface itself (not recommended for actual usage though). Creating a new file in the mqueuefs mountpoint will create a message queue internally. Likewise, message queue can be removed with `rm` command too.

```text
~ $ ls /dev/mqueue/
app-health_checker
~ $ touch /dev/mqueue/new-queue
~ $ cat !$
cat /dev/mqueue/new-queue
QSIZE:0          NOTIFY:0     SIGNO:0     NOTIFY_PID:0
~ $ rm !$
rm /dev/mqueue/new-queue
rm: remove regular file '/dev/mqueue/new-queue'? y
```

## Summary

## References

- [Julia Evans Blog](https://jvns.ca/blog/2019/11/18/how-containers-work--overlayfs/)
- [Overlay driver in Docker](https://docs.docker.com/storage/storagedriver/overlayfs-driver/)
- [WindSock](https://windsock.io/the-overlay-filesystem/)
- [Data light](https://www.datalight.com/blog/2016/01/27/explaining-overlayfs-%E2%80%93-what-it-does-and-how-it-works/)
- [Overlayfs kernel docs](https://www.kernel.org/doc/Documentation/filesystems/overlayfs.txt)
- [tdlp docs on Squashfs](https://tldp.org/HOWTO/SquashFS-HOWTO/index.html)
- [Squashfs kernel docs](https://www.kernel.org/doc/Documentation/filesystems/squashfs.txt)
- [Squashfs in Android](https://source.android.com/devices/architecture/kernel/squashfs)
- [Squashfs in Snap](https://snapcraft.io/docs/snap-format)
- [Soft Prayog](https://www.softprayog.in/programming/interprocess-communication-using-posix-message-queues-in-linux)
