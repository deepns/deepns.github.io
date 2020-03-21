---
title: Enable quick suggestions for Markdown in VS Code
categories:
    - Tech
tags:
    - VSCode
    - markdown
---

I had been using VS Code for quite sometime for my personal projects. The quick suggestion and code completion feature of VS Code come in handy in many cases. I was working on a long markdown file one day and wished quick suggestion showed up here as well. The quick suggestion works even in a plain text file, so I was wondering why it didn't work in a markdown file.

I looked into [Intellisense](https://code.visualstudio.com/docs/editor/intellisense) page for reference and realized that it is enabled only for certain languages (TypeScript, JavaScript, HTML and some more) by default. Support for other languages (e.g. Python, C, C++ etc.) are managed by their corresponding extension. I had to explicitly turn it on for Markdown file by setting the `editor.quickSuggestions` options in the `settings.json` file. The flags `comments` and `strings` can be set to `true` if we want quick suggestions for comments and string literals.

```json
"[markdown]": {
    "editor.quickSuggestions": {
        "other": true,
        "comments": false,
        "strings": false
    }
}
```

The [docs](https://code.visualstudio.com/docs/editor/intellisense#_customizing-intellisense) has all the necessary details on different options in Intellisense that we can customize. Quick suggestions can be sometime be annoying too, so I didn't want to enable globally in VS Code. I updated the `settings.json` only in the workspace I wanted to, instead of updating the user settings. That way, I can toggle the settings without affecting other projects that are open in Code.
