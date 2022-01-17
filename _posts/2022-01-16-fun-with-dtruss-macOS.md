---
title: Fun with macOS dtruss
category:
    - Tech
tags:
    - macOS
    - programming
    - tools
header:
    teaser: /assets/images/teasers/nubelson-fernandes-CO6r5hbt1jg-unsplash.jpg
    caption: "Photo Credit: [Nubelson Fernandes](https://unsplash.com/@@nublson) on [Unsplash](https://unsplash.com/photos/CO6r5hbt1jg)"
---

I was working on a little tool on macOS and wanted to see what system calls does it call internally. Apparently, strace is specific to Linux. macOS has [dtruss](https://opensource.apple.com/source/dtrace/dtrace-147/DTTk/dtruss.auto.html) tool which is a **dtrace** version of [truss](https://www.freebsd.org/cgi/man.cgi?query=truss&apropos=0&sektion=1&manpath=FreeBSD+10.4-RELEASE&arch=default&format=html). **dtruss** is a shell script wrapper around dtrace. Looking at [dtrace man pages](https://www.freebsd.org/cgi/man.cgi?query=dtrace&apropos=0&sektion=1&manpath=FreeBSD+13.0-stable&arch=default&format=html), it seemed to too much of a hassle to run it by myself 🤷. So I happily continued with dtruss.

```console
% dtruss -t socket ./poll_server
dtrace: system integrity protection is on, some features will not be available
dtrace: failed to initialize dtrace: DTrace requires additional privileges
```

Since dtrace required root privileges, re-ran the command as root.

```console
% sudo dtruss -t socket ./poll_server
dtrace: system integrity protection is on, some features will not be available

SYSCALL(args)            = return
Server listening at port 11011
socket(0x2, 0x1, 0x0)            = 3 0
```

Then wanted to explore **dtruss** with some of the system programs.

```consoles
~ % sudo dtruss du -h
Password:
dtrace: system integrity protection is on, some features will not be available

dtrace: failed to execute du: Operation not permitted
~ %
```

Damn 🤔. It didn't let me to run dtruss even with root privileges. I was kicked out by [System Integrity Protection](https://support.apple.com/en-us/HT204899). Since macOS El Capitan, SIP limits the actions that even a root user can perform on the programs that come under the protected paths (e.g. **/System, /usr, /bin, /sbin/, /var** and some pre-installed apps). Tracing is one of those prohibited actions.

So I tried copying the binary to an unprotected path (e.g. `/tmp`) and ran dtruss again.

```console
~ % cp $(which du) /tmp
~ % sudo dtruss /tmp/du -h
Password:
dtrace: system integrity protection is on, some features will not be available

dtrace: failed to execute /tmp/du: Operation not permitted
~ %
```

🙄🙄🙄 You kidding me? Then I came to know that the system tools are code signed, so the signature come along even if we run them from another path in the system. So wanted to see some more information about the code signature.

```console
~ % codesign --display /tmp/du
Executable=/private/tmp/du
```

By default, **codesign** doesn't display much information. We have to up the verbose level.

```console
~ % codesign --display --verbose=1 /tmp/du
Executable=/private/tmp/du
Identifier=com.apple.du
Format=Mach-O universal (x86_64 arm64e)
CodeDirectory v=20400 size=453 flags=0x0(none) hashes=9+2 location=embedded
Platform identifier=13
Signature size=4442
Signed Time=Oct 1, 2021 at 9:31:44 PM
Info.plist=not bound
TeamIdentifier=not set
Sealed Resources=none
Internal requirements count=1 size=6

~ % codesign --display --verbose=4 /tmp/du
Executable=/private/tmp/du
Identifier=com.apple.du
Format=Mach-O universal (x86_64 arm64e)
CodeDirectory v=20400 size=453 flags=0x0(none) hashes=9+2 location=embedded
Platform identifier=13
VersionPlatform=1
VersionMin=658944
VersionSDK=786432
Hash type=sha256 size=32
CandidateCDHash sha256=7d2b17ef804dcfa615e1e36c48c8af3ac0f73156
CandidateCDHashFull sha256=7d2b17ef804dcfa615e1e36c48c8af3ac0f73156b062ecf6cb7529e88b68c9ce
Hash choices=sha256
CMSDigest=7d2b17ef804dcfa615e1e36c48c8af3ac0f73156b062ecf6cb7529e88b68c9ce
CMSDigestType=2
Executable Segment base=0
Executable Segment limit=16384
Executable Segment flags=0x1
Page size=4096
CDHash=7d2b17ef804dcfa615e1e36c48c8af3ac0f73156
Signature size=4442
Authority=Software Signing
Authority=Apple Code Signing Certification Authority
Authority=Apple Root CA
Signed Time=Oct 1, 2021 at 9:31:44 PM
Info.plist=not bound
TeamIdentifier=not set
Sealed Resources=none
Internal requirements count=1 size=60
```

I then removed the code signature using `codesign --remove-signature`.

```console
~ % codesign --remove-signature /tmp/du
~ % codesign --display --verbose=4 /tmp/du
/tmp/du: code object is not signed at all
```

After removing the code signature, I was able to run dtruss on the copied binary. (there were some probes which were still denied)

```console
~ % sudo dtruss /tmp/du -h
Password:
dtrace: system integrity protection is on, some features will not be available

SYSCALL(args)            = return
 88K    .
access("/AppleInternal/XBS/.isChrooted\0", 0x0, 0x0)             = -1 2
bsdthread_register(0x7FF802308020, 0x7FF80230800C, 0x2000)               = 1073742303 0
shm_open(0x7FF8021D6F5D, 0x0, 0x21D57BA)                 = 3 0
fstat64(0x3, 0x7FF7B04D50F0, 0x0)                = 0 0
mmap(0x0, 0x2000, 0x1, 0x40001, 0x3, 0x0)                = 0x10FB37000 0
close(0x3)               = 0 0
ioctl(0x2, 0x4004667A, 0x7FF7B04D51A4)           = 0 0
mprotect(0x10FB3E000, 0x1000, 0x0)               = 0 0
mprotect(0x10FB43000, 0x1000, 0x0)               = 0 0
mprotect(0x10FB44000, 0x1000, 0x0)               = 0 0
mprotect(0x10FB49000, 0x1000, 0x0)               = 0 0
mprotect(0x10FB39000, 0x90, 0x1)                 = 0 0
mprotect(0x10FB39000, 0x90, 0x3)                 = 0 0
mprotect(0x10FB39000, 0x90, 0x1)                 = 0 0
mprotect(0x10FB4A000, 0x1000, 0x1)               = 0 0
mprotect(0x10FB4B000, 0x90, 0x1)                 = 0 0
mprotect(0x10FB4B000, 0x90, 0x3)                 = 0 0
mprotect(0x10FB4B000, 0x90, 0x1)                 = 0 0
mprotect(0x10FB39000, 0x90, 0x3)                 = 0 0
mprotect(0x10FB39000, 0x90, 0x1)                 = 0 0
mprotect(0x10FB4A000, 0x1000, 0x3)               = 0 0
mprotect(0x10FB4A000, 0x1000, 0x1)               = 0 0
issetugid(0x0, 0x0, 0x0)                 = 0 0
getentropy(0x7FF7B04D4FC0, 0x20, 0x0)            = 0 0
getentropy(0x7FF7B04D5020, 0x40, 0x0)            = 0 0
getpid(0x0, 0x0, 0x0)            = 83854 0
stat64("/AppleInternal\0", 0x7FF7B04D56C0, 0x0)          = -1 2
csops_audittoken(0x1478E, 0x7, 0x7FF7B04D51F0)           = -1 22
proc_info(0x2, 0x1478E, 0xD)             = 64 0
csops_audittoken(0x1478E, 0x7, 0x7FF7B04D52E0)           = -1 22
sysctlbyname(kern.osvariant_status, 0x15, 0x7FF7B04D5710, 0x7FF7B04D5708, 0x0)           = 0 0
csops(0x1478E, 0x0, 0x7FF7B04D5744)              = 0 0
mprotect(0x10FA35000, 0x100000, 0x1)             = 0 0
open_nocancel("/usr/share/locale/en_US.UTF-8/LC_COLLATE\0", 0x0, 0x0)            = 3 0
fcntl_nocancel(0x3, 0x3, 0x0)            = 0 0
getrlimit(0x1008, 0x7FF7B04D6130, 0x0)           = 0 0
fstat64(0x3, 0x7FF7B04D60A8, 0x0)                = 0 0
dtrace: error on enabled probe ID 1690 (ID 969: syscall::read_nocancel:return): invalid kernel access in action #12 at DIF offset 68
close_nocancel(0x3)              = 0 0
open_nocancel("/usr/share/locale/en_US.UTF-8/LC_CTYPE\0", 0x0, 0x0)              = 3 0
fcntl_nocancel(0x3, 0x3, 0x0)            = 0 0
fstat64(0x3, 0x7FF7B04D61E8, 0x0)                = 0 0
fstat64(0x3, 0x7FF7B04D5FE8, 0x0)                = 0 0
lseek(0x3, 0x0, 0x1)             = 0 0
lseek(0x3, 0x0, 0x0)             = 0 0
dtrace: error on enabled probe ID 1690 (ID 969: syscall::read_nocancel:return): invalid kernel access in action #12 at DIF offset 68
dtrace: error on enabled probe ID 1690 (ID 969: syscall::read_nocancel:return): invalid kernel access in action #12 at DIF offset 68
dtrace: error on enabled probe ID 1690 (ID 969: syscall::read_nocancel:return): invalid kernel access in action #12 at DIF offset 68
dtrace: error on enabled probe ID 1690 (ID 969: syscall::read_nocancel:return): invalid kernel access in action #12 at DIF offset 68
dtrace: error on enabled probe ID 1690 (ID 969: syscall::read_nocancel:return): invalid kernel access in action #12 at DIF offset 68
dtrace: error on enabled probe ID 1690 (ID 969: syscall::read_nocancel:return): invalid kernel access in action #12 at DIF offset 68
dtrace: error on enabled probe ID 1690 (ID 969: syscall::read_nocancel:return): invalid kernel access in action #12 at DIF offset 68
dtrace: error on enabled probe ID 1690 (ID 969: syscall::read_nocancel:return): invalid kernel access in action #12 at DIF offset 68
close_nocancel(0x3)              = 0 0
open_nocancel("/usr/share/locale/en_US.UTF-8/LC_MONETARY\0", 0x0, 0x0)           = 3 0
fstat64(0x3, 0x7FF7B04D61F8, 0x0)                = 0 0
dtrace: error on enabled probe ID 1690 (ID 969: syscall::read_nocancel:return): invalid kernel access in action #12 at DIF offset 68
close_nocancel(0x3)              = 0 0
open_nocancel("/usr/share/locale/en_US.UTF-8/LC_NUMERIC\0", 0x0, 0x0)            = 3 0
fstat64(0x3, 0x7FF7B04D61F8, 0x0)                = 0 0
dtrace: error on enabled probe ID 1690 (ID 969: syscall::read_nocancel:return): invalid kernel access in action #12 at DIF offset 68
close_nocancel(0x3)              = 0 0
open_nocancel("/usr/share/locale/en_US.UTF-8/LC_TIME\0", 0x0, 0x0)               = 3 0
fstat64(0x3, 0x7FF7B04D61F8, 0x0)                = 0 0
dtrace: error on enabled probe ID 1690 (ID 969: syscall::read_nocancel:return): invalid kernel access in action #12 at DIF offset 68
close_nocancel(0x3)              = 0 0
open_nocancel("/usr/share/locale/en_US.UTF-8/LC_MESSAGES/LC_MESSAGES\0", 0x0, 0x0)               = 3 0
fstat64(0x3, 0x7FF7B04D61F8, 0x0)                = 0 0
dtrace: error on enabled probe ID 1690 (ID 969: syscall::read_nocancel:return): invalid kernel access in action #12 at DIF offset 68
close_nocancel(0x3)              = 0 0
sysctlbyname(vfs.nspace.prevent_materialization, 0x22, 0x0, 0x0, 0x7FF7B04D6874)                 = 0 0
sigaction(0x1D, 0x7FF7B04D6758, 0x7FF7B04D6780)          = 0 0
fstatat64(0xFFFFFFFFFFFFFFFE, 0x7FF40FF04938, 0x7FF40FF04940)            = 0 0
getattrlist(".\0", 0x7FF7B04D67B0, 0x7FF7B04D6850)               = 0 0
open_nocancel(".\0", 0x1100004, 0x0)             = 3 0
getattrlistbulk(0x3, 0x7FF7B04D66E8, 0x7FF41000B000)             = 2 0
getattrlistbulk(0x3, 0x7FF7B04D66E8, 0x7FF41000B000)             = 0 0
close_nocancel(0x3)              = 0 0
fstat64(0x1, 0x7FF7B04D6468, 0x0)                = 0 0
ioctl(0x1, 0x4004667A, 0x7FF7B04D64B4)           = 0 0
dtrace: error on enabled probe ID 1688 (ID 971: syscall::write_nocancel:return): invalid kernel access in action #12 at DIF offset 68
```

We can filter specific system call as well.

```console
~ % sudo dtruss -t mmap /tmp/du -h
dtrace: system integrity protection is on, some features will not be available

SYSCALL(args)            = return
 88K    .
mmap(0x0, 0x2000, 0x1, 0x40001, 0x3, 0x0)                = 0x10B9B4000 0

~ % sudo dtruss -t fstat64 /tmp/du -h
dtrace: system integrity protection is on, some features will not be available

SYSCALL(args)            = return
 88K    .
fstat64(0x3, 0x7FF7BF0290E0, 0x0)                = 0 0
fstat64(0x3, 0x7FF7BF02A098, 0x0)                = 0 0
fstat64(0x3, 0x7FF7BF02A1D8, 0x0)                = 0 0
fstat64(0x3, 0x7FF7BF029FD8, 0x0)                = 0 0
fstat64(0x3, 0x7FF7BF02A1E8, 0x0)                = 0 0
fstat64(0x3, 0x7FF7BF02A1E8, 0x0)                = 0 0
fstat64(0x3, 0x7FF7BF02A1E8, 0x0)                = 0 0
fstat64(0x3, 0x7FF7BF02A1E8, 0x0)                = 0 0
fstat64(0x1, 0x7FF7BF02A458, 0x0)                = 0 0

~ % sudo dtruss -t ioctl /tmp/du -h
dtrace: system integrity protection is on, some features will not be available

SYSCALL(args)            = return
 88K    .
ioctl(0x2, 0x4004667A, 0x7FF7B3BA51A4)           = 0 0
ioctl(0x1, 0x4004667A, 0x7FF7B3BA64B4)           = 0 0
```
