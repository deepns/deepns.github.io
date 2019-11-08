---
title: VSCode app missing from macOS dock
categories:
    - tech
tags:
    - macOS
    - VSCode
---

I ran into weird problem with VSCode on my Mac recently. The app would show up in the list of open apps, Spotlight and also under Applications. However, it was missing from the dock even though I explicity set the `Keep in Dock` option. It was annoying sometimes as it would confuse me whether the app is open or not. I restarted VSCode few times, but it didn't make any difference in the dock. In the end, restarting the `Dock` process fixed the problem.

`Dock` is one of the several core services in the macOS (checkout `/System/Library/CoreServices/`). Killing the process will restart the service again. `Dock` can be killed in mulitple ways:

- Open `Activity Monitor`, search for the Dock process and stop it. Choose `Force Quit` when stopping the process.
- Open `Terminal` app and run `killall Dock`. Note that process name here is case sensitive. 
  - Alternatively, you can also find the process ID and send a kill signal. To find the pid of Dock, use `pgrep Dock`. `ps -p` displays the details about the given process id.

```text
$ ps -p $(pgrep Dock)
  PID TTY           TIME CMD
15890 ??         0:01.92 /System/Library/CoreServices/Dock.app/Contents/MacOS/Dock
```

This solution can also be applied when the dock is unresponsive or frozen.
