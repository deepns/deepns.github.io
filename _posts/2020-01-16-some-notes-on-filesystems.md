---
title: Some notes on filesystems
toc: true
category:
    - Tech
tags:
    - linux
    - filesystems
---

I was poking around the mount command on one day to mount a nfs remote on my local machine. I stumbled upon many other filesystems in the listed under `mount` command. Some of them were totally unknown to me. Each of them have different use cases and different characteristics on their own. I wanted to learn them at least at a high level so I know what file system is used when and for what purposes in the world of Unix and Unix like systems. I often use [Google Cloud Shell](https://cloud.google.com/shell/docs/how-cloud-shell-works) (which is a g1-small instance type VM based on Debian in GCP) for quick checks on Linux commands and features. It is an ephemeral instance, so contents stored in other than the home directory are lost upon deactivation. Also, it is free and automatically reclaimed after a period of inactivity, so I don't have to worry about billing or maintaining the instance.

In the list of mounted filesystems on this cloud shell instance, I could see 10 different filesytems.

```text
$ mount | grep -o "type [a-z,0-9].* "  | sort | uniq | nl
     1  type cgroup
     2  type devpts
     3  type ext4
     4  type mqueue
     5  type nsfs
     6  type overlay
     7  type proc
     8  type securityfs
     9  type sysfs
    10  type tmpfs
```

Looking into the list of file systems supported by this machine, there were about 28 of them. Only few of them require a block device as the backend (indicated by the absence of nodev).

```text
~ $ cat /proc/filesystems | sort -k 2 | nl
     1          ext2
     2          ext3
     3          ext4
     4  nodev   autofs
     5  nodev   bdev
     6  nodev   binfmt_misc
     7  nodev   bpf
     8  nodev   cgroup
     9  nodev   cgroup2
    10  nodev   cpuset
    11  nodev   dax
    12  nodev   debugfs
    13  nodev   devpts
    14  nodev   devtmpfs
    15  nodev   efivarfs
    16  nodev   hugetlbfs
    17  nodev   mqueue
    18  nodev   overlay
    19  nodev   pipefs
    20  nodev   proc
    21  nodev   pstore
    22  nodev   ramfs
    23  nodev   rootfs
    24  nodev   securityfs
    25  nodev   sockfs
    26  nodev   sysfs
    27  nodev   tmpfs
    28  nodev   tracefs
```

I'm trying to learn the basics of each of these filesytem and post a summary as I go along. It will be too long if I post all of them into one, so breaking down into 3 or 4 parts.

## autofs

Autofs is program/service used to mount file systems on demand. The typical use cases are to mount remote filesystems like NFS mounts and CIFS shares, mount removable media like USB, CD-Drive etc. The specified filesystem is auto mounted upon access and unmounted after a period of inactivity. The traditional approach is to specify all the necessary mounts in `/etc/fstab` so that the OS can mount them during the bootup. With remote filesystems, having an always-connected filesystem may incur significant network bandwidth. Autofs conserves the bandwidth by mounting the filesystems only when needed. The operations are controlled through the config and map files.

### autofs-references

- [Kernel Doc](https://www.kernel.org/doc/Documentation/filesystems/autofs.txt)
- [Autofs on Ubuntu](https://help.ubuntu.com/community/Autofs)
- [Autofs on Gentoo](https://wiki.gentoo.org/wiki/AutoFS)
- [A post on elinuxbook.com](http://elinuxbook.com/how-to-configure-autofs-automount-in-linux/)

## cgroup

This is a virtual filesystem, used by Linux [cgroups](https://www.kernel.org/doc/Documentation/cgroup-v1/cgroups.txt) kernel feature to manage cgroup operations. There is no cgroup specific system call. All cgroup actions are handled through operations on the files inside this virtual file system. In a typical configuration, a `tmpfs` filesystem is mounted at the top of cgroup hierarchy, usually at the path `/sys/fs/cgroup`. Each cgroup controller (e.g. memory, cpu, cpuset, blkio etc..) then has its own `cgroup` filesystem under this hierarchy. A new cgroup can be simply created by creating a directory under the desired controller (note: there are other ways too, mkdir is just one of them.). Kernel then automatically populates the directory with files specific to that controller.

A quick grep for cgroup in the list of mounted file system...can see that every cgroup controller has its own cgroup filesystem.

```text
~ $ grep "cgroup" /proc/mounts
tmpfs /sys/fs/cgroup tmpfs rw,nosuid,nodev,noexec,relatime,mode=755 0 0
cgroup /sys/fs/cgroup/systemd cgroup rw,nosuid,nodev,noexec,relatime,xattr,name=systemd 0 0
cgroup /sys/fs/cgroup/net_cls,net_prio cgroup rw,nosuid,nodev,noexec,relatime,net_cls,net_prio 0 0
cgroup /sys/fs/cgroup/hugetlb cgroup rw,nosuid,nodev,noexec,relatime,hugetlb 0 0
cgroup /sys/fs/cgroup/devices cgroup rw,nosuid,nodev,noexec,relatime,devices 0 0
cgroup /sys/fs/cgroup/cpuset cgroup rw,nosuid,nodev,noexec,relatime,cpuset 0 0
cgroup /sys/fs/cgroup/memory cgroup rw,nosuid,nodev,noexec,relatime,memory 0 0
cgroup /sys/fs/cgroup/pids cgroup rw,nosuid,nodev,noexec,relatime,pids 0 0
cgroup /sys/fs/cgroup/freezer cgroup rw,nosuid,nodev,noexec,relatime,freezer 0 0
cgroup /sys/fs/cgroup/cpu,cpuacct cgroup rw,nosuid,nodev,noexec,relatime,cpu,cpuacct 0 0
cgroup /sys/fs/cgroup/blkio cgroup rw,nosuid,nodev,noexec,relatime,blkio 0 0
cgroup /sys/fs/cgroup/perf_event cgroup rw,nosuid,nodev,noexec,relatime,perf_event 0 0
cgroup /sys/fs/cgroup/rdma cgroup rw,nosuid,nodev,noexec,relatime,rdma 0 0
```

The files inside each controller directory are the interfaces to the cgroup operations

```text
~ $ cd /sys/fs/cgroup/blkio/
blkio $ ls
blkio.io_merged            blkio.io_service_bytes            blkio.io_service_time            blkio.leaf_weight         blkio.sectors_recursive                    blkio.throttle.io_serviced_recursive  blkio.throttle.write_iops_device  blkio.weight_device    tasks
blkio.io_merged_recursive  blkio.io_service_bytes_recursive  blkio.io_service_time_recursive  blkio.leaf_weight_device  blkio.throttle.io_service_bytes            blkio.throttle.read_bps_device        blkio.time                        cgroup.clone_children
blkio.io_queued            blkio.io_serviced                 blkio.io_wait_time               blkio.reset_stats         blkio.throttle.io_service_bytes_recursive  blkio.throttle.read_iops_device       blkio.time_recursive              cgroup.procs
blkio.io_queued_recursive  blkio.io_serviced_recursive       blkio.io_wait_time_recursive     blkio.sectors             blkio.throttle.io_serviced                 blkio.throttle.write_bps_device       blkio.weight                      notify_on_release

~ $ cd /sys/fs/cgroup/memory/
memory $ ls
cgroup.clone_children  memory.force_empty              memory.kmem.slabinfo                memory.kmem.tcp.usage_in_bytes  memory.memsw.failcnt             memory.move_charge_at_immigrate  memory.soft_limit_in_bytes  memory.use_hierarchy
cgroup.event_control   memory.kmem.failcnt             memory.kmem.tcp.failcnt             memory.kmem.usage_in_bytes      memory.memsw.limit_in_bytes      memory.numa_stat                 memory.stat                 notify_on_release
cgroup.procs           memory.kmem.limit_in_bytes      memory.kmem.tcp.limit_in_bytes      memory.limit_in_bytes           memory.memsw.max_usage_in_bytes  memory.oom_control               memory.swappiness           tasks
memory.failcnt         memory.kmem.max_usage_in_bytes  memory.kmem.tcp.max_usage_in_bytes  memory.max_usage_in_bytes       memory.memsw.usage_in_bytes      memory.pressure_level            memory.usage_in_bytes
```

Say we want to create a new cgroup to limit the memory consumed by processes initiated by product-developers within a particular group. We can create a directory within `/sys/fs/cgroup/memory/` first, and then set the desired values in the corresponding files.

```text
memory $ sudo mkdir prod_devs
memory $ cd prod_devs/
prod_devs $ ls
cgroup.clone_children  memory.force_empty              memory.kmem.slabinfo                memory.kmem.tcp.usage_in_bytes  memory.memsw.failcnt             memory.move_charge_at_immigrate  memory.soft_limit_in_bytes  memory.use_hierarchy
cgroup.event_control   memory.kmem.failcnt             memory.kmem.tcp.failcnt             memory.kmem.usage_in_bytes      memory.memsw.limit_in_bytes      memory.numa_stat                 memory.stat                 notify_on_release
cgroup.procs           memory.kmem.limit_in_bytes      memory.kmem.tcp.limit_in_bytes      memory.limit_in_bytes           memory.memsw.max_usage_in_bytes  memory.oom_control               memory.swappiness           tasks
memory.failcnt         memory.kmem.max_usage_in_bytes  memory.kmem.tcp.max_usage_in_bytes  memory.max_usage_in_bytes       memory.memsw.usage_in_bytes      memory.pressure_level            memory.usage_in_bytes

memory $ echo 4G > /sys/fs/cgroup/memory/prod_devs/memory.limit_in_bytes

memory $ cat /sys/fs/cgroup/memory/prod_devs/memory.limit_in_bytes
4294967296

memory $ sudo rmdir prod_devs/
```

[cgroup version 2](https://www.kernel.org/doc/Documentation/cgroup-v2.txt) uses a unified hierarchy instead of having a separate file system for each controller. It uses the `cgroup2` filesystem. It is possible to have both version 1 and 2 running in the same system, although there are some restrictions on the interoperability. There is so much to learn about cgroups, its operations and applications in the container world. That will be an endless path, so stopping wth just a overview of the file system for now.

```text
~ $ grep "cgroup" /proc/mounts
tmpfs /sys/fs/cgroup tmpfs ro,nosuid,nodev,noexec,mode=755 0 0
cgroup /sys/fs/cgroup/unified cgroup2 rw,nosuid,nodev,noexec,relatime,nsdelegate 0 0
```

### cgroup-references

- [cgroups v1](https://www.kernel.org/doc/Documentation/cgroup-v1/cgroups.txt)
- [cgroups v1 memory](https://www.kernel.org/doc/Documentation/cgroup-v1/memory.txt)
- [cgroup man pages](http://man7.org/linux/man-pages/man7/cgroups.7.html)
- [Linux Journal](https://www.linuxjournal.com/content/everything-you-need-know-about-linux-containers-part-i-linux-control-groups-and-process)
- [Linux Journal part2](https://www.linuxjournal.com/content/everything-you-need-know-about-linux-containers-part-ii-working-linux-containers-lxc)

## devpts

`devpts` is a virtual filesystem used to manage the pseudo terminal devices, typically mounted at `/dev/pts`. It is mostly pseudo terminal that we deal with these days through applications like xterm, iterm etc that emulates a hardware terminal. Pseudo terminals work in a master-slave relationship. There used to individual master-slave pair for each pseudo-terminal. That has been replaced with a terminal mulitplexer (`/dev/ptsmx`) in the later releases. When a process (like xterm or any other terminal application) tries to open a new pseudo terminal, the multiplexes allocates a slave pseudo terminal in `/dev/pts/` and returns the file descriptor to the calling process. There is quite a bit of history in the development of pseudo terminals.

```text
~ $ mount -t devpts
devpts on /dev/pts type devpts (rw,nosuid,noexec,relatime,gid=5,mode=620,ptmxmode=000)

~ $ ls /dev/pts/
0  ptmx
~ $ tty
/dev/pts/0

~ $ #opening another terminal in another window.
~ $ ls /dev/pts/
0  1  ptmx

~ $ #send message to the new terminal
~ $ echo "hello, from pty0" >> /dev/pts/1

~ $ #sending a self message
~ $ echo "hello, from pty0" >> /dev/pts/0
hello, from pty0
```

### devpts-references

- [man page](http://man7.org/linux/man-pages/man4/pts.4.html)
- [wiki](https://en.wikipedia.org/wiki/Devpts)
- [stack overflow thread](https://unix.stackexchange.com/questions/93531/what-is-stored-in-dev-pts-files-and-can-we-open-them)

### devtmpfs

`devtmpfs` is an advancement over the now deprecated `devfs` filesystem. Both are meant for dynamic identification and management of system devices. devfs ran in kernel space and had some inherent issues that led to its deprecation over time. devfs is both a filesystem and a device manager. While devtmpfs takes care of the filesystem operations, `udev` takes care of the actual device management. udev deamon mounts the devtmpfs filesystem at `/dev/` during the boot (see `/etc/rc.d/udev` or `/etc/init.d/udev` if using init as init daemon). All devices visible to the system will have an entry in `/dev/`. New device nodes are created in the `devtmpfs` filesystem by the kernel and are notified to the udev daemon for additional processing based on udev rules.

```text
~ $ mount -t devtmpfs
udev on /dev type devtmpfs (rw,nosuid,relatime,size=1885344k,nr_inodes=471336,mode=755)

~ $ cd /dev
dev $ ls
autofs           disk       kmsg              network_latency     rtc       stdin   tty14  tty22  tty30  tty39  tty47  tty55  tty63  uinput   vcsa         vhci
block            fd         log               network_throughput  rtc0      stdout  tty15  tty23  tty31  tty4   tty48  tty56  tty7   urandom  vcsa1        vhost-net
bsg              full       loop-control      null                sda       tty     tty16  tty24  tty32  tty40  tty49  tty57  tty8   vcs      vcsa2        zero
btrfs-control    fuse       mapper            port                sda1      tty0    tty17  tty25  tty33  tty41  tty5   tty58  tty9   vcs1     vcsa3
char             hpet       mcelog            ppp                 sg0       tty1    tty18  tty26  tty34  tty42  tty50  tty59  ttyS0  vcs2     vcsa4
console          hugepages  mem               psaux               shm       tty10   tty19  tty27  tty35  tty43  tty51  tty6   ttyS1  vcs3     vcsa5
core             hwrng      memory_bandwidth  ptmx                snapshot  tty11   tty2   tty28  tty36  tty44  tty52  tty60  ttyS2  vcs4     vcsa6
cpu_dma_latency  initctl    mqueue            pts                 snd       tty12   tty20  tty29  tty37  tty45  tty53  tty61  ttyS3  vcs5     vfio
cuse             input      net               random              stderr    tty13   tty21  tty3   tty38  tty46  tty54  tty62  uhid   vcs6     vga_arbiter
dev $ ls /dev/block/
8:0  8:1
dev $ ls -l /dev/block/
total 0
lrwxrwxrwx 1 root root 6 Jan 16 21:29 8:0 -> ../sda
lrwxrwxrwx 1 root root 7 Jan 16 21:29 8:1 -> ../sda1
```

macOS seems to use `devfs` instead of `devtmpfs`. I need to find more on this.

```text
~ $ mount -t devtmpfs
~ $ mount -t devfs
devfs on /dev (devfs, local, nobrowse)
```

### devtmpfs-references

- [dev on tldp](http://www.tldp.org/LDP/Linux-Filesystem-Hierarchy/html/dev.html)
- [udev](http://www.linuxfromscratch.org/lfs/view/development/chapter07/udev.html)
- [sysfs and devtmpfs](https://unix.stackexchange.com/questions/236533/sysfs-and-devtmpfs)

## ramfs

[ramfs]((https://www.kernel.org/doc/Documentation/filesystems/ramfs-rootfs-initramfs.txt)) allows us to use the physical memory as the backend of a filesystem with the help of Linux page caching mechanism. Since the backend is a volatile storage, all contents stored in a ramfs will be lost after unmounting. All file read and write operations typically hit the page cache first (unless it is a direct I/O). For reads, data is returned from the cache if present. If not, data is read from the backing store (e.g. disk), cached and then returned. For writes, blocks are first written to the cache and marked dirty. Once the dirty blocks are flushed (i.e. written permanently) to the backing store, the corresponding dirty blocks are marked clean and kept in cache to serve future operations. Only the clean blocks are allowed to be freed when there is a need for eviction. Dirty blocks are never freed. When we write into a file on ramfs filesystem, the blocks in page cache are allocated as usual but are never marked clean because there is no backing store to flush to. Therefore one can grow a ramfs as big as the physical memory itself, at which point system will stop to respond as there is no memory left to operate. For such reasons, only root user is allowed to create a ramfs.

Prior to ramfs, a concept called `ramdisk` was used. ramdisk simulates a fake block device backed by the RAM. We can then install the desired filesystem (e.g. zfs) on top of the ramdisk. This is certainly expensive as there are lot of overheads and conflicts in managing the filesystem on top of the volatile block device.

Some of the shortcomings of ramfs are addressed in **tmpfs**.

## rootfs

rootfs is a special form of tmpfs (or ramfs if tmpfs is not available) that is always mounted and cannot be unmounted. It is mainly used in the system boot up and run the init process. The [kernel doc](https://www.kernel.org/doc/Documentation/filesystems/ramfs-rootfs-initramfs.txt) has only minimal explanation this. `rootfs` doesn't show up in `mount` or `df` output, which makes me wonder whether rootfs is hidden or just something else is used in place rootfs. I found few links ([so thread](https://unix.stackexchange.com/questions/479415/how-does-linux-know-where-the-rootfs-is), [so thread2](https://unix.stackexchange.com/questions/152029/why-is-there-no-rootfs-file-system-present-on-my-system)), but still not very clear about the answers.

## tmpfs

tmpfs was built on top of ramfs with the following additional capabilities:

- size limiting
- swap space usage

Because blocks written in a ramfs filesystem are never freed, we can keep writing to a ramfs until the full capacity is exhausted. tmpfs provides an option to limit the maximum size of the filesystem. The limit can be changed dynamically too. It also supports page swapping where the unneeded blocks are swapped out from the memory into the swap space backed by the persistent storage like disk. When those blocks are accessed later on, they are paged into the memory. This allows better memory management and finer controls for the applications making use of the memory for quick file based operations. When cache miss occurs in a tmpfs filesystem, blocks will have to be loaded from the swap space. That will incur disk I/O, so it is possible for a read/write op to a tmpfs filesystem to wait for disk I/O operation to complete. Like ramfs, the contents in tmpfs are volatile.

The size limit can be specified in terms of raw size in k/m/g units or % of the physical memory. The default behavior is to consume 50% of the memory if no size is specified.

### Mounting a tmpfs filesystem

The general syntax for the mount command is `mount [OPTIONS] DEVICE MOUNTPOINT`. The device identifier doesn't matter for tmpfs. In this case, the device identifier used is `appdata` and mount point is `/mnt/appdata`. The device identifier could be anything here. The mount point must exist though. I think the general convention is to use `tmpfs` as the device name when using a tmpfs filesystem. (e.g. `mount -t tmpfs -o size=10M tmpfs /mmt/mymountpoint`)

```text
~ $ sudo mkdir /mnt/appdata
~ $ sudo mount -t tmpfs -o size=100M appdata /mnt/appdata
~ $ df -h
Filesystem      Size  Used Avail Use% Mounted on
overlay          41G   34G  6.4G  85% /
tmpfs            64M     0   64M   0% /dev
tmpfs           847M     0  847M   0% /sys/fs/cgroup
/dev/sdb1       4.8G   13M  4.6G   1% /home
/dev/sda1        41G   34G  6.4G  85% /root
shm              64M     0   64M   0% /dev/shm
overlayfs       1.0M  164K  860K  17% /etc/ssh/ssh_host_dsa_key
overlayfs       1.0M  164K  860K  17% /etc/ssh/keys
tmpfs           847M  704K  846M   1% /run/metrics
tmpfs           847M     0  847M   0% /run/google/devshell
appdata         100M     0  100M   0% /mnt/appdata

~ $ mount -l -t tmpfs
tmpfs on /dev type tmpfs (rw,nosuid,size=65536k,mode=755)
tmpfs on /sys/fs/cgroup type tmpfs (rw,nosuid,nodev,noexec,relatime,mode=755)
shm on /dev/shm type tmpfs (rw,nosuid,nodev,noexec,relatime,size=65536k)
tmpfs on /run/metrics type tmpfs (rw,nosuid,nodev,mode=755)
tmpfs on /google/host/var/run type tmpfs (rw,nosuid,nodev,mode=755)
tmpfs on /run/google/devshell type tmpfs (rw,relatime)
appdata on /mnt/appdata type tmpfs (rw,relatime,size=102400k)
```

The space used by tmpfs mounts are counted towards shared memory consumption, thus they show up under **Shmem** in the output of `/proc/meminfo`
Lets create some dummy files in the tmpfs path and list the space consumption using `df -h` and `/proc/meminfo`

```text
~ $ df -h | grep appdata
appdata         100M     0  100M   0% /mnt/appdata
~ $ dd if=/dev/zero of=/mnt/appdata/dummy bs=1M count=50
50+0 records in
50+0 records out
52428800 bytes (52 MB, 50 MiB) copied, 0.0720446 s, 728 MB/s
~ $ df -h | grep appdata
appdata         100M   50M   50M  50% /mnt/appdata
~ $ grep -i "shmem" /proc/meminfo
Shmem:             52008 kB
ShmemHugePages:        0 kB
ShmemPmdMapped:        0 kB
~ $ dd if=/dev/zero of=/mnt/appdata/dummy1 bs=1M count=20
20+0 records in
20+0 records out
20971520 bytes (21 MB, 20 MiB) copied, 0.0129131 s, 1.6 GB/s
~ $ grep -i "shmem" /proc/meminfo
Shmem:             72488 kB
ShmemHugePages:        0 kB
ShmemPmdMapped:        0 kB
```

### ramfs-roots-tmpfs-references

- [Kernel Doc](https://www.kernel.org/doc/Documentation/filesystems/tmpfs.txt)
- [Linux Man Pages](http://man7.org/linux/man-pages/man5/tmpfs.5.html)
- [tmpfs paper](http://wiki.deimos.fr/images/1/1e/Solaris_tmpfs.pdf)
- [Difference between ramfs and tmpfs](https://www.jamescoyle.net/knowledge/951-the-difference-between-a-tmpfs-and-ramfs-ram-disk)

Many thanks to those who contributed in the reference pages. Those were immensely helpful. If you find some misunderstanding or misconception in the notes, please let me know.
