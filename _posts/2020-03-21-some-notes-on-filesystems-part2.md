---
title: Some notes on filesystems - part 2
toc: true
categories:
    - Tech
tags:
    - filesystems
    - linux
---

This is in continuation of my [previous post on filesystems](https://deepns.github.io/tech/some-notes-on-filesystems/). The last post briefly covered the following filesystems.

- autofs - file systems mounted on demand and unmounted automatically after the expiry window
- cgroupfs - a virtual filesystem to manage operations in Linux cgroups
- devpts - a virtual filesystem to manage pseudo terminal devices
- devtmpfs - a filesystem interface to access the system devices
- ramfs - a non-persistent filesystem backed by the physical memory
- tmpfs - similar to ramfs, but with better and finer controls over resource usage

This post will cover some basics of **overlayfs**, **squashfs** and **mqueuefs** filesystems.

## overlayfs

As the name implies, this file system overlays one file system on top of other and provides a unified view at a new mount point.  So we have two filesystems here: one is referred as **lowerdir** and other one is referrred as **upperdir**. These two are combined into a new mountpoint that shows the **merged** view. In practice, the lower and upper can be two different file systems or different directories on the same file system. In addition to lower, upper and merged options, overlayfs requires us a **workdir** which acts as a scratch space for the operating system to provide the functionality of overlayfs.

### Why do we need this type of merged file system

When we combine two file system and if both are allowed to be modified, we don't benefit much other than getting a unified view. By keeping the lower file system as read-only and the upper file system as writable, it serves in variety of use cases (e.g. making container images, copy-on-write operations etc.) that aren't possible when the file systems are maintained separately. In advanced use cases, overlay filesystems can be stacked too. Multiple directories can be combined in the lowerdir (stacked from right to left in the order of specification in mount options). The lowerdir can be another overlayfs mountpoint as well.

### How merge conflicts are resolved

Merging the **lowerdir** and **upperdir** into a **merged** directory may run into conflicts if a file or directory exists in both lower and upper directories under the same identity. If the conflict is with a directory that exists in both the file systems, then the contents of the two directories will be merged into one in the unified layout. If the conflict is with a file, then the file in the upper directory will be used in the unified view.

### Overlayfs example

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

When renaming a file which is common to both lower/ and upper/, it is applied only to the file in upper/, leaving lower/ undisturbed.

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

When deleting a file in an overlay filesystem, the behavior depends on the file's existence in the lower and upper directories. If a file exists only in the upperdir, the deletion process is as usual. If a file exists in both lowerdir and upperdir, a character device called **whiteout** file is created in the upper directory to denote that file is removed only from the upper file system. The file in lowerdir is still preserved as it is read-only. This applies to directories as well.

### Overlayfs in practice

One use case is to implement copy-on-write like functionality where reads can be served from the lower directory until a modification comes in. When file contents (and in some cases metadata too) need to be changed, the file needing the change will be first copied from the lower filesystem into the upper filesystem. Any changes will be applied only to the copy created in the upper file system. There is a downside to this approach too. Because of this copy operation, it may take a long time if the file size is large. So application has to be vigilant about modifying large files that are backed by a overlay file system and designed to take steps accordingly.

A very common and more prevalent use case of overlayfs is in the container world. Creating a new image file for every instance of a container will be eat up too much space on the host system. Also, container images are generally read only files. Any modification that happen within the container filesystem during the lifetime of the container doesn't persist when the container dies. Containers will have to save the changes elsewhere in a persistent storage like a disk, cloud volume, networked block device, network file system etc. Container images makes a perfect fit for the overlay filesystem. A read-only container image can be shared across many containers by using the image as a lowerdir in the overlayfs with a writable layer on top for each container to apply the temporary changes. This avoids unnecessary copy of the base image thereby preserving space and persumably takes advantage of the kernel page cache in sharing the base image pages. Docker now by default uses the Overlay2 storage driver which is more performant and efficient than the old overlay storage driver. I found the Docker docs pages ([this](https://docs.docker.com/storage/storagedriver/) and [this](https://docs.docker.com/storage/storagedriver/overlayfs-driver/#how-the-overlay2-driver-works)) to be super informative.

A small snippet here to show the overlayfs at work. I pulled the alpine and ubuntu images from docker repository and inspected it. **docker inspect** shows how the image layers are laid out in the Overlay2 filesystem. Alpine linux had only one layer, whereas Ubuntu image had 4 layers.

```text
~ $ sudo docker pull alpine
Using default tag: latest
latest: Pulling from library/alpine
aad63a933944: Pull complete
Digest: sha256:b276d875eeed9c7d3f1cfa7edb06b22ed22b14219a7d67c52c56612330348239
Status: Downloaded newer image for alpine:latest
docker.io/library/alpine:latest

~ $ sudo docker inspect alpine
[
    {
        "Id": "sha256:a187dde48cd289ac374ad8539930628314bc581a481cdb41409c9289419ddb72",
        "RepoTags": [
            "alpine:latest"
        ],
.
.
        "Architecture": "amd64",
        "Os": "linux",
        "Size": 5595566,
        "VirtualSize": 5595566,
        "GraphDriver": {
            "Data": {
                "MergedDir": "/var/lib/docker/overlay2/ab694ac9ea07190315eeb0ce815f409994f4414aa656b9875e3db65bd053e37d/merged",
                "UpperDir": "/var/lib/docker/overlay2/ab694ac9ea07190315eeb0ce815f409994f4414aa656b9875e3db65bd053e37d/diff",
                "WorkDir": "/var/lib/docker/overlay2/ab694ac9ea07190315eeb0ce815f409994f4414aa656b9875e3db65bd053e37d/work"
            },
            "Name": "overlay2"
        },
.
.
]

~ $ sudo ls /var/lib/docker/overlay2/ab694ac9ea07190315eeb0ce815f409994f4414aa656b9875e3db65bd053e37d
diff  link
~ $ sudo ls /var/lib/docker/overlay2/ab694ac9ea07190315eeb0ce815f409994f4414aa656b9875e3db65bd053e37d/diff
bin  dev  etc  home  lib  media  mnt  opt  proc  root  run  sbin  srv  sys  tmp  usr  var
```

Pulling and inspecting the ubuntu image...

```text
~ $ sudo docker pull ubuntu
Using default tag: latest
latest: Pulling from library/ubuntu
5bed26d33875: Pull complete
f11b29a9c730: Pull complete
930bda195c84: Pull complete
78bf9a5ad49e: Pull complete
Digest: sha256:bec5a2727be7fff3d308193cfde3491f8fba1a2ba392b7546b43a051853a341d
Status: Downloaded newer image for ubuntu:latest
docker.io/library/ubuntu:latest

~ $ sudo docker inspect ubuntu
[
    {
        "Id": "sha256:4e5021d210f65ebe915670c7089120120bc0a303b90208592851708c1b8c04bd",
        "RepoTags": [
            "ubuntu:latest"
        ],
        "RepoDigests": [
            "ubuntu@sha256:bec5a2727be7fff3d308193cfde3491f8fba1a2ba392b7546b43a051853a341d"
        ],
.
.
        "Architecture": "amd64",
        "Os": "linux",
        "Size": 64205678,
        "VirtualSize": 64205678,
        "GraphDriver": {
            "Data": {
                "LowerDir": "/var/lib/docker/overlay2/4ca0a2a278b1d9fd4a25acb9ae8f51110fe2b3eb3dc47ff4be7045ae2ccc8395/diff:/var/lib/docker/overlay2/cd3cab1f606d0434b7cb3944e0563e6f6b8d0c5c41c83fc3551e7e06fac5c850/diff:/var/lib/docker/overlay2/68b95b72c04895a05d55675f7031a6ac1cfbcf76198b5ce6357aa99d75b8d76c/diff",
                "MergedDir": "/var/lib/docker/overlay2/5a8ab55da60c81d25c5c5dc5d05eda53fc62429687092c9d0e3dd9a779edd731/merged",
                "UpperDir": "/var/lib/docker/overlay2/5a8ab55da60c81d25c5c5dc5d05eda53fc62429687092c9d0e3dd9a779edd731/diff",
                "WorkDir": "/var/lib/docker/overlay2/5a8ab55da60c81d25c5c5dc5d05eda53fc62429687092c9d0e3dd9a779edd731/work"
            },
            "Name": "overlay2"
        },
.
.
]
```

The **LowerDir** of ubuntu image consists of three directories stacked, with the right most one being the lowest.

```text
# lowerdir 1
~ $ sudo ls /var/lib/docker/overlay2/68b95b72c04895a05d55675f7031a6ac1cfbcf76198b5ce6357aa99d75b8d76c/diff
bin  boot  dev  etc  home  lib  lib64  media  mnt  opt  proc  root  run  sbin  srv  sys  tmp  usr  var

# lowerdir 2
~ $ sudo ls /var/lib/docker/overlay2/cd3cab1f606d0434b7cb3944e0563e6f6b8d0c5c41c83fc3551e7e06fac5c850/diff
var
~ $ sudo ls /var/lib/docker/overlay2/cd3cab1f606d0434b7cb3944e0563e6f6b8d0c5c41c83fc3551e7e06fac5c850/diff/var
cache
sudo ls /var/lib/docker/overlay2/cd3cab1f606d0434b7cb3944e0563e6f6b8d0c5c41c83fc3551e7e06fac5c850/diff/var/cache/apt
pkgcache.bin  srcpkgcache.bin

# lowerdir 3
~ $ sudo ls /var/lib/docker/overlay2/4ca0a2a278b1d9fd4a25acb9ae8f51110fe2b3eb3dc47ff4be7045ae2ccc8395/diff
etc  sbin  usr  var
```

## squashfs

Squashfs is a compressed read-only filesystem mostly used in space constrained environments (such as embedded,IOT) and in cases where files are accessed only for reads (e.g. archives). Since filesystem blocks have to be uncompressed before serving the reads, Squashfs lags in performance when compared to regular filesystems. There are some optimizations built in the filesystem implementation to improve the caching and thereby reducing the uncompress requests. The read-only nature of this filesystem makes this a suitable candidate to the lower layer of Overlayfs.

There are number of places where Squashfs is under use. Squashfs was also [used in Android](https://source.android.com/devices/architecture/kernel/squashfs) until kernel version 4.14. [Snap, the package manager](https://snapcraft.io/docs/snap-format) for Ubuntu also uses Squashfs to mount the application files in a readonly filesystem for each app. SDKs like aws-cli, google-cloud also uses this fileystem on linux distributions to install their CLI and related functionalities.

### squashfs in practice

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

## References

Some reference articles that were of great help to me in understanding the filesystems discussed above. Many thanks to the contributors.

- [Julia Evans Blog](https://jvns.ca/blog/2019/11/18/how-containers-work--overlayfs/)
- [Overlay driver in Docker](https://docs.docker.com/storage/storagedriver/overlayfs-driver/)
- [WindSock](https://windsock.io/the-overlay-filesystem/)
- [Overlayfs kernel docs](https://www.kernel.org/doc/Documentation/filesystems/overlayfs.txt)
- [tdlp docs on Squashfs](https://tldp.org/HOWTO/SquashFS-HOWTO/index.html)
- [Squashfs kernel docs](https://www.kernel.org/doc/Documentation/filesystems/squashfs.txt)
- [Squashfs in Android](https://source.android.com/devices/architecture/kernel/squashfs)
- [Squashfs in Snap](https://snapcraft.io/docs/snap-format)
- [Soft Prayog](https://www.softprayog.in/programming/interprocess-communication-using-posix-message-queues-in-linux)
