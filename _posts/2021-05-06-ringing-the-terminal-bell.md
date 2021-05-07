---
title: Ringing the terminal 🔔
category:
    - Tech
tags:
    - programming
    - linux
    - utilities
    - vscode
header:
  teaser: /assets/images/teasers/terminal-bell.png
---

The terminal bell comes in handy to have a visual or audible notifier while waiting on some jobs/processes to finish. Some ways to trigger the terminal bell. This also works well when working on remote shell in terminals.

- Send the escape character `\a` or the equivalent [ascii code](https://www.ascii-code.com/)(`007`) for terminal bell to stdout
- Query the `bel` capability of the terminal using [tput](https://www.ibm.com/docs/en/aix/7.2?topic=t-tput-command)

## Using echo

```bash
# -n to avoid new line
# -e to interpret the string with backlash-escaped characters
# The behavior of -e is shell specific. 
# For e.g. this was required in bash, but not in zsh
$ echo -ne '\a'

# Running in zsh
% echo -n '\007'
```

## Using printf

This provides the same behavior as echo, but takes out the dependency on shell.

```bash
% printf '\a'

% printf '\007'
```

## Using tput

tput uses the terminfo database to make the terminal capabilities available to the shell.
`bell` is defined as one of the terminal capabilities.

```bash
% tput bel
```

A snippet from `terminfo` man page.

```text
       These are the string capabilities:

               Variable                              Cap-                       TCap                          Description

                String                               name                       Code
       acs_chars                                     acsc                       ac                        graphics charset
                                                                                                          pairs, based on
                                                                                                          vt100
       back_tab                                      cbt                        bt                        back tab (P)
       bell                                          bel                        bl                        audible signal
                                                                                                          (bell) (P)
```

PS: I often use the integrated terminal in Visual Studio code. While it works great for most use cases, terminal bell didn't work as expected due to this [issue#47711](https://github.com/microsoft/vscode/issues/47711). Neither visual nor audio bell worked with the local terminal or when running a remote shell. When working with remote ssh with tmux or screen, sending a bell in the remote server would highlight the tab that triggered the bell. That's the workaround I currently use until [issue#47711](https://github.com/microsoft/vscode/issues/47711) is fixed.

For macOS, there is another way to trigger the bell through OSA scripts. I don't know much about OSA scripts though.

```zsh
% osascript -e 'beep'
```
