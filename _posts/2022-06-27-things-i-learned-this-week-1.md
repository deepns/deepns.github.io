---
title: Things I learned/revisited this week#1
category:
    - Tech
tags:
    - learning
    - python
    - cryptography
    - docker
    - markdown
lcb: "{"
header:
    image: /assets/images/headers/tim-mossholder-WE_Kv_ZB1l0-unsplash.jpg
    caption: "Photo Credit: [Tim Mossholder](https://unsplash.com/@timmossholder) on [Unsplash](https://unsplash.com/photos/WE_Kv_ZB1l0)"
    teaser: /assets/images/teasers/tim-mossholder-WE_Kv_ZB1l0-unsplash.jpg
---

Reading SSL certificate material with python cryptography library...deleting git branches...docker command formatting...escaping liquid syntax in markdown.

- Load x509 certificate and rsa key files using [Python cryptography library](https://cryptography.io/en/latest/x509/reference/#loading-certificates)

```python
from cryptography as x509
with open(cert_file, "rb") as cert_file_fp:
    # opening the file in byte mode
    cert_file_pem = x509.load_pem_x509_certificate(cert_file_fp.read())
    print(cert_file_pem.serial_number, cert_file_pem.subject)
    # backend parameter deprecated from version 36.0.0 onwards
    # See https://cryptography.io/en/latest/faq/#what-happened-to-the-backend-argument
    # cert_file_pem = x509.load_pem_x509_certificate(cert_file_fp.read(), backend=default_backend())

from cryptography.hazmat.primitives import serialization
with open(key_file, "rb") as key_file_fp:
    # unencrypted key, so leaving the password as None
    key_file_pem = serialization.load_pem_private_key(
                                    key_file_fp.read(), 
                                    password=None)
    # dumping the public key info
    public_key = key_file_pem.public_key()
    print(public_key.public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo
    ))                                 
```

- Deleting local and remote branches in Git.
   1. local
      1. to delete => `git branch --delete <branch-name>` (or `git branch -d`)
      2. to force delete => `git branch --delete --force <branch-name>` (or `git branch -D <branch-name>`)
   2. remote - `git push origin --delete <remote-branch-name>`

- **perror("some msg")** from standard library - prints `some msg: <description of error matching errno>`. (use **strerror(errno)** to get just the description of errno)

- [Format](https://docs.docker.com/engine/reference/commandline/images/#format-the-output) **docker images** output to display only the image and tag information => {% raw %} `$(docker images --format '{{.Repository}}:{{.Tag}}')`.{% endraw %} Formatting is based on [Go templates](https://pkg.go.dev/text/template). This is often useful in scripting to use only the needed fields.

{% raw %}
```bash
$ docker images
REPOSITORY   TAG       IMAGE ID       CREATED       SIZE
nginx        latest    7425d3a7c478   3 weeks ago   142MB

$ # {{..}} are the Actions
$ # all text between actions is copied verbatim 
$ docker images --format '{{.Repository}}:{{.Tag}}'
nginx:latest
{% endraw %}
```

- Escape liquid syntax in markdown with **{{ page.lcb }}% raw %}** and **{{ page.lcb }}% endraw %}** tags. Thanks to [this post](https://ozzieliu.com/2016/04/26/writing-liquid-template-in-markdown-with-jekyll/). The second workaround of using jekyll variables was helpful to even escape **raw** and **endraw** tags.
