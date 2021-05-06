---
title: Combine multiple PDF files into one from command line in Mac
categories:
    - Tech
tags:
    - python
    - macOS
    - utilities
---

Recently I downloaded some reference materials that came in a bunch of PDF files. I wanted to stitch them into one file so I can read or print more comfortably. I knew I can do this with the Preview app by drag-and-dropping multiple PDF files in the order I wanted to combine. Since I had few dozen files, I wasn't interested in doing this manually. If Preview can do it, there must be some ways to do that from command line too. That way, I can automate this with a bash script to go over mulitple files. The solution turned out much simpler than I thought, thanks to this [post](https://apple.stackexchange.com/questions/230437/how-can-i-combine-multiple-pdfs-using-the-command-line).

macOS uses the python script `/System/Library/Automator/Combine\ PDF\ Pages.action/Contents/Resources/join.py` to combine multiple PDF into one. The same script can be executed from command line too.

The syntax for this script goes like this: `join.py -o OUTPUT_FILE [FILE1] [FILE2] [FILE3]...`, with options to shuffle pages and also print verbose information to standard error.

Here are the comments, taken from the file.

```python
# join
#   Joing pages from a a collection of PDF files into a single PDF file.
#
#   join [--output <file>] [--shuffle] [--verbose]"
#
#   Parameter:
#
#   --shuffle
#       Take a page from each PDF input file in turn before taking another from each file.
#       If this option is not specified then all of the pages from a PDF file are appended
#       to the output PDF file before the next input PDF file is processed.
#
#   --verbose
#   Write information about the doings of this tool to stderr.
```

Since I had multiple files to combine, I used the [bash command substitution](https://www.gnu.org/software/bash/manual/html_node/Command-Substitution.html) to include files in a specific order when I ran the join script. That worked out great.

```bash
$ /System/Library/Automator/Combine\ PDF\ Pages.action/Contents/Resources/join.py -o notes.pdf $(ls -rt)
```
