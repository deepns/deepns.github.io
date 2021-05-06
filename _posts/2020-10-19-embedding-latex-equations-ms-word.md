---
title: Embedding LaTeX Equations in MS Word
categories:
    - Tech
tags:
    - learning
    - markdown
    - productivity
    - utilities
---

I have got used to Markdown for most of my notes and sometimes even for delivering presentations at work.  I unwillingly returned to Word to help out my wife on one of her tasks related to her studies. I had to insert some statistics related formula in Word. Its been ages I played with that section of Word so it took some time to figure out. After playing around with the equations and symbols for few minutes, I got so frustrated with the convoluted workflow of inserting various math symbols and that too with different subscripts and superscripts. I basically FU to word and returned to Markdown to insert the equation using [MathJax](https://www.mathjax.org/).  The equations goes some like this:

<p align="center">
<img src="{{site.url}}/assets/images/for-posts/equations.jpg" title="Stat Equation" alt="That Stat Equation">
</p>

With Markdown, I can pretty much type this equation in natural language in a flow. Intellisense in VS Code works great here as well as it provides auto suggestion and completion as I type. The text for the first equation in the above image maps to:

```latex
$n_1 = \frac{(\sigma_1^2 + \sigma_2^2/k)(Z_{1-\alpha/2} +Z_{1-\beta})^2}{\delta^2}$
```

The initial ramp with LaTeX equation may be little steep, but it pays off handsomely in the long run. We can type an equation very similar to how we spell it out. Here is a snapshot from my VS Code.

<p align="center">
<img src="{{site.url}}/assets/images/for-posts/vscode-auto-complete-equations.jpg" title="VS Code AutoComplete Equation" alt="VS Code AutoComplete">
</p>

Later I found out that Word also had a short cut to convert LaTeX equations into Word equations. That came in so handy to move the equations from my markdown notes directly to Word without going through that difficult workflow. With minor edits (such as replacing `{}` with `()`), it was so easy to convert these equations into a readable one.

<p align="center">
<img src="{{site.url}}/assets/images/for-posts/equations2.gif" title="LaTeX to professional format" alt="LaTeX to professional format in MS Word">
</p>

Shortly later, as I explored more, I found out that Word also supports a similar type to convert. Explained in this [link](https://support.microsoft.com/en-us/office/linear-format-equations-using-unicodemath-and-latex-in-word-2e00618d-b1fd-49d8-8cb4-8d17f25754f8). It worked good as typed in the equation box. I still liked the flexibility to the equations into professional format due its multipurpose.
