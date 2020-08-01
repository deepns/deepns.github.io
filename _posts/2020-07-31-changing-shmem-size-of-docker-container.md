---
title: Changing shmem size of a docker container
categories:
    - Tech
tags:
    - programming
    - c
    - linux
    - docker
    - containers
---

Recently, I was playing around with a containerized application having processes using shared memory for communication. It turned out to be a good learning exercise.

I learnt that docker containers are allocated 64M of shared memory by default. The option `--shm-size` is used to set the required size for `/dev/shm` within the container.

Here is a snippet from [Docker documentation](https://docs.docker.com/engine/reference/run/).

```text
--shm-size=""   Size of /dev/shm. The format is <number><unit>. number must be greater than 0. Unit is optional and can be b (bytes), k (kilobytes), m (megabytes), or g (gigabytes). If you omit the unit, the system uses bytes. If you omit the size entirely, the system uses 64m.
```

Running a BusyBox container with default settings.

```text
~ $ docker images
REPOSITORY          TAG                 IMAGE ID            CREATED             SIZE
busybox             latest              018c9d7b792b        4 days ago          1.22MB
~ $ # checking the default size
~ $ docker run -it busybox sh
/ # df -h /dev/shm
Filesystem                Size      Used Available Use% Mounted on
shm                      64.0M         0     64.0M   0% /dev/shm
```

Launching a new container with increased shmem size.

```text
~ $ docker run --shm-size=256m -it busybox sh
/ # df -h /dev/shm
Filesystem                Size      Used Available Use% Mounted on
shm                     256.0M         0    256.0M   0% /dev/shm
```

In a running container, the shmem size can be changed by remounting `/dev/shm` with the required size. This will not persist if the container restarts though. Persisting that with a running container may require more steps as discussed in this [issue](https://github.com/docker/cli/issues/1278).

```text
~ $ docker run --privileged -it busybox sh
/ # df -h /dev/shm
Filesystem                Size      Used Available Use% Mounted on
shm                      64.0M         0     64.0M   0% /dev/shm
/ # mount -o remount,size=512m /dev/shm
/ # df -h /dev/shm
Filesystem                Size      Used Available Use% Mounted on
shm                     512.0M         0    512.0M   0% /dev/shm
```

Pruning the containers after use.

```text
~ $ docker container prune
WARNING! This will remove all stopped containers.
Are you sure you want to continue? [y/N] y
Deleted Containers:
96bc50cec581a5b9704a85b48ea519d9a8ca37576ee715c9a9f82e4da4bd80b3
c7e4b4ad4478aaa54cb2acc5e18d5358a06dd6fd1150f9e239df2c97de4ae7a2
e1bfe52829d68340b89308c4ffffa226d5f6a0e8c17ef35b835c7e98cd1d49f5
526cdabfda0d4599d4ff8ed95b04b56808aa65cc88949afc23afe82fe7a3fc67
c54610631c874f833644a59a4bcaa7f81efd07b882a1177b8f2b23e02fac86b0
017e7b878dd22f1a54163d39eb0510fddfa5c947a562293675f9d95c637ae29c

Total reclaimed space: 291B
```
