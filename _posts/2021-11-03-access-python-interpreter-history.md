---
title: Access python interpreter history
category:
    - Tech
tags:
    - python
    - programming
header:
  teaser: /assets/images/teasers/python-logo.jpg
---

A quick note to myself about accessing the commands from history while working in Python interpreter.

- `readline` module provides the necessary methods to access the history in runtime.
  - See [get_current_history_length](https://docs.python.org/3/library/readline.html#readline.get_current_history_length) and [get_history_item](https://docs.python.org/3/library/readline.html#readline.get_history_item)
- Commands run inside the interpreter are saved by default at `.python_history` in the user's home directory

For convenience, I have added a short helper to my [python startup](https://github.com/deepns/dotfiles/blob/master/pythonrc.py) file, so it is always available during interactive sessions.

```python
import readline

def show_history(num_recent=10):
    """ Show the entries from interpreter history buffer

    Args:
        num_recent (int): Number of entries to show (default:10)
    """
    history_length = readline.get_current_history_length()
    # Index of the underlying history buffer one based
    # https://docs.python.org/3/library/readline.html?highlight=readline#readline.get_history_item
    start = max(1, history_length - num_recent)
    for i in range(start, history_length):
        print("{} {}".format(i, readline.get_history_item(i)))
```
