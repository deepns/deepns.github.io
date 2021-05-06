---
title: A Python script to run commands over SSH
header:
    teaser: /assets/images/teasers/ssh-using-python.png
category:
    - Tech
tags:
    - python
    - programming
    - utilities
---

When working with remote servers, I needed to run some commands frequently and sometimes save the command output for later references and debugging. Manually running the commands over ssh each time was quite cumbersome. So I started using Python's [paramiko](http://docs.paramiko.org/en/stable/index.html) library to automate some of the workflow. Having a wrapper over the paramiko library makes it much easier to customize with additional functionalities than working directly with the library calls.

<script src="https://gist.github.com/deepns/65b28e8ea40a555f84b85adaba314941.js"></script>
