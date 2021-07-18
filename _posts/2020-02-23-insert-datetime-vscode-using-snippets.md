---
title: Insert date/time using snippets and keyboard shortcuts in VS Code
categories:
    - Tech
tags:
    - vscode
    - markdown
---

I use VS Code for a lot of cases outside code editing too. It works out great for me to take quick notes often in markdown format. One of the actions that I frequently do is to insert the current date and/or time in the document that I'm working on. It isn't a difficult or time consuming action, but having a shortcut to do that would be more convenient. There wasn't any existing keyboard shortcut to do the same. It turns out to be quite simple to do this with the help of [Snippets](https://code.visualstudio.com/docs/editor/userdefinedsnippets). Current date and time can be fetched from the predefined variables.

Snippets can be configured at **workspace** level or **globally** or to a **specific language** too. In this case, I applied only to markdown files. Go to Preferences -> User Snippets (alternatively we can pull this up from command palette as well) and choose markdown. It will then create markdown.json file in the global snippets directory if it doesn't exist already.

Snippets take three parameters:

- prefix - list of strings on which this snippet should be invoked
- body - content to be inserted by the snippet
- description - user readable description about the snippet.

```json
{
    "Insert Current Date": {
        "prefix": ["date", "cdate"],
        "body": "$CURRENT_MONTH/$CURRENT_DATE/$CURRENT_YEAR_SHORT",
        "description": "Insert current date in DD/MM/YY format"
    }
}
```

If IntelliSense is on, then this snippet will automatically show up in suggestions when entering one of the words in the prefix list. Otherwise, it can be manually invoked with Ctlr+Space shortcut.

<img src="{{site.url}}/assets/images/for-posts/insert-date-vscode.gif" title="Inserting current date in vscode using snippets" alt="Inserting current date in vscode using snippets">

A snippet can be invoked with a [keyboard shortcut](https://code.visualstudio.com/docs/editor/userdefinedsnippets#_assign-keybindings-to-snippets) as well. Since this snippet is a super simple one, it can be invoked inline instead of a explicit definition in a snippet file. I found it more convenient to have it a snippet file than inline.

Here is the keybinding definition I use to invoke the snippet I defined above.

```json
{
    "key": "cmd+k /",
    "command": "editor.action.insertSnippet",
    "when": "editorTextFocus",
    "args": {
        "langId": "markdown",
        "name": "Insert Current Date"
    }
}
```
