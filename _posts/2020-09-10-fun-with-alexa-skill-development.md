---
title: Fun with Alexa Skill Development
header:
    image: /assets/images/headers/alexa-echo-jan-antonin-kolar-qQRrhMIpxPw-unsplash.jpg
    caption: "Photo Credit: [Jan Antonin Kolar](https://unsplash.com/@jankolar) on [Unsplash](https://unsplash.com/photos/qQRrhMIpxPw)"
category:
    - Tech
    - Learning
tags:
    - programming
    - fun
    - Alexa Skills
---

While fighting boredom at home due to COVID restrictions, I looked to do something interesting and new.  Having worked on backend systems for most of my projects, I had very little exposure to front end, mobile app development and the likes. I wanted to learning something new but also do not want it to be so intimidating that it would put me off in the half way. I have been using an Echo device for quite some time. My interaction with Alexa is limited to playing music. So thought of extending it little bit and making it work for my needs. 

I am a huge huge fan of [GoodBerry's Frozen Custard](https://www.goodberrys.com/). I have tried almost all of their special flavors that they have on rotation. A word of caution: Their frozen custard is so addictive that you will never visit another ice cream or froyo or custard point ever. 

It has been a habit for few years for me to check the [flavor of the day page](https://www.goodberrys.com/flavor-of-the-day) very often, especially when driving past it. One disadvantage of that page is that entries show up in a calendar format and not very mobile friendly. I even tried to extract the text from the calendar using a ML library, but it didn't work well. So I wanted an Alexa Skill to which I can simply ask to get the flavor of the day. For example, I can ask `What is the flavor tomorrow?`, `What is the flavor this Friday?`, `What's todays flavor?`.  I surprisingly found few skills in the store already published for this purpose. Much to my dismay, all of them are broken and not working at all. They either return invalid response or simply errors. So I decided to write one for myself and publish it.

It took some time to set up the developer environment (AWS account, Alexa developer console, AWS Lambda if hosting using Lambda functions, etc.). I found the [docs](https://developer.amazon.com/en-US/docs/alexa/quick-reference/custom-skill-quick-reference.html) to be super expansive and helpful. The boilerplate code included in the skill itself covers many of the mandatory actions so we can focus on the core functionality of the skill. The primary languages for the Alexa Skills Kit SDK are Node.js and Java. Python SDK is still in beta. I am glad they have at least in beta support as I am more comfortable with Python than the other two SDKs. 

I worked on sample skills such as [City Guide](https://github.com/alexa/skill-sample-python-city-guide) and [Pet Match](https://github.com/alexa/skill-sample-python-petmatch) to familiarize myself with the skill development process and the SDK. That gave a good reference to start my own skill. The end point for Alexa Skill can be any HTTPS endpoint, however many go with an AWS Lambda for ease of simplicity and flexibility. I chose to go with [Alexa Hosted Skills](https://developer.amazon.com/en-US/docs/alexa/hosted-skills/build-a-skill-end-to-end-using-an-alexa-hosted-skill.html) to get started on the fast track. It comes with the following resources:

1. 1 million free AWS Lambda requests, 3.2 million seconds of compute time per month
2. 5 GB of Amazon S3 storage, 20,000 get requests, 2,000 put requests, and 15 GB egress transfer per month
3. 50GB storage for the skill code and 10K git requests per month.

That was way more than what my skill would need. So it was a no brainer to go with Alexa Hosted Skills instead of hosting my own AWS Lambda and S3 buckets. After couple of weekends, I got my skill to a pretty good working state and submitted for approval. My skill **[GoodBerry's Day](https://www.amazon.com/Deep-S-GoodBerrys-Day/dp/B08HQWRXK5/) i**s now officially available in the [Skill Store](https://www.amazon.com/Deep-S-GoodBerrys-Day/dp/B08HQWRXK5/) after passing the certification**.** 

It turned out to be a great learning exercise. I refreshed some of my AWS knowledge, learnt the ASK SDK, basics of Voice UI, [SSML](https://en.wikipedia.org/wiki/Speech_Synthesis_Markup_Language), Alexa Skill certification and many more. I am planning to follow it up with some new features (such as date lookups, reminders, e.g. `Alexa, ask Goodberry's Day to remind me when Pumpkin is available`) regular updates going forward.

## References

- [Alexa Skill Kit  Documentation](https://developer.amazon.com/en-US/docs/alexa/ask-overviews/build-skills-with-the-alexa-skills-kit.html#)
- [ASK SDK for Python](https://github.com/alexa/alexa-skills-kit-sdk-for-python)
- [Developer tools](https://developer.amazon.com/blogs/alexa/post/a4b865ec-e7ac-4d92-a2db-7cb2326c08c2/developer-tools-to-help-you-build-alexa-skills)