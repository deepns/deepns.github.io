---
title: Tweeting my notes with Google Cloud Functions
category: Tech
tags:
    - programming
    - gcp
    - cloud
    - go
    - python
header:
  teaser: /assets/images/for-posts/tweet-my-notes.jpg
---

A habit that I developed in recent times is to take a short note about the things I learn at work and in my personal explorations. Something like a flash card note, in a plain text, that is easy to take, remember and revisit. There are plenty of great flash card apps, note taking apps for mobile, web and desktop. No doubt about that. I wanted to reduce the friction and distractions in making a note, so things that require me to switch to my phone or different apps on my desktop can possibly distract me too much from my workflow. I just wanted some structure to the notes I take, so started off with a json file (like [this](https://gist.github.com/deepns/909db3c52c319412a014a6025f676f05)). These are just plain text notes, with probably a few hundred entries. And, I could very well use my favorite VS code to maintain those notes, since VS Code is where I spent most of my time with. Days went by, my notes grew in number. While looking for ways I can make the learning better, I thought of bringing my notes more prominent in the places I frequent.

Twitter is one of the main sources of media consumption. So why not bring my notes into my twitter feed periodically so I get to look at them more often? That gave birth to a weekend project - Making a twitter bot to read my notes and tweet a note based on my interests. I tagged each note as I took them, so it was easier to choose the ones that mattered to me at that time. It also gave me a choice to tune my bot in such a way that certain notes get tweeted with higher probability. After some fun time with Google Cloud Run in the past, I was reading about Cloud Functions. It fitted perfectly into the use case I was working on. I can have the bot run in a schedule through Cloud Scheduler. The number of invocations, CPU time and network egress for my use case were very minimal and fell well under the generous [free limits](https://cloud.google.com/functions/pricing#free_tier). Putting all together, I came up with something like below.

<figure>
<img src="{{site.url}}/assets/images/for-posts/tweet-my-notes.jpg"/>
</figure>

A little bit about the individual components:

- **NotesBot**
  - An event driven Cloud Function in Python, to post a note into one or more tweets
  - Gets a random note from the Note Service
  - Processes the note and post them using Tweepy and Twitter v2 API
  - Set to be invoked when a message is posted to the connected pub-sub
  - Tweets are posted [@deeptechnotes](https://twitter.com/deeptechnotes) handle
- A Cloud Scheduler job to post a message to the pub-sub on a cadence (e.g. every 3 hours)
- **Note Service**
  - A HTTP Cloud function in Go to serve a note from my collection. This could have been done with Python/Flask too, went with Go just for some fun as I was learning Go in the recent times. To keep things simple, didn't add any API spec when I started off. Planning to add that soon.
  - Supports different paths to return a random note or multiple notes based on tags specified in the query
  - Having this as a separate service makes it convenient to pull the notes from other possible clients (e.g. a vscode extension to display my notes in a notification pop-up, chrome extension) in future
  - The service is available [here](https://mynotesapp-nxxo6p55tq-uc.a.run.app). Some sample queries:

```console
➜  ~ curl -s "https://mynotesapp-nxxo6p55tq-uc.a.run.app/" | jq                        
{                                                                              
  "id": 9,                                                                     
  "description": "shell - sum numbers from stdin",                                                                                                             
  "tags": [
    "shell",
    "commands",                                                                                                                                                
    "tools"
  ],
  "contents": [
    "# Ways to sum up numbers from stdin or from piped output from previous commands",
    "# Using paste command",
    "$ echo somefile | paste -s -d+ | bc",
    "$ cat nums | paste -sd+ - | bc",
    "# using awk.. substitute $1 with the actual column number",
    "$ cat nums | awk '{sum += $1} END {print sum}'"
  ]
}

➜  ~ curl -s "https://mynotesapp-nxxo6p55tq-uc.a.run.app/notes?tags=vim&limit=1" | jq
[
  {
    "id": 65,
    "description": "vim - show relative and absolute file path",
    "tags": [
      "vim",
      "programming",
      "editor",
      "shortcuts"
    ],
    "contents": [
      "Ctrl+G - shows the relative path of the current file",
      "{n}Ctrl+G - shows the relative path of the nth file in the buffer",
      "1Ctrl+G - shows the absolute path of the current file"
    ]
  }
]
```

It would be interesting to have an vscode extension too, that displays my notes in a pop-up.  May be for another weekend.
