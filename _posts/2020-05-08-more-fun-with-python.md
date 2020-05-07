---
title: More fun with Python
toc: true
categories:
    - Tech
tags:
    - programming
    - python
    - books
---

After finishing up [Python Tricks](https://www.amazon.com/Python-Tricks-Buffet-Awesome-Features-ebook/dp/B0785Q7GSY), my interest in Python went up even higher. I continued my quest to learn something new in Python every day as much as possible. I picked up another book this time, [Effective Python](https://www.amazon.com/Effective-Python-Specific-Software-Development-ebook/dp/B00TKGY0GU) by Brett Slatkin. Lots of cool techniques, patterns and practices in Python presented in easy to consume portions.

<p align="center">
<img src="{{site.url}}/assets/images/for-posts/effective-python_brett-slatkin.jpg" title="Effective Python - By Brett Slatkin">
</p>

I have been only through few chapters in the book so far and I thoroughly enjoying it. I started making some notes for myself about the chapters where I find something interesting or useful. This greatly helps me in retaining what I learn and also makes it easy to recall when a situation to use what I learn arises.

## Enforce clarity with keyword only arguments

Functions accepting keyword arguments are susceptible to bugs when the callers pass the values to keyword arguments through positional values.

Consider the below module. It has a simple function `log` that prints a given message to standard output and takes two options.

```python
from datetime import datetime
from os import path
import inspect
import sys

def log(msg, logerr, verbose):
    """
    Logs a message to standard output.
    If logerr is True, logs the message to standard error as well.
    If verbose is True, add additional context about the caller.
    """
    callerinfo = ""
    timestamp = str(datetime.now())

    if verbose:
        stack = inspect.stack()
        if len(stack) >= 2:
            callerinfo = "[{}:{}:{}]".format(
                            path.basename(stack[1].filename),
                            stack[1].lineno,
                            stack[1].function)

    print("{}|{}|{}".format(timestamp, callerinfo, msg))

    if logerr:
        print("{}|{}|{}".format(timestamp, callerinfo, msg), file=sys.stderr)
```

With this signature, callers to the `log` function have to specify both the options on each call. In cases like this, it is often easy for the developers to misinterpret and pass unintended values to these options. We could change the positional arguments into keyword arguments and specify a default value to them.

```python
def log(msg, logerr=False, verbose=False):
    """
    Logs a message to standard output.
    If logerr is True, logs the message to standard error as well.
    If verbose is True, add additional context about the caller.
    """
    ...
```

This will allow the callers to call `log` without specifying any or some of the options. But this still doesn't prevent us from passing in values to keyword arguments through positional values.

```python
>>> log("testing log")
2020-05-07 01:36:03.886528||testing log
>>> log("testing log", False, True)
2020-05-07 01:36:08.216705|[<stdin>:1:<module>]|testing log
```

Python3 provides a way to enforce that certain arguments to be specified only through keyword arguments. This makes the programmer's intent explicit and makes it easy for the callers to follow the intended design of the callee function. With a `*` after the positional arguments, all the following arguments are treated as keyword-only arguments. [PEP 3102](https://www.python.org/dev/peps/pep-3102/) talks about this in detail.

Here is the new signature.

```python
def log(msg, *, logerr=False, verbose=False):
    """
    Logs a message to standard output.
    If logerr is True, logs the message to standard error as well.
    If verbose is True, add additional context about the caller.
    """
    ...
```

Few sample invocations with the new signature.

```text
>>> log("testing log without keyword args")
2020-05-07 01:38:53.458642||testing log without keyword args
>>> log("testing log without keyword args", False, True)
Traceback (most recent call last):
  File "<stdin>", line 1, in <module>
TypeError: log() takes 1 positional argument but 3 were given

>>> log("testing log with keyword args..", verbose=True)
2020-05-07 01:42:35.484216|[<stdin>:1:<module>]|testing log with keyword args..
>>> log("testing log with keyword args..", verbose=True, logerr=True)
2020-05-07 01:42:55.393846|[<stdin>:1:<module>]|testing log with keyword args..
2020-05-07 01:42:55.393846|[<stdin>:1:<module>]|testing log with keyword args..
```

## Be defensive when iterating over arguments

Functions iterating over input arguments multiple times may see strange behavior if the arguments are iterators or generators. The iterators could be exhausted after one full iteration, leaving no values in the next iteration.

In the below example of computing standard deviation, we iterate over the elements in data twice. Once to calculate the sum and once to calculate the variance.

If the input data is an iterator or generator, then it will be exhausted after calculating the sum of the values. Call to `sum` in the variance will return 0 since iterator would be empty, thus causing the standard deviation also to be empty.)

```python
import math
def standard_deviation(data):
    """ Returns the standard deviation of the values in given data """
    sum_data = 0
    for N, x in enumerate(data, start=1):
        sum_data += x
    mean = sum_data/N
    variance = (1/(N-1)) * sum(math.pow((x - mean), 2) for x in data)
    return math.sqrt(variance)
```

Running it through the python interpreter.

```python
>>> num_list = [random.randint(1, 100) for _ in range(10)]
>>> num_iter = iter(num_list)
>>> standard_deviation(num_list)
31.317194425214186
>>> standard_deviation(num_iter) # WRONG RESULT!!!
0.0
>>> # making a generator and passing into standard_deviation()
>>> num_gen = (random.randint(1, 100) for _ in range(10))
>>> standard_deviation(num_gen) # WRONG HERE TOO!!!
0.0
```

This can be handle in few ways:

- Check that argument is not an iterator. `iter(iterator)` will return the iterator itself. We can use `iter(arg) is iter(arg)` to find whether the argument is an iterator or not and raise appropriate error.
- The argument can be an iterable or a container class that implements the iterator protocol in case of user defined data types or a non-iterable data type.

Here is an example with a container class reading input from a file using a generator wrapped in the iterator.

```python
import math

class Reader:
    """ A container class to read data from file with one integer per line """
    def __init__(self, path):
        self.path = path

    def __iter__(self):
        with open(self.path) as source:
            for line in source:
                yield int(line.strip())

def standard_deviation(data):
    """ Returns the standard deviation of the values in given data """
    if iter(data) is iter(data):
        raise ValueError("data must be an iterable")
    sum_data = 0
    for N, x in enumerate(data, start=1):
        sum_data += x
    mean = sum_data/N
    variance = (1/(N-1)) * sum(math.pow((x - mean), 2) for x in data)
    return math.sqrt(variance)

# Create a reader object that opens the file and returns one line at a time
print(standard_deviation(Reader("subj1.txt")))
print(standard_deviation(Reader("subj2.txt")))

# list is an iterable object, so it will work just fine
subj3 = [56, 22, 102, 244, 98, 150]
print(standard_deviation(subj3))

# This will raise ValueError, since iter() will return
# the list_iterator object associated with the list.
print(standard_deviation(iter(subj3)))
```

## Prefer exceptions over returning None from functions

Functions that return None to indicate special meaning are error prone because None and other special values (empty list, 0, empty string, empty dict etc.) equates to False in Python.

Consider this below example.

```python
import math
def quadratic_roots(a, b, c):
    try:
        x1 = (-b + math.sqrt(abs(b**2 - 4*a*c))) / (2*a)
        x2 = (-b - math.sqrt(abs(b**2 - 4*a*c))) / (2*a)
    except ZeroDivisionError as ze:
        return None, None
    else:
        return x1, x2
```

If the return values of this function are used in conditional checks, then roots with values 0 and error cases where `None` is returned will both equate to `False`. That will lead to hard to find bugs in the code.

```python
>>> x, y = quadratic_roots(0, 10, 2)
>>> if x and y:
...     print(x, y)
...
>>> x, y = quadratic_roots(4, 16, 0) # this is a valid call, with roots 0 and -4
>>> if x and y:
...     print(x, y)
...
>>>
```

In such cases, it is better to raise appropriate errors to handle invalid values than returning `None`. This will enforce the callers to take appropriate action for error cases and also differentiate it from values that may equate to `False`.

```python
import math
def quadratic_roots(a, b, c):
    if a == 0:
        raise ValueError("Invalid coefficient a({})".format(a))

    x1 = (-b + math.sqrt(abs(b**2 - 4*a*c))) / (2*a)
    x2 = (-b - math.sqrt(abs(b**2 - 4*a*c))) / (2*a)
    return x1, x2
```

## try/except/else/finally

A sample template of try/except/else/finally statements.

```python
foo()
try:
    bar() # bar can raise multiple errors
except ValueError:
    # catch the ValueError raised from bar()
    # all other errors propagated to the caller
    pass
else:
    # no errors raised in the try block.
    # do the follow up processing
    pass
finally:
    # run the finally block irrespective of whether
    # an error was raised in the try block or not
    pass
```

Applying this template to handle a case of opening a file, reading from it and writing to it.

```python
def add_flavor(flavor: str):
    """ Add a flavor to flavors list if flavor doesn't exist already """
    fh = open("flavors.json", "r+") # may raise IOError, needs to be handled by the caller.
    try:
        data = json.loads(fh.read())
    except ValueError as ve:
        print("Error in reading from the file: {}".format(ve))
    else:
        # add the new flavor to flavors list
        flavors = data["flavors"]
        if flavor not in flavors:
            flavors.append(flavor)
            fh.seek(0)
            fh.write(json.dumps(data, indent=2))
    finally:
        # close the file handle if the file was successfully opened.
        fh.close()
```

## Iterating with zip

Use the built-in function **zip** to iterate over multiple iterators simultaneously. **zip** in Python3 combines the iterators and produces a lazy generator that yields a tuple with values from the zipped iterators. Whereas in Python2, zip generates a list of tuples with values from the iterators. That can be memory intensive on large lists, so use `itertools.izip` instead when using Python2.

```python
>>> lengths = (random.randint(1, 100) for _ in range(10))
>>> breadths = (random.randint(1, 100) for _ in range(10))
>>> areas = (length * breadth for length, breadth in zip(lengths, breadths))
>>> list(areas)
[851, 3827, 2232, 451, 2925, 913, 4745, 2584, 6880, 60]
```

In general, zip works great with iterators of equal length. zip stops iterating when any of the iterator is exhausted. This may cause strange behaviors when working with iterators of different lengths. To iterate until at least one of the iterator is producing output, use `itertools.zip_longest

```python
>>> # shrinking the breadth list..stops zipping when breadths generator stops iteration
...
>>> lengths = (random.randint(1, 100) for _ in range(10))
>>> breadths = (random.randint(1, 100) for _ in range(5))
>>> areas = [length * breadth for length, breadth in zip(lengths, breadths)]
>>> areas
[4851, 3500, 3825, 2610, 2881]

>>> # using zip_longest this time
...
>>> lengths = (random.randint(1, 100) for _ in range(10))
>>> breadths = (random.randint(1, 100) for _ in range(5))
>>> areas = [length * (breadth if breadth else 0) for length, breadth in itertools.zip_longest(lengths, breadths)]
>>> areas
[1815, 1632, 2211, 8835, 3321, 0, 0, 0, 0, 0]
```

## Generator expressions over list comprehensions

List comprehensions are compact and convenient, but they come at a cost of holding all the items in the list in memory. When iterating over large files or a network socket, this can become quickly become problematic and consume too much space in memory. Generator expressions solves this problem by creating a generator object with the given expression that yields one item at a item. Generator expressions can also be chained together where result of one expression is consumed by another (with each iterator advancing one at a time). It must be noted that generator expressions are stateful. So they can't be reused.

```python
>>> odds = (x for x in range(1, 20) if x%2 == 1)
>>> square_of_odds = (x**2 for x in odds)
>>> type(odds)
<class 'generator'>
>>> odds
<generator object <genexpr> at 0x10bb3ab10>
>>> type(square_of_odds)
<class 'generator'>
>>> list(square_of_odds)
[1, 9, 25, 49, 81, 121, 169, 225, 289, 361]
```

## Prefer enumerate over range

`range(iterable)` creates a range object that iterates over the given iterable. If we want to get the item index as well while iterating, we have to keep the index counter separately. `enumerate(iterable)` wraps the iterable with a lazy generator and yields a pair containing a count and the value yielded by the iterable. The default starting value is 0, but can be overridden by setting the `start` argument to the desired value when creating the enumerator.

```python
>>> for index, value in enumerate(range(1, 10, 2), start=1):
...     print(f"{index}: {value}")
...
1: 1
2: 3
3: 5
4: 7
5: 9
```

## Docstrings

Docstrings can be attached to **functions, classes and modules**. It can be retrived by accessing **__doc__** attribute. See [PEP](https://www.python.org/dev/peps/pep-0257/) for docstring conventions.

### Module documentation

A string literal specified at the first statement in a source file. First line is a brief description of the module. Paragraphs that follow the first line can include additional details (e.g. functions, classes, command line usage etc.) about the module.

### Class documentation

Similar to module level, each class should also have a doc string. First line of the literal gives an one-liner description of the classes. Paragraphs that follow can include details like subclassing restrictions, public attributes.

### Function documentation

For simple functions (e.g. ones that has no arguments or return value, or only one argument), an one liner description is probably functions. If the function signature is not simple (e.g. there are multiple arguments, arguments with default values, variadic arguments, a generator function etc.), we should also include details about them in the doc string. Also, specify details of the return value and possible exception the function may throw.

[doctest module](https://docs.python.org/3/library/doctest.html) makes it easy to exercise usage examples embedded in docstrings to ensure source code and documentation are in sync.
