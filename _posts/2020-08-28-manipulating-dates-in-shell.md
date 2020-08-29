---
title: Manipulating dates in shell
category:
    - Tech
tags:
    - linux
    - utilities
    - python
    - programming
---

After a long time, I had to automate some of my workflow using shell scripts. One of the functions was to lookup something based on relative dates. Having used to Python and C for quite some time, I totally forgot the options and syntax to do the same thing in bash. I can use `datetime` and `timedelta` from `datetime` module to look up dates relative to a certain date.

```python
>>> from datetime import datetime, timedelta
>>> for i in range(7):
...     print(datetime.today() - timedelta(days=i))
...
2020-08-29 13:36:35.981576
2020-08-28 13:36:35.981656
2020-08-27 13:36:35.981694
2020-08-26 13:36:35.981730
2020-08-25 13:36:35.981766
2020-08-24 13:36:35.981801
2020-08-23 13:36:35.981837

>>> # Say I want to do something in the days between christmas and new year
>>> xmas = datetime.strptime("12/25/20", "%m/%d/%y")
>>> newyear = datetime.strptime("01/01/21", "%m/%d/%y")
>>> date = xmas
>>> while (date != newyear):
...     # do something
...     print(date)
...     date += timedelta(days=1)
...
2020-12-25 00:00:00
2020-12-26 00:00:00
2020-12-27 00:00:00
2020-12-28 00:00:00
2020-12-29 00:00:00
2020-12-30 00:00:00
2020-12-31 00:00:00
```

I didn't know `date` command in bash supports relative calculation. The `-d`/`--date` option to `date` command takes input in variety of formats (including human readable ones like `today`, `next month`, `last year`) that support both absolute and relative values.

Here are some examples.

```bash
ubuntu@ubuntu-lts:~$ date
Sat Aug 29 13:48:13 EDT 2020
ubuntu@ubuntu-lts:~$ date --date "last week"
Sat Aug 22 13:48:23 EDT 2020
ubuntu@ubuntu-lts:~$ date --date "-7 days"
Sat Aug 22 13:48:36 EDT 2020
ubuntu@ubuntu-lts:~$ for i in {1..7};do date --date "-$i days" +%c; done
Fri Aug 28 13:51:21 2020
Thu Aug 27 13:51:21 2020
Wed Aug 26 13:51:21 2020
Tue Aug 25 13:51:21 2020
Mon Aug 24 13:51:21 2020
Sun Aug 23 13:51:21 2020
Sat Aug 22 13:51:21 2020
```

The man page for `date` didn't have full details on the free format for the `--date` option. The [info page](http://www.gnu.org/software/coreutils/manual/coreutils.html#Relative-items-in-date-strings) for `coreutil` had that information (this can also be viewed from the command line with `info coreutils` command).

The `date` tool in `macOS` is quite different though. The option `-d` is used to set the datetime in the kernel unlike the gnu counterpart where `-d` is used to specify the string to display the time. `date` uses the option `-f` to parse date strings similar to [strptime](https://man7.org/linux/man-pages/man3/strptime.3.html). The option `-v` is the one to use adjust date and display the adjustment that works similar to `--date` with the gnu version. However, it doesn't support human readable input strings.

```zsh
~ % date
Sat Aug 29 14:11:37 EDT 2020
~ % date -v +1d
Sun Aug 30 14:11:45 EDT 2020
~ % date -v +1d -v -1m # go back 1month, 1day
Thu Jul 30 14:11:58 EDT 2020

~ % for i in {1..7};do  date -v -1m -v -${i}d +%c;done
Tue Jul 28 14:15:32 2020
Mon Jul 27 14:15:32 2020
Sun Jul 26 14:15:32 2020
Sat Jul 25 14:15:32 2020
Fri Jul 24 14:15:32 2020
Thu Jul 23 14:15:32 2020
Wed Jul 22 14:15:32 2020
```
