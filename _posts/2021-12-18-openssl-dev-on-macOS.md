---
title: Working with openssl in macOS
category:
    - Tech
tags:
    - programming
header:
  teaser: /assets/images/teasers/openssl-certificate-post.jpeg
---

A quick note to myself. When installing `openssl` through `brew` on macOS, the installation is not symlinked into `/usr/local`.

```text
~ % brew info openssl@1.1            
openssl@1.1: stable 1.1.1l (bottled) [keg-only]
Cryptography and SSL/TLS Toolkit
https://openssl.org/
/usr/local/Cellar/openssl@1.1/1.1.1l_1 (8,073 files, 18.5MB)
  Poured from bottle on 2021-12-08 at 22:55:46
From: https://github.com/Homebrew/homebrew-core/blob/HEAD/Formula/openssl@1.1.rb
License: OpenSSL
==> Dependencies
Required: ca-certificates ✔
==> Caveats
A CA file has been bootstrapped using certificates from the system
keychain. To add additional certificates, place .pem files in
  /usr/local/etc/openssl@1.1/certs

and run
  /usr/local/opt/openssl@1.1/bin/c_rehash

openssl@1.1 is keg-only, which means it was not symlinked into /usr/local,
because macOS provides LibreSSL.

If you need to have openssl@1.1 first in your PATH, run:
  echo 'export PATH="/usr/local/opt/openssl@1.1/bin:$PATH"' >> ~/.zshrc

For compilers to find openssl@1.1 you may need to set:
  export LDFLAGS="-L/usr/local/opt/openssl@1.1/lib"
  export CPPFLAGS="-I/usr/local/opt/openssl@1.1/include"

For pkg-config to find openssl@1.1 you may need to set:
  export PKG_CONFIG_PATH="/usr/local/opt/openssl@1.1/lib/pkgconfig"

==> Analytics
install: 860,488 (30 days), 2,764,743 (90 days), 9,780,423 (365 days)
install-on-request: 29,818 (30 days), 101,109 (90 days), 787,233 (365 days)
build-error: 1,183 (30 days)
~ % 
```

**brew** installs the requested version of openssl into `/usr/local/Cellar/` and creates a symlink at `/usr/local/opt/openssl`. We can set the options `-I/usr/local/opt/openssl/include` and `-L/usr/local/opt/openssl/lib/` when compiling the application that uses the version of openssl symlinked into `/usr/local/opt/openssl/`. I was playing with only one version (1.1.1), so didn't have to worry about maintaining different versions on the system. Having the libs and include files symlinked into `/usr/local/lib` and `/usr/local/include` takes out the hassle of setting the preprocessor options each time.

```text
~ % ln -s /usr/local/opt/openssl/include/openssl /usr/local/include/
~ % ln -s /usr/local/opt/openssl/lib/libssl.dylib /usr/local/lib 
~ % ln -s /usr/local/opt/openssl/lib/libssl.a /usr/local/lib
~ % ln -s /usr/local/opt/openssl/lib/libcrypto.a /usr/local/lib
~ % ln -s /usr/local/opt/openssl/lib/libcrypto.dylib /usr/local/lib

~ % ls -l /usr/local/opt/openssl \
/usr/local/include/openssl /usr/local/lib/libss* /usr/local/lib/libcryp* \
> | cut -w -f9-11
/usr/local/include/openssl	->	/usr/local/opt/openssl/include/openssl
/usr/local/lib/libcrypto.a	->	/usr/local/opt/openssl/lib/libcrypto.a
/usr/local/lib/libcrypto.dylib	->	/usr/local/opt/openssl/lib/libcrypto.dylib
/usr/local/lib/libssl.a	->	/usr/local/opt/openssl/lib/libssl.a
/usr/local/lib/libssl.dylib	->	/usr/local/opt/openssl/lib/libssl.dylib
/usr/local/opt/openssl	->	../Cellar/openssl@1.1/1.1.1l_1
```
