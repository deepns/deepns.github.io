---
title: Pretty print json from command line
categories:
    - Tech
tags: 
    - python
    - json
---

I was grepping through some application logs which contained compacted json strings in the log messages. Some of them were too lengthy to fit in a single line, so it was difficult to read the json contents when grepping. I was about to write a small script to pretty print the json contents in the logs. I looked into Python docs to refresh my memory, and that's when I stumbled upon the [**json.tool**](https://github.com/python/cpython/blob/3.6/Lib/json/tool.py) module. Its a simple script that loads json data and dumps in pretty format. Python allows us to run a library module as a script with `-m` option. So I can run the `json.tool` module as a script. That made my work much easier. It allows reading from regular files as well as standard input and writes to regular files or standard output too. So all I had to was to extract the json text with proper pattern matching with grep and pipe the extracted content to `json.tool`. This tool also provides an option to sort the keys as well.

```text
% python -m json.tool --help
usage: python -m json.tool [-h] [--sort-keys] [infile] [outfile]

A simple command line interface for json module to validate and pretty-print
JSON objects.

positional arguments:
  infile       a JSON file to be validated or pretty-printed
  outfile      write the output of infile to outfile

optional arguments:
  -h, --help   show this help message and exit
  --sort-keys  sort the output of dictionaries alphabetically by key
```

Here is an example usage of this tool.

```text
% echo '{"[markdown]": {"editor.quickSuggestions": {"other": true,"comments": false,"strings": false}}}' | python -m json.tool
{
    "[markdown]": {
        "editor.quickSuggestions": {
            "other": true,
            "comments": false,
            "strings": false
        }
    }
}
```

With `--sort-keys` option,

```text
% echo '{"[markdown]": {"editor.quickSuggestions": {"other": true,"comments": false,"strings": false}}}' | python -m json.tool --sort-keys
{
    "[markdown]": {
        "editor.quickSuggestions": {
            "comments": false,
            "other": true,
            "strings": false
        }
    }
}
```

My machine currently has python 3.6 only, so it is missing some new options (e.g. indenting, compacting etc.) added in the latest version of this tool. Check out the source code of the [3.8 version](https://github.com/python/cpython/blob/3.8/Lib/json/tool.py) and the [master](https://github.com/python/cpython/blob/master/Lib/json/tool.py) of json.tool.
