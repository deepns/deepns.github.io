---
title: Lessons from coloring screen
category:
    - Tech
tags:
    - linux
    - macOS
    - productivity
    - utilities
gallery:
    - url: /assets/images/for-posts/term-colors-inside-screen.png
      image_path: /assets/images/for-posts/term-colors-inside-screen.png
    - url: /assets/images/for-posts/term-colors-outside-screen.png
      image_path: /assets/images/for-posts/term-colors-outside-screen.png
---

I recently started customizing my dev environment after a long time. I installed [lightline](https://github.com/itchyny/lightline.vim) for a configurable statusline in vim, modified some of my settings in `.vimrc` and also changed the color theme to [monokai](https://github.com/crusoexia/vim-monokai/blob/master/colors/monokai.vim). It worked great on my mac and brought vim interface very close to vscode. It looked great on my remote dev server too until I started using inside a [gnu  screen](https://www.gnu.org/software/screen/) session. The colors appeared little off from what I see in my mac (inside and outside screen) versus running vim inside screen in my remote server.

I have set the terminal type to xterm-256color in my iTerm long time ago and also in my remote environment through $TERM, so nothing has changed on that front. Many stack overflow threads([this](https://apple.stackexchange.com/questions/39608/running-gnu-screen-with-256-colors-on-os-x-lion/46855), [this](https://www.tigraine.at/2012/01/25/make-gnu-screen-xterm-256color-work-on-osx), [this](https://unix.stackexchange.com/questions/118806/tmux-term-and-256-colours-support), and [this](https://stackoverflow.com/questions/6787734/strange-behavior-of-vim-color-inside-screen-with-256-colors)) talked about tweaking term settings. I read through several of them, but couldn’t get my environment working with the expected colors. I found this [neat perl script](https://gist.github.com/hSATAC/1095100#file-256color-pl) that shows the supported colors on the terminal.

{% include gallery layout="half" caption="Screenshots from colors in 16 color (on the left) and 256 color terminals. (on right)" %}

Finally found one post that talked about identifying the screen configuration in the welcome page. Honestly I had never paid attention to that message before. Looking at the welcome message of screen in local Ubuntu box, it showed the capabilities.

```bash
Capabilities:
+copy +remote-detach +power-detach +multi-attach +multi-user +font +color-256 +utf8 +rxvt +builtin-telnet
```

Whereas, the screen on the remote server showed `+color-16` instead of `+color-256` in the capabilities section of the welcome message. It turns out that screen on my remote server was never compiled with 256 color support.

That’s when I realized no tweaks of using 256 color would work as the executable itself was compiled to support only 16 colors.  After some fights in making this work, I decided to switch from `screen` to `tmux` for my terminal multiplexing needs. I attempted to try `tmux` some years ago, but kept using screen only as it had been working good for the most part. I finally decided to switch to `tmux` once for all. Many settings and key mapping in tmux is quite siimlar to screen albeit the configuration and commands differ by a large extent. It may take few days to ramp up in the new environment, but it will be worth the switch.
