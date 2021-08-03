---
title: Using Python APIs in GDB
category:
    - Tech
tags:
    - gdb
    - python
    - programming
header:
  teaser: /assets/images/teasers/sigmund-jbwFv4chusE-unsplash.jpg
  caption: "Photo Credit: [Sigmund](https://unsplash.com/@@sigmund) on [Unsplash](https://unsplash.com/photos/jbwFv4chusE)"
---

Debugging can be so much fun and sometimes can be very frustrating. Especially when debugging cores from large applications, there can be so many structures that we have to examine to understand the state of the application and draw conclusions based on how various components within the applications interact. It is very much like a forensic investigation. GDB scripts are so helpful and very much needed in such situations. However, scripting with the traditional gdb commands and language can be painful. Extracting structured info out of large datatypes in the core can be cumbersome.

[Python APIs](https://sourceware.org/gdb/onlinedocs/gdb/Python-API.html) makes it much easier to work with and complements the standard gdb functionality very well. The values in the inferior program are provided in an object of type gdb.Value. For classes and structs, gdb.Value acts like a dict where struct members are maintained as gdb.Field objects and can be accessed as `value["field"]` (equivalent to value.field or value->field).

Here is a sample program.

```c++
#include <stdio.h>
#include <stdlib.h>
#include <time.h>
#include <strings.h>
#include <sys/time.h>

#define NAMELEN 64

typedef struct node {
    int id;
    char name[NAMELEN];
    time_t creation_time;
    struct node *left;
    struct node *right;
} node_t;

typedef short bool;
#define true 1
#define false 0

node_t *create_node(char *name) {
    static int id = 0;
    node_t *node = malloc(sizeof(node_t));
    node->id = id++;
    snprintf(node->name, NAMELEN, "%s", name);

    node->creation_time = time(NULL);
    node->left = NULL;
    node->right = NULL;
    return node;
}

void free_node(node_t *node) {
    if (!node) {
        return;
    }

    node->left = NULL;
    node->right = NULL;
    free(node);
}

void print_node(node_t *node, int recurse) {
    if (!node) {
        return;
    }

    printf("id=%d, name=%s, creation_time(secs)=%lu, creation_time=%s",
        node->id, node->name, node->creation_time, ctime(&node->creation_time));

    if (recurse) {
        print_node(node->left, true);
        print_node(node->right, true);
    }
}

node_t *insert_left(node_t *node, char *name)
{
    if (!node) {
        return NULL;
    }

    if (!node->left) {
        node->left = create_node(name);
    }
    return node->left;
}

node_t *insert_right(node_t *node, char *name)
{
    if (!node) {
        return NULL;
    }

    if (!node->right) {
        node->right = create_node(name);
    }
    return node->right;
}

int main() {
    node_t *root = create_node("root");
    insert_left(root, "X");
    insert_right(root, "Y");
  
    print_node(root, true);
    
    free_node(root->left);
    free_node(root->right);
    free_node(root);

    return 0;
}
```

## Using Python GDB APIs when debugging with gdb

Python commands can be run using

1. `python <command>` (or shortcut `py`)
2. `python-interactive` (or shortcut `pi`)

Python APIs are available in the module `gdb`. This module is automatically imported by gdb for use in scripts evaluated by the python command. When exiting from an interactive session, exit using `Ctrl+D` as calling `exit()` would cause the gdb session as well to quit.

```text
(gdb) py import sys
(gdb) py print(sys.version)
3.8.10 (default, Jun  2 2021, 10:49:15) 
[GCC 9.4.0]
(gdb) pi
>>> import os
>>> print(os.path.dirname(gdb.__file__))
/usr/share/gdb/python/gdb
>>> print(os.listdir(os.path.dirname(gdb.__file__)))
['printer', 'types.py', 'FrameDecorator.py', 'prompt.py', 'xmethod.py', 'FrameIterator.py', 'function', 'command', 'frames.py', 'unwinder.py', '__init__.py', 'printing.py']
>>>
```

`gdb.parse_and_eval` evaluates the expression, based on the standard scoping rules and returns the result in a gdb.Value object.

```text
Breakpoint 1, insert_right (node=0x4052a0, name=0x402045 "Y") at tree.c:69
69          if (!node) {

(gdb) p node
$1 = (node_t *) 0x4052a0
(gdb) p *node
$2 = {
  id = 0,
  name = "root", '\000' <repeats 59 times>,
  creation_time = 1627959891,
  left = 0x405310,
  right = 0x0
}

(gdb) py node = gdb.parse_and_eval("node")
(gdb) py print("id={}, name={}, creation_time={}".format(node["id"], node["name"], node["creation_time"]))
id=0, name="root", '\000' <repeats 59 times>, creation_time=1627959891
(gdb) 
```

Values from gdb history are obtained using `gdb.history()` by passing appropriate index. `gdb.history` can also take negative indices similar to lists and return values at index from the end.

```text
(gdb) print node->left
$3 = (struct node *) 0x405310
(gdb) py print(gdb.history(3))
0x405310
(gdb) py print(gdb.history(3)["name"])
"X", '\000' <repeats 62 times>
```

New GDB CLI commands can be implemented by extending gdb.Command. The example at the end of [this page](https://sourceware.org/gdb/onlinedocs/gdb/Commands-In-Python.html#Commands-In-Python) shows how easy it is to add a new CLI command. This way we can extend the CLI with lot more capabilities (e.g. parsing CLI arguments with ArgumentParser). Here is an example.

```python
class ShowNodes(gdb.Command):
    """Show info about node object"""

    def __init__(self):
        super(ShowNodes, self).__init__("show-nodes", gdb.COMMAND_USER)

    def parse_args(self, args):
        try:
            parser = argparse.ArgumentParser(description=ShowNodes.__doc__)
            parser.add_argument("-a", "--addr", help="Address of the node")
            parser.add_argument("-v", "--varname", help="Name of the variable")
            parser.add_argument("-i", "--index", help="Index of the variable from gdb history")
            parsed_args = parser.parse_args(args)
            return parsed_args
        except(SystemExit):
            # parse_args throws SystemExit when the args are 
            # invalid or help is needed.
            return None

    def invoke(self, argument, from_tty):
            # gdb.string_to_argv converts argument into sys.argv style
            argv = gdb.string_to_argv(argument)
            args = self.parse_args(argv)

ShowNodes()
```

These CLI commands can be defined a separate `.py` file and sourced in when needed.

```text
(gdb) source tree-gdb-scripts.py 
(gdb) show-nodes --help
usage: [-h] [-a ADDR] [-v VARNAME] [-i INDEX]

Show info about node object

optional arguments:
  -h, --help            show this help message and exit
  -a ADDR, --addr ADDR  Address of the node
  -v VARNAME, --varname VARNAME
                        Name of the variable
  -i INDEX, --index INDEX
                        Index of the variable from gdb history

(gdb) show-nodes -a 0x402045
id=16777305, name=d, timestamp=-7493989774290583565
(gdb) show-nodes -v node
id=0, name=root, timestamp=1627963459
```

More details on this example is available [here](https://github.com/deepns/fun-with-gdb-python/blob/main/tree-gdb-scripts.py). For many smaller works, we can simply define python functions and source them in instead of adding new CLI commands. The python functions can be invoked with `python <function(args)>` as usual. There are lot more functionalities available with [Python APIs for GDB](https://sourceware.org/gdb/onlinedocs/gdb/Python-API.html) for advanced debugging.
