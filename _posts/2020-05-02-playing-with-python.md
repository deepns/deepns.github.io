---
title: Playing with Python
toc: true
categories:
    - Tech
    - Books
tags:
    - programming
    - python
    - books
---

I have been using Python on and off both at work and for my personal projects. Its been a while since I touched it, so I was spending some time reading through the blogs from [Real Python](https://realpython.com/). Few posts after, I ended up buying Dan's book about [Python Tricks](https://www.amazon.com/Python-Tricks-Buffet-Awesome-Features-ebook/dp/B0785Q7GSY). A nifty little book to refresh our knowledge on Python. Through this book, I found lot of useful tips and tricks in Python that I have forgotten over the years and also learnt lot of new things.

<p align="center">
<img src="{{site.url}}/assets/images/for-posts/python-tips-and-tricks_dan-bader.jpg" title="Python Tricks - A buffet of awesome python features by Dan Bander">
</p>

Some key takeaways from this book:

## Argument handling with *args, **kwargs

The operators **\*** and **\*\*** are used to unpack the sequence objects and dictionaries into their individual elements when passed as function arguments. The unpacking can happen in either direction of the function call. The name **\*args** and **\*\*kwargs** are a general convention to denote the variadic positional and keyword arguments in functions.

1. Unpack a sequence/dictionary into individual positional and keyword arguments of a function

```python
>>> def concat(str1, str2, str3, sep=" "):
...     """
...     Conctenate three strings, separated by the given separator. Default separator is a space.
...     """
...     return f'{str1}{sep}{str2}{sep}{str3}'
...
>>> # we could call concat with individual strings like below
...
>>> concat("hello", "foo", "bar")
'hello foo bar'
...
>>> # if the strings are in a sequence object, we could unpack the sequence object into individual arguments
...
>>> strings = ("hello", "foo", "bar")
>>> concat(*strings)
'hello foo bar'
>>> strings = ["hello", "foo", "bar"]
>>> concat(*strings)
'hello foo bar'
>>> # unpack positional and keyword arguments of function using a sequence and dict
...
>>> strings = ["hello", "foo", "bar"]
>>> options = { "sep": ":" }
>>> concat(*strings, **options)
'hello:foo:bar'
>>> # if a dict is unpacked with just *, then only its keys will be used
...
>>> concat(*strings, *options)
'hellosepfoosepbar'
```

2. Pack a variable number of positional arguments into a list and keyword arguments into dictionary object when the function argument uses variadic arguments

```python
def get_directions(start, *stops, **options):
    """
    Get driving directions between starting point and arbitrary number
    of stops, with the given options
    """
    for stop in stops:
        # find_route(start, stop)
        print(f'Finding route between {start} and {stop}')
        start = stop
    if options:
        print("with the route options:",
            ",".join([option + "=" + str(value) for option, value in options.items()]))

>>> get_directions("Seattle", "Kirkland", "Bellevue")
Finding route between Seattle and Kirkland
Finding route between Kirkland and Bellevue

>>> # now passing additional route options in keyword arguments, which are packed
... # into options argument of the function
...
>>> get_directions("Seattle", "Kirkland", "Bellevue", toll=True, highways=False)
Finding route between Seattle and Kirkland
Finding route between Kirkland and Bellevue
with the route options: toll=True,highways=False
```

## Decorators

I found [this post](https://realpython.com/primer-on-python-decorators/) on RealPython to be an excellent intro decorators in Python.

## Generator expression

This is similar to list comprehension, but the generator expression is specified inside parantheses whereas expression for list comprehension is specified within square brackets that we use to create lists. A generator expression can't be reused though.

```python
>>> ascii_vals = (ord(char) for char in 'hello')
>>> type(ascii_vals)
<class 'generator'>
>>> ascii_vals
<generator object <genexpr> at 0x109a10c00>
>>> # iterating the generator object and turning into list
>>> [val for val in ascii_vals]
[104, 101, 108, 108, 111]
>>> # once the iteration on generator expression is complete, further iteration will raise StopIteration
>>> next(ascii_vals)
Traceback (most recent call last):
  File "<stdin>", line 1, in <module>
StopIteration
```

## A Crazy dict expression

Here is the crazy expression.

```python
# There are seemingly three different keys, but the expression evaluates to just one key in the end.
>>> crazy_dict = { True: 'y', 1: 'n', 1.0: 'blah' }
>>> crazy_dict
{True: 'blah'}
```

How did it happen?

**True** is an instance of **bool** class which is a subclass of **int** with a value of `1`. So `True` and `1` are compared equal when tested on their equality. Are their hash values also the same?

```python
>>> help(True)
Help on bool object:

class bool(int)
 |  bool(x) -> bool
 |  
 |  Returns True when the argument x is true, False otherwise.
 |  The builtins True and False are the only two instances of the class bool.
 |  The class bool is a subclass of the class int, and cannot be subclassed.
 |  
 |  Method resolution order:
 |      bool
 |      int
 |      object

>>> True == 1
True
>>> [hash(True), hash(1), hash(1.0)]
[1, 1, 1]
```

The hash value of True, 1 and 1.0 are the same, so we ran into hash collisions. Upon a collision, python updates the old value to the new value, but retains the old key. So `{ True: 'y', 1: 'n' }` becomes `{ True: 'n' }`. Inserting `1.0: 'blah'` into that overwrites the existing value, bringing the dict to `{True: 'blah'}`

## Helpers

`dir()` and `help()` are super helpful to inspect objects and docs for a quick peek while working with the Python interpreter. The docs are available online too, but that requires going to the browser, search for the results and often leads to further distractions.

```python
>>> import dis
>>> help(dis.dis) # this will display the following content

# Help on function dis in module dis:
#
# dis(x=None, *, file=None)
#    Disassemble classes, methods, functions, generators, or code.

```

## ByteCode translation

The module `dis` provides the necessary objects and tools to disassemble python code and see how it translates into assembly instructions. It was fun to inspect `__code__` attribute of function objects to see how the arguments and variables are packed internally.

```python
>>> def add(x, y):
...     z = x + y
...     return z
...
>>> dir(add)
['__annotations__', '__call__', '__class__', '__closure__', '__code__', '__defaults__', '__delattr__', '__dict__', '__dir__', '__doc__', '__eq__', '__format__', '__ge__', '__get__', '__getattribute__', '__globals__', '__gt__', '__hash__', '__init__', '__init_subclass__', '__kwdefaults__', '__le__', '__lt__', '__module__', '__name__', '__ne__', '__new__', '__qualname__', '__reduce__', '__reduce_ex__', '__repr__', '__setattr__', '__sizeof__', '__str__', '__subclasshook__']
>>> add.__code__
<code object add at 0x10de6cc00, file "<stdin>", line 1>
>>> dir(add.__code__)
['__class__', '__delattr__', '__dir__', '__doc__', '__eq__', '__format__', '__ge__', '__getattribute__', '__gt__', '__hash__', '__init__', '__init_subclass__', '__le__', '__lt__', '__ne__', '__new__', '__reduce__', '__reduce_ex__', '__repr__', '__setattr__', '__sizeof__', '__str__', '__subclasshook__', 'co_argcount', 'co_cellvars', 'co_code', 'co_consts', 'co_filename', 'co_firstlineno', 'co_flags', 'co_freevars', 'co_kwonlyargcount', 'co_lnotab', 'co_name', 'co_names', 'co_nlocals', 'co_stacksize', 'co_varnames']
>>> add.__code__.co_consts
(None,)
>>> add.__code__.co_filename
'<stdin>'
>>> add.__code__.co_names
()
>>> add.__code__.co_name
'add'
>>> add.__code__.co_varnames
('x', 'y', 'z')
>>> add.__code__.co_code
b'|\x00|\x01\x17\x00}\x02|\x02S\x00'
>>> import dis
>>> dis.dis(add)
  2           0 LOAD_FAST                0 (x)
              2 LOAD_FAST                1 (y)
              4 BINARY_ADD
              6 STORE_FAST               2 (z)

  3           8 LOAD_FAST                2 (z)
             10 RETURN_VALUE
>>>
```

This book brought back my curiousity in Python and I'm totally enjoying it. I'm following it up with frequent readings from RealPython blogs and also picked up another book on Python.