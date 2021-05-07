---
title: Convert epoch seconds to datetime
category:
    - Tech
tags:
    - shell
    - linux
    - macOS
header:
  teaser: /assets/images/teasers/convert-epoch-seconds-into-datetime.png
---

Some of the logs I debug often contain the timestamp in the form of [epoch seconds](https://en.wikipedia.org/wiki/Epoch_(computing)), so I frequently had to convert them into readable datetime format. Noting this down for a quick reference.

## macOS

```zsh
# % date -r <seconds>
~ % date -r 1220355645
Tue Sep  2 07:40:45 EDT 2008
```

## Linux coreutils

```bash
# date -d @<seconds>
$ date -d @1120355645
Sat Jul  2 21:54:05 EDT 2005
```

[coreutils date conversion specifiers](https://www.gnu.org/software/coreutils/manual/coreutils.html#Date-conversion-specifiers)

## Display current time in epoch seconds

(common to both macOS and coreutils)

```bash
~$ date +%s
1620355706
```
