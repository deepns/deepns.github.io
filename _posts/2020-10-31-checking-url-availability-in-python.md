---
title: Checking URL availability in Python
categories:
    - Tech
tags:
    - programming
    - python
    - utilities
    - macOS
---

I had to script some of the tasks in my workflow that required checking whether URL is alive or not. Noting it down here for my future reference.
I ran into `SSL: CERTIFICATE_VERIFY_FAILED` error when I tried to access https links on macOS through this tool. I later realize that I didn't read the README instructions of Python installation properly and missed to run the additional script (`/Applications/Python\ 3.6/Install\ Certificates.command`) (side effect of always ignoring the readme instructions :blush:). Afer running that script, things worked as expected.

<script src="https://gist.github.com/deepns/ca1f9c35882a0512e1bf9cad4a6c1913.js"></script>
