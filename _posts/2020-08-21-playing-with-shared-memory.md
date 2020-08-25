---
title: Playing with shared memory in Linux and macOS
categories:
    - Tech
tags:
    - programming
    - c
    - linux
    - macOS
---

Reading the operating system internals is like going down the rabbit hole. It is so easy start at one topic, get lost and end up in a totally different topic. On one such journey sometime back, I ended up at shared memory, one of the frequently used inter process communication mechanisms. If we are to communicate between parent and child processes, we could do so through a memory region in the parent's address space since that is accessible to the child process as well. Here is an example.

<script src="https://gist.github.com/deepns/dc4b80615cda94f0956d3b435c5282a9.js"></script>

Running this program will show an output similar to the one below. Since the physical page backed by the address returned by mmap is set to be shared, changes made by the child process is visible in the parent process as well.

```text
% ./mmap_parent_child.exe
(child) Writing data=10 at addr=0x10691a000
(parent) Reading from addr=0x10691a000 returned data=10
```

However, if we have to communicate between distinct process through memory, we can't do so with the above method since the address space will be different. There comes the concept of [Shared Memory](https://en.wikipedia.org/wiki/Shared_memory). The two most common IPC standards

1. System V IPC
2. POSIX IPC

support shared memory, along with message queues and semaphores. The two standards offer the similar functionalities, with the latter being relatively new but more portable. The implementations of System V and POSIX in macOS and Linux tend to be quite different though. For e.g. default size of shmem segments in macOS is only 4MB, macOS supports POSIX shared memory but not message queues etc. There are some more differences I noticed while running the sample code of the two interfaces in Linux and macOS.

## System V

The general flow in accessing shared memory segments using System V IPC goes like this:

```c
// Create a key of type key_t
// Can convert an int to key_t or better if we use ftok()
key_t shm_key = ftok("some_file", 0);

// Create/Open the shared memory segment of required size(specified in bytes) and permissions
int shm_id = shmget(shm_key, 4096, IPC_CREAT | SHM_R | SHM_W);

// Map the shared memory to the virtual memory.
void *shm_addr = shmat(shm_id, NULL, 0);

// Read and/or write from/to the virtual memory which backs the physical pages of the shared memory
// In real world use cases, we have to synchronize the read/write operations to the shared memory
// segments with semaphores.

// Unmap the virtual memory backing the shared memory
shmdt(shm_addr);

// Schedule removal of the shared memory
// Deletion will happen after all the processes attached to the shared memory are detached.
shmctl(shm_id, IPC_RMID, NULL);
```

The System V interfaces to manage shared memory are defined in `<sys/shm.h>`. The above snippet is just to show the calls involved in accessing the System V shared memory. For a proper example with working code, see [here](https://github.com/deepns/fun-with-shared-memory).

The command interfaces to read or manage the segments vary significantly. Listing my observations in the below sections.

### Similarities

- `ipcs` command lists information about the three IPC objects(shared memory, semaphores and message queues)

In Linux,
```text
ubuntu@ubuntu-lts:~$ ipcs

------ Message Queues --------
key        msqid      owner      perms      used-bytes   messages

------ Shared Memory Segments --------
key        shmid      owner      perms      bytes      nattch     status
0x82ef8ae8 0          ubuntu     644        1024       0

------ Semaphore Arrays --------
key        semid      owner      perms      nsems
```

In macOS,
```text
~ % ipcs
IPC status from <running system> as of Sun Aug 23 11:28:55 EDT 2020
T     ID     KEY        MODE       OWNER    GROUP
Message Queues:

T     ID     KEY        MODE       OWNER    GROUP
Shared Memory:

T     ID     KEY        MODE       OWNER    GROUP
Semaphores:
```

- `ipcrm` removes the IPC objects
- shmem configuration parameters can be obtained from `sysctl`

In Linux,
```text
~ % sysctl -a | grep sysv.shm
kern.sysv.shmmax: 4194304
kern.sysv.shmmin: 1
kern.sysv.shmmni: 32
kern.sysv.shmseg: 8
kern.sysv.shmall: 1024
```

In macOS,
```text
ubuntu@ubuntu-lts:~$ sudo sysctl -a | grep shm
kernel.shm_next_id = -1
kernel.shm_rmid_forced = 0
kernel.shmall = 18446744073692774399
kernel.shmmax = 18446744073692774399
kernel.shmmni = 4096
vm.hugetlb_shm_group = 0
```

### Differences

- `ipcs` and `ipcrm` has different options in macOS and Linux. For e.g. `ipcs -M` shows the system configuration of shared memory in macOS, where `-M` is not supported in the Linux variant. `ipcs -m` in Linux shows the sizes of the IPC objects too, where macOS requires us to run `ipcs -b` to show the sizes.
- The default value of maximum size of shared memory segment in macOS is just 4MB, whereas in Linux it is typically infinite. If we need more than 4MB, we have to override the values through the sysctl interfaces.

```text
~ % ipcs -M
IPC status from <running system> as of Sun Aug 23 11:17:46 EDT 2020
shminfo:
    shmmax: 4194304 (max shared memory segment size)
    shmmin:       1 (min shared memory segment size)
    shmmni:      32 (max number of shared memory identifiers)
    shmseg:       8 (max shared memory segments per process)
    shmall:    1024 (max amount of shared memory in pages)

# temporarily changing the limits through sysctl
~ % sudo sysctl -w kern.sysv.shmall=2560
kern.sysv.shmall: 1024 -> 2560
~ % sudo sysctl -w kern.sysv.shmmax=10485760
kern.sysv.shmmax: 4194304 -> 10485760

~ % ipcs -M
IPC status from <running system> as of Sun Aug 23 11:47:41 EDT 2020
shminfo:
    shmmax: 10485760    (max shared memory segment size)
    shmmin:       1 (min shared memory segment size)
    shmmni:      32 (max number of shared memory identifiers)
    shmseg:       8 (max shared memory segments per process)
    shmall:    2560 (max amount of shared memory in pages)

~ % sysctl -a | grep sysv.shm
kern.sysv.shmmax: 10485760
kern.sysv.shmmin: 1
kern.sysv.shmmni: 32
kern.sysv.shmseg: 8
kern.sysv.shmall: 2560
```

```text
ubuntu@ubuntu-lts:~$ sudo sysctl -a | grep shm
kernel.shm_next_id = -1
kernel.shm_rmid_forced = 0
kernel.shmall = 18446744073692774399
kernel.shmmax = 18446744073692774399
kernel.shmmni = 4096
vm.hugetlb_shm_group = 0
```

- `ipcmk` in Linux supports creating shared memory and other IPC objects from the command line

## POSIX

Shared memory segments in POSIX IPC are handled very similar to memory mapped file operations. The file descriptor backing the virtual address points to a shared memory instead of a file on the system. The general flow in accessing shared memory segments using POSIX IPC goes like this: `Open` -> `Allocate` -> `Map` -> `Read/Write` -> `Unmap` -> `Close` -> `Remove`.

```c
// Open the shared memory, with required access mode and permissions.
// This is analagous to how we open file with open()
int fd = shm_open("/myshm", O_CREAT | O_RDWR /* open flags */, S_IRUSR | S_IWUSR /* mode */);

// extend or shrink to the required size (specified in bytes)
ftruncate(fd, 1048576); // picking 1MB size as an example

// map the shared memory to an address in the virtual address space
// with the file descriptor of the shared memory and necessary protection.
// The flags to mmap must be set to MAP_SHARED for other process to access.
void *shm_addr = mmap(NULL, 1048576, PROT_READ | PROT_WRITE /*protection*/, MAP_SHARED /*flags*/, fd, 0);

// read from/write to the virtual address backing the shared memory

// when done, unmap the virtual address mapped to the shared memory
munmap(shm_addr, 1048576);

// remove the shared memory when it is no longer needed.
shm_unlink("/myshm");
```

For a proper example with working code, see [here](https://github.com/deepns/fun-with-shared-memory). Some observations from my experiments in running this on Linux and macOS.

- System V and POSIX shared memory segments can coexist in a system. However, they are totally independent and has no interoperability.
- The config and limits of System V does not apply to POSIX and vice versa
- The naming is mandated to start with `/` in some implementations, but not all.

### Linux

- IPC interfaces are available as part of the realtime extensions library `librt`. Programs using posix ipc objects must be linked with `librt`.
- `/dev/shm` - a tmpfs mount by the kernel provides a file system interface to manage the posix shared memory objects. We could create shared memory through this interface too (although not recommended). Here is an example.

```text
posix $ ls /dev/shm/
posix $ echo "created this shmem from /dev/shm" > /dev/shm/shm_posix
posix $ stat /dev/shm/shm_posix
  File: /dev/shm/shm_posix
  Size: 33          Blocks: 8          IO Block: 4096   regular file
Device: 19h/25d	Inode: 3           Links: 1
Access: (0664/-rw-rw-r--)  Uid: ( 1000/  ubuntu)   Gid: ( 1000/  ubuntu)
Access: 2020-08-24 22:55:12.100255179 -0400
Modify: 2020-08-24 22:55:12.100255179 -0400
Change: 2020-08-24 22:55:12.100255179 -0400
 Birth: -
```

[shm_reader](https://github.com/deepns/fun-with-shared-memory/blob/master/posix/shm_reader.c) reads from `shm_posix` shared memory that I just created.

```text
posix $ ./shm_reader.exe
Reading from addr=0x7f3f71a29000, msg=created this shmem from /dev/shm

shm_stats: st_size=33, st_blocks=8, st_blksize=4096
Cleaning up /shm_posix segment
```

### macOS

- Support for POSIX shared memory is somewhat limited. Though the functionality is implemented, there is no file system interface like `/dev/shm` to manage the shared memory segments.
- The default maximum size of the shared memory is just 4MB. That is applicable only to System V based shared memory and not POSIX shared memory segments.
- `stat` support is also limited. `st_size` in bytes is populated, but `st_blocks` and `st_blksize` are not.

## References

- [shm_overview](https://www.man7.org/linux/man-pages/man7/shm_overview.7.html)
- [Dave Marshall notes](http://users.cs.cf.ac.uk/Dave.Marshall/C/node27.html)
- [an example](http://logan.tw/posts/2018/01/07/posix-shared-memory/)
- [SO discussion](https://stackoverflow.com/questions/21311080/linux-shared-memory-shmget-vs-mmap/21312601#21312601)
- [Flylib](https://flylib.com/books/en/3.126.1.115/1/)
- [System V vs POSIX discussion](https://rubenlaguna.com/post/2015-02-22-posix-slash-system-v-shared-memory-vs-threads-shared-memory/`)
- [Setting shm parameters through sysctl.conf](https://www.ssec.wisc.edu/mcidas/doc/users_guide/2015.1/SharedMemory.html)
