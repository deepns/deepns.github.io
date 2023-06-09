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
  teaser: /assets/images/teasers/azure-aci.png
---

A habit that I developed in the recent times is to take a short note about the things I learn at work and in my personal explorations. Something like a flash card note, in a plain text, that is easy to take, remember and revisit. There are plenty of great flash card apps, note taking apps for mobile, web and desktop. No doubt about that. I wanted to reduce the friction and distractions in making a note, so things that require me to switch to my phone or different apps on my desktop can possibly distract me too much from my workflow. I just wanted some structure to the notes I take, so started off with a json file (like this). These are just plain text notes, with probably few hundred entries. And, I could very well use my favorite VS code to maintain those notes, since VS Code is where I spent most of my time with. Days went by, my notes grew in number. While looking for ways I can make the learning better, I thought of bringing my notes more prominent in the places I frequent.

Twitter is one of the main sources of media consumption. So why not bring my notes into my twitter feed periodically so I get to look at them more often? That gave birth to a weekend project - Making a twitter bot to read my notes and tweet them based on my interests. I tagged each note as I took them, so it was easier to choose the ones that mattered to me at that time. It also gave me a choice to tune my bot such a way that certain notes get tweeted with higher probability. After some funtime with Google Cloud Run in the past, I was reading about Cloud Functions. It fitted perfectly into the use case I was working on. I can have the bot run in a schedule through Cloud Scheduler. The number of invocations, CPU time and network egress for my use case were very minimal and fell well under the generous [free limits](https://cloud.google.com/functions/pricing#free_tier). Putting all together, came up with something like below.
