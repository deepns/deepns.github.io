---
title: Switch focus between terminal and editor tabs in VS Code
category:
    - Tech
tags:
    - programming
    - vscode
    - shortcuts
header:
  teaser: /assets/images/teasers/syntax-highlighting.png
---

Noting down some keyboard shortcuts that I use to switch between editor tabs and the integrated terminal in VS Code.

I usually keep the terminal maximized most of the times, so needed a shortcut to switch back and forth between the editor and terminal. The command `workbench.action.terminal.toggleTerminal` toggles the terminal view.

```json
{
    "key": "cmd+`",
    "command": "workbench.action.terminal.toggleTerminal"
}
```

Sometimes I have both the editor and the terminal open in parallel, so I can run something on the terminal while I continue making changes to the file in the editor. Toggling the terminal view in this case is quite an interruption to the workflow. I can switch back to the editor tabs using the default shortcuts (`Ctrl+<tab number>` - e.g. `Ctrl+1` invokes the command `"workbench.action.openEditorAtIndex1"`). That requires remembering the tab numbers. Found this nifty solution in the [stackoverflow thread](https://stackoverflow.com/questions/42796887/switch-focus-between-editor-and-integrated-terminal-in-visual-studio-code) that helps to switch the focus between the terminal and editor tabs.

```json
{ 
    "key": "ctrl+`",
    "command": "workbench.action.terminal.focus"
},
{
    "key": "ctrl+`",
    "command": "workbench.action.focusActiveEditorGroup",
    "when": "terminalFocus"
}
```

<figure>
<img src="{{site.url}}/assets/images/for-posts/vscode-switch-focus-editor-terminal.gif" title="Switch focus between terminal and editor tabs" alt="Switch focus between terminal and editor tabs">
</figure>

These kind of customizations is what makes working with vscode even more joyful.
