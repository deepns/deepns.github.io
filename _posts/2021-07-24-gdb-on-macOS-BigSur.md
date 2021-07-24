---
title: Running GDB on macOS Big Sur
category:
    - Tech
tags:
    - macOS
    - programming
header:
  teaser: /assets/images/teasers/nubelson-fernandes-CO6r5hbt1jg-unsplash.jpg
  caption: "Photo Credit: [Nubelson Fernandes](https://unsplash.com/@@nublson) on [Unsplash](https://unsplash.com/photos/CO6r5hbt1jg)"
---

I usually use a remote VM for my dev work. I switched to my local mac due to some issues with remote environment. When I needed to run some quick debugging experiments, I realized I haven't installed gdb on my local machine yet. So I tried to install using `brew`.

```text
% brew install gdb
Error: 
  homebrew-core is a shallow clone.
  homebrew-cask is a shallow clone.
To `brew update`, first run:
  git -C /usr/local/Homebrew/Library/Taps/homebrew/homebrew-core fetch --unshallow
  git -C /usr/local/Homebrew/Library/Taps/homebrew/homebrew-cask fetch --unshallow
These commands may take a few minutes to run due to the large size of the repositories.
This restriction has been made on GitHub's request because updating shallow
clones is an extremely expensive operation due to the tree layout and traffic of
Homebrew/homebrew-core and Homebrew/homebrew-cask. We don't do this for you
automatically to avoid repeatedly performing an expensive unshallow operation in
CI systems (which should instead be fixed to not use shallow clones). Sorry for
the inconvenience!
==> Downloading https://homebrew.bintray.com/bottles/gdbm-1.19.big_sur.bottle.tar.gz
#=#=-#  #                                                                     
curl: (22) The requested URL returned error: 403 Forbidden
Error: Failed to download resource "gdbm"
Download failed: https://homebrew.bintray.com/bottles/gdbm-1.19.big_sur.bottle.tar.gz
```

It turns out that I haven't updated my homebrew installation in a long time. I was running a pretty old version. Homebrew has migrated away from using bintray quite a while ago.

```text
% brew --version 
Homebrew 3.0.9
Homebrew/homebrew-core (git revision 60004dcdfd; last commit 2021-03-27)
Homebrew/homebrew-cask (git revision 4cae9b1187; last commit 2021-03-28)
```

So I ran the suggested commands to fetch homebrew-core and homebrew-cask before updating. It took several minutes to complete. Trying ot understand what homebrew does here took me down a rabbit hole that I didn't want to chase. I briefly read about [shallow clone](https://github.blog/2020-12-21-get-up-to-speed-with-partial-clone-and-shallow-clone/) and came out.

Ran these commands and then updated brew.

```text
git -C /usr/local/Homebrew/Library/Taps/homebrew/homebrew-core fetch --unshallow
git -C /usr/local/Homebrew/Library/Taps/homebrew/homebrew-cask fetch --unshallow
.
.
% brew update
.
.
You have 43 outdated formulae and 1 outdated cask installed.
You can upgrade them with brew upgrade
or list them with brew outdated.

% brew install gdb
==> Downloading https://ghcr.io/v2/homebrew/core/gdbm/manifests/1.20
######################################################################## 100.0%
==> Downloading https://ghcr.io/v2/homebrew/core/gdbm/blobs/sha256:ea88ce09e934407b1c7dfcc1b74e2d4f1b409f8264b4475b816369a129c6cd25
==> Downloading from https://pkg-containers.githubusercontent.com/ghcr1/blobs/sha256:ea88ce09e934407b1c7dfcc1b74e2d4f1b409f8264b4475b816369a129c6cd25?se=2021-07-24T20%3A15%3A00Z&sig=paVSkzoyrOVn%2FgbsCXvXMfmDMUzmASTmMeVkTZFwaUk%3D&sp=r&spr=https
######################################################################## 100.0%
==> Downloading https://ghcr.io/v2/homebrew/core/mpdecimal/manifests/2.5.1
.
.
```

So I updated brew...installed gdb...all went well until I ran into another error when running gdb. macOS kernel security model prevents gdb from assuming control over another process.

```text
(gdb) run
Starting program: /Users/deepan/scratch/a.out 
Note: this version of macOS has System Integrity Protection.
Because `startup-with-shell' is enabled, gdb has worked around this by
caching a copy of your shell.  The shell used by "run" is now:
    /Users/deepan/Library/Caches/gdb/bin/zsh
Unable to find Mach task port for process-id 16417: (os/kern) failure (0x5).
 (please check gdb is codesigned - see taskgated(8))
```

I followed the instructions from [here](https://sourceware.org/gdb/wiki/PermissionsDarwin) to generate a self signed certificate and make it trusted for code signing. I was skeptical initially to go over all these steps as I don't have any prior experience with the tools and the operations listed on this page. I gave this a try anyway and was finally able to run gdb.

```text
(gdb) run
Starting program: /Users/deepan/scratch/a.out 
[New Thread 0x1803 of process 17301]
```

It got stuck at this point :(. This [bug](https://sourceware.org/bugzilla/show_bug.cgi?id=24069) is the culprit.
I gave up and went back to running gdb in my [Ubuntu VM using multipass](https://www.deepanseeralan.com/tech/running-ubuntu-with-multipass/). I could have gone there directly. Nonetheless, this was a good learning exercise.
