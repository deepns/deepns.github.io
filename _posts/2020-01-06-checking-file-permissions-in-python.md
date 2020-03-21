---
title: Checking file permissions in Python
categories:
    - Tech
tags:
    - linux
    - python
---

I was writing a small script to automate some of my workflow of invoking several small scripts. I wanted to check the permissions of the internal scripts to avoid any unexpected errors in the overall execution. I can certainly get the file permissions with commands like `ls` and `stat` from the shell. I wanted to do the same but through Python this time. The python interfaces to check the file permissions resemble very much like the native calls.

The options to `stat` command on macOS/FreeBSD aren't quite the same from the `stat` command on Linux. For e.g. the option `-f` is used to specify the output format in the macOS stat command, where it is used to display file system status instead of file status in Linux. Along with permissions, stat command shows many other information too (such as access times, inode number etc..). Here are some examples.

```text
$ ls
cmd1 cmd2 cmd3

$ stat -f "%p" cmd*
100644
100644
100644

$ stat -f "%Sp" cmd*
-rw-r--r--
-rw-r--r--
-rw-r--r--
```

The option `-s` shows the file status in a form that can be used to assign shell variables.

```text
$ stat -s cmd1
st_dev=16777220 st_ino=4315060526 st_mode=0100644 st_nlink=1 st_uid=501 st_gid=20 st_rdev=0 st_size=0 st_atime=1577982315 st_mtime=1577982315 st_ctime=1577982315 st_birthtime=1577982315 st_blksize=4096 st_blocks=0 st_flags=0
```

The same information can be obtained through the functions in [os](https://docs.python.org/3/library/os.html) and [stat](https://docs.python.org/3/library/stat.html) modules of Python. The function `os.stat` returns an `os.stat_result` object containing several information about the given file. The file type and access flags are carried in the mode field (st_mode), just like the stat system call. See [stat.h](https://github.com/torvalds/linux/blob/master/include/uapi/linux/stat.h) for the values of different file types and access permission flags.

```python
>>> import os
>>> status = os.stat("cmd1")
>>> status
os.stat_result(st_mode=33252, st_ino=4315060526, st_dev=16777220, st_nlink=1, st_uid=501, st_gid=20, st_size=0, st_atime=1577982315, st_mtime=1577982315, st_ctime=1577984724)
>>> # converting the unsigned value of st_mode into octal form
... oct(status.st_mode)
'0o100744'
```

`stat` module has the helper definitions to validate the stat mode of a file. Since the stat module implementation is backed by C, the flags used here are also inline with definitions in C.

```python
>>> import stat
>>> status
os.stat_result(st_mode=33252, st_ino=4315060526, st_dev=16777220, st_nlink=1, st_uid=501, st_gid=20, st_size=0, st_atime=1577982315, st_mtime=1577982315, st_ctime=1577984724)
>>> # check whether the file is readable and writable by the user
... hex(status.st_mode & (stat.S_IRUSR | stat.S_IWUSR))
'0x180'
>>> # check whether the file is executable by the user
... hex(status.st_mode & stat.S_IXUSR)
'0x40'
>>> # check whether the file is writable by the others
... hex(status.st_mode & stat.S_IWOTH)
'0x0'
>>> # get a human readable form of the permissions, similar to what displayed in ls -l
... stat.filemode(status.st_mode)
'-rwxr--r--'
```

To check whether current process has permissions on a certain file, we could use [os.access](https://docs.python.org/3/library/os.html?#os.access) which is based on the [access system call](https://www.freebsd.org/cgi/man.cgi?query=access&apropos=0&sektion=2&manpath=CentOS+7.1&arch=default&format=html). It uses real-uid instead of the effective uid of the calling process. For security reasons, it is however discouraged to use this call to check whether an user is authorized for certain permissions or not before calling open(). One could exploit the interval between the invocations of `access()` and `open()` and manipulate the permissions.

```python
>>> os.access("cmd1", os.R_OK | os.W_OK)
True
>>> os.access("cmd1", os.X_OK)
True
```
