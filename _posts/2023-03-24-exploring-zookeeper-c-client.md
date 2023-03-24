---
title: Exploring Zookeeper C Client
category: Tech
tags:
    - zookeeper
    - c
    - programming
    - learning
header:
  teaser: /assets/images/teasers/building-zookeeper-on-macOS.jpg
  caption: "Photo Credit: [Clément Hélardot](https://unsplash.com/@clemhlrdt) on [Unsplash](https://unsplash.com/photos/95YRwf6CNw8)"
---

A short while ago I happened to work on Zookeeper related feature that required the use of Zookeeper C Client library to interact with the ensemble. We ran into many stability issues on the client side, so had to dig deeper to diagnose those issues and fix. Unfortunately ZK C client did't have rich documentation and code comments, so navigating the code was somewhat challenging at the beginning.

The library provides a set of functions for creating and managing ZooKeeper sessions, creating and deleting nodes in the namespace, setting and getting node data, setting watches on nodes to receive notifications of changes, and performing various other operations such as listing child nodes, checking node existence, and setting access control lists.

The code is organized into several modules, including a main client module (zookeeper.c), threading adaptors (st_adaptor.c and mt_adaptor.c), hashtable (zk_hashtable.c) and various utility modules for data serialization, buffer management, logging, and error handling.

Functions in `zookeeper.c` handles communication with the ensemble using ZooKeeper's wire protocol and manages the client's session state, including connection management, session timeouts, and error handling. It also supports SSL/TLS connections to ZooKeeper servers through the use of OpenSSL.

A short rundown of the main functions defined in zookeeper.c:

- **zookeeper_init()**: called to initialize the ZooKeeper client library. It takes a set of connection parameters, such as the host and port of the ZooKeeper ensemble, a timeout value, and a callback function to handle connection state changes. The function returns a zhandle_t handle, which is used to identify the client's session.

- **zookeeper_close()**: called to close the client's session with the ZooKeeper ensemble. It takes a zhandle_t handle as input and returns 0 on success.

- **zookeeper_create()**: used to create a new node in the ZooKeeper namespace. It takes a zhandle_t handle, the path of the node to create, the initial data for the node, a set of flags to specify node creation options, and a callback function to handle completion of the operation. The function returns the path of the newly created node on success.

- **zookeeper_delete()**: used to delete a node from the ZooKeeper namespace. It takes a zhandle_t handle and the path of the node to delete, along with a version number that must match the current version of the node. The function returns 0 on success.

- **zookeeper_set()**: used to set the data associated with a node in the ZooKeeper namespace. It takes a zhandle_t handle, the path of the node to set, the new data for the node, and a version number that must match the current version of the node. The function returns the version number of the newly set data on success.

- **zookeeper_get()**: used to get the data associated with a node in the ZooKeeper namespace. It takes a zhandle_t handle, the path of the node to get, a callback function to handle completion of the operation, and a set of flags to specify node retrieval options.

- **zookeeper_wget()**: similar to zookeeper_get(), but it also registers a watch on the node to receive notifications of changes to the node's data.

- **zookeeper_exists()**: used to check if a node exists in the ZooKeeper namespace. It takes a zhandle_t handle, the path of the node to check, a callback function to handle completion of the operation, and a set of flags to specify node existence check options.

- **zookeeper_wexists()**: similar to zookeeper_exists(), but it also registers a watch on the node to receive notifications of changes to the node's existence status.

**mt_adaptor.c** provides a multithreaded adaptor layer to allow client applications to use the ZooKeeper library in a multithreaded environment. The module uses a global lock to protect access to the ZooKeeper library's internal state, and all calls to the library are made through the adaptor functions provided by mt_adaptor.c.

**zk_hashtable.c** provides a hashtable implementation for storing key-value pairs and uses chaining to handle collisions. Each entry in the hashtable is a struct hash_node, which contains a key-value pair and a pointer to the next node in the chain. Data typically stored in this table are `zhandle_t`, `znode_t` `watcher_registration_t` and `watcher_registration_t`.

I forked the repo to explore the code and [added detailed comments](https://github.com/deepns/zookeeper/blob/addl-comments/) about the code flow, session management, error handling etc. (just for learning reference, not meant to be production grade) so I can always refer to in case of doubts. Full diffs of the change is available [here](https://github.com/apache/zookeeper/compare/master...deepns:zookeeper:addl-comments).
