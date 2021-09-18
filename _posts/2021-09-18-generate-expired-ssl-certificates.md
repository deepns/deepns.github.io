---
title: Generate expired SSL certificates using openssl and faketime
category:
    - Tech
tags:
    - programming
    - tools
    - security
header:
  teaser: /assets/images/teasers/openssl-certificate-post.jpeg
---

While playing with HTTPS related things recently, I wanted to see how the server initialization and the client side respond when the certificate provided to the server has expired. Since I used self-signed certificates for my test server, I was able to play with different configurations. The lowest duration of validity we can give to the certificate is 1 day. I wasn't patient enough to wait for a day to let the certificate expire. Nor the automated tests. So I had to find a way to generate certificates that is expired at the time of generation itself.

I stumbled upon [libfaketime](https://github.com/wolfcw/libfaketime) that worked perfectly for my use case. libfaketime intercepts various system calls from the given program and report modified date and time. I used the CLI version `faketime` as it had enough functionalities for my needs.

- Generate the root ca with start time sometime in the past

```bash
# Generate the private key and self-signed cert for the root CA
faketime 'last week' openssl req -x509 -nodes -sha256 \
    -newkey rsa:2048 -days 365 -out root_ca.crt -keyout root_ca.key \
    -subj "/C=US/ST=DE/O=MyCert, Inc./CN=mycert.com" 
```

- Generate the server certificate and key using the root_ca, but with shorter validity so it is expired at the time of generation itself.

```bash
# Generate the CSR for the server
openssl req -new -nodes -newkey rsa:2048 \
    -subj "/C=US/ST=DE/O=ExampleOrg, Inc./CN=127.0.0.1" \
    -out server.csr -keyout server.key

# Generate the certificate signed by the root CA
# The lowest validity is 1 day. we would have to wait
# for a day for the certificate to expire. Instead, use
# faketime to generate cert with validity starting
# from the date specified in faketime
faketime '3 days ago' openssl x509 -req -sha256 -days 1 \
    -in server.csr -CA root_ca.crt -CAkey root_ca.key \
    -CAcreateserial -out server.crt
```

Lets run these commands.

```text
generate-expired-certs % faketime 'last week' openssl req -x509 -nodes -sha256 \
    -newkey rsa:2048 -days 365 -out root_ca.crt -keyout root_ca.key \
    -subj "/C=US/ST=DE/O=MyCert, Inc./CN=mycert.com"
Generating a 2048 bit RSA private key
.....+++
....+++
writing new private key to 'root_ca.key'
-----
generate-expired-certs % openssl req -new -nodes -newkey rsa:2048 \
    -subj "/C=US/ST=DE/O=ExampleOrg, Inc./CN=127.0.0.1" \
    -out server.csr -keyout server.key
Generating a 2048 bit RSA private key
................+++
...............................................+++
writing new private key to 'server.key'
-----
generate-expired-certs % faketime '3 days ago' openssl x509 -req -sha256 -days 1 \
    -in server.csr -CA root_ca.crt -CAkey root_ca.key \
    -CAcreateserial -out server.crt
Signature ok
subject=/C=US/ST=DE/O=ExampleOrg, Inc./CN=127.0.0.1
Getting CA Private Key
```

Check the certificate expiration dates using `openssl x509`. The root_ca is set to start from a week ago, and expire 1 year from the start date. The server certificate is set to start 3 days and expire 2 days ago.

```text
generate-expired-certs % openssl x509 -noout -startdate -enddate -in root_ca.crt
notBefore=Sep 11 21:51:20 2021 GMT
notAfter=Sep 11 21:51:20 2022 GMT

generate-expired-certs % openssl x509 -noout -startdate -enddate -in server.crt
notBefore=Sep 15 21:51:20 2021 GMT
notAfter=Sep 16 21:51:20 2021 GMT
```

You can find the script of the above commands [here](https://github.com/deepns/fun-with-openssl/tree/main/generate-expired-certs)

## Note

**faketime** has some limitations with macOS due to [System Integrity Protection](https://support.apple.com/en-us/HT204899) in releases El Capitan and above. faketime cannot intercept the system calls from programs under the system protected directories. Copy the binaries to a different location or use different binary that is not in the protection location (e.g. `/usr/local/bin/gdate` instead of `/bin/date`)
