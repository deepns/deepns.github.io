---
title: Playing with posix message queues
categories:
    - Tech
tags:
    - programming
    - c
    - linux
---

While working on my [last post on filesystems](https://deepns.github.io/tech/some-notes-on-filesystems-part2/), I came across [mqueuefs](https://deepns.github.io/tech/some-notes-on-filesystems-part2/#mqueuefs). The mqueuefs interface gives the information about the active message queues in the system and basic stats about them. I wanted to try out the posix message queues just for fun to see how it works and how the library calls are used. So I designed a sample application with few threads and used posix message queues to communicate betwen them. The sample code can be found in this [repository](https://github.com/deepns/posix-mq-example).
