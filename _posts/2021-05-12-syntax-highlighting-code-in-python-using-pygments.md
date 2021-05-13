---
title: Syntax Highlighting in python using pygments
category:
    - Tech
tags:
    - programming
    - markdown
    - python
    - json
    - howto
header:
  teaser: /assets/images/teasers/syntax-highlighting.png
---

I was working on a script where I had to output some markdown and json formatted content to the terminal. I thought it would be prettier to print that with syntax highlighting than with no highlighting. [Pygments](https://pygments.org/) package worked great to my needs.

```text
 -------          -------          -----------        -----------------
 | code | ===>   | lexer |  ===> | formatter  | ===> | highlighted code |
 -------          -------          -----------        -----------------
```

Pygments supports tens of programming, template and markup languages. There is a lexer available for each of the supported language. The lexer parses the code into tokens, identifies the semantics represented by the tokens and streams it to the formatter. The formatter takes the token stream and writes to the output with the given style.

Here is a sample markdown text.

```text
markdown_text = """
# Heading 1

## Heading 2

This is `inline code`.

```c
// fenced code block
void foo() {
    printf("bar");
}
```\

### Lists

- **bold**
- *italic*

#### Checklists

- [ ] TBD
- [x] Done
"""

```

The above content can be printed to the terminal with markdown syntax highlighting as below.

```python
from pygments import highlight
from pygments.lexers import get_lexer_by_name

# Formatting the output to be sent to a terminal
# Hence using Terminal256Formatter. Many other formatters 
from pygments.formatters import Terminal256Formatter, HtmlFormatter

# Using my favorite style - monokai
print(highlight(markdown_text, 
                lexer=get_lexer_by_name("markdown"), 
                formatter=Terminal256Formatter(style="monokai")))
```

The list of available styles can be obtained `pygments.styles.get_all_styles`

```python
from pygments.styles import get_all_styles
print(list(get_all_styles()))

# styles available as of pygments 2.8.1.

# ['default', 'emacs', 'friendly', 'colorful', 'autumn', 'murphy', 'manni', 
# 'material', 'monokai', 'perldoc', 'pastie', 'borland', 'trac', 'native', 
# 'fruity', 'bw', 'vim', 'vs', 'tango', 'rrt', 'xcode', 'igor', 'paraiso-light',
# 'paraiso-dark', 'lovelace', 'algol', 'algol_nu', 'arduino', 'rainbow_dash',
# 'abap', 'solarized-dark', 'solarized-light', 'sas', 'stata', 'stata-light', 
# 'stata-dark', 'inkpot', 'zenburn']
```

Likewise, there is a lexer available for `json` too. Here is an example to print a json formatted content with syntax highlighting.

```python
import json

data = {
    "year" : 2020,
    "sucks": True
}

# Convert object into json formatted string using json.dumps

data_with_syntax_highlighting = highlight(
                code=json.dumps(data, indent=2), 
                lexer=get_lexer_by_name("json"), 
                formatter=Terminal256Formatter(style="monokai"))

# with syntax highlighting, the raw string would like below.
# '\x1b[38;5;15m{\x1b[39m\n\x1b[38;5;15m  \x1b[39m\x1b[38;5;197m"year"\x1b[39m\x1b[38;5;15m:\x1b[39m\x1b[38;5;15m \x1b[39m\x1b[38;5;141m2020\x1b[39m\x1b[38;5;15m,\x1b[39m\n\x1b[38;5;15m  \x1b[39m\x1b[38;5;197m"sucks"\x1b[39m\x1b[38;5;15m:\x1b[39m\x1b[38;5;15m \x1b[39m\x1b[38;5;81mtrue\x1b[39m\n\x1b[38;5;15m}\x1b[39m\n'
print(data_with_syntax_highlighting)
```

Combined output of the above two examples

![syntax-highlighting](/assets/images/for-posts/pymentize.jpg)
