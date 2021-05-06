---
title: Adding Custom Shortcuts in iOS
header:
    teaser: "/assets/images/teasers/adding-custom-shortcuts-in-ios.png"
category:
    - Tech
tags:
    - programming
    - utilities
    - productivity
    - iOS
---

[Shortcuts](https://support.apple.com/guide/shortcuts/shortcuts-at-a-glance-apdf22b0444c/ios) was introduced in iOS 12.0 a couple years ago. I didn't pay much attention to it back then. As I continued using iOS 12, I became used to the Siri suggested shortcuts. iOS did a decent job of automating our actions based on the usage and suggesting them at appropriate points (sometimes it was quite off too. Got to admit that.).

Off late I have been poking around adding my own shortcuts and automation in iOS to automate some of my common workflow in using the phone. Like any other development work, it took considerably more time to develop the automation than it takes to do the job once. So it is quite common for anyone to ignore the automation and take the easy path of just doing things manually. In many cases, automation saves a lot of time and improves our productivity in the long run.

[Here](https://www.icloud.com/shortcuts/166deff5193843268fb8a30538934f89) is a shortcut that I wrote recently to automate parts of my morning routine.

- Start a **timer** to meditate
- Turn on **Do Not Disturb**
- Turn off **Do Not Disturb** when the timer expires
- Log the details under **Mindfulness** category in **Health** app

<figure class="align-center" style="width: 360px">
    <img src="{{site.url}}/assets/images/for-posts/ios_shortcuts_mindful.gif" title="Custom Shortcuts in iOS14"/>
</figure>

If I were to do the above actions manually, it would easily take a couple of dozen taps and multiple app switches (Clock, Control Center, Health). Sometimes I tend to forget to turn back on DND. I can now do all these in a single tap, by grouping them under a shortcut. It's good that iOS made the shortcuts shareable, making it much more usable and accessible. You can open [this](https://www.icloud.com/shortcuts/166deff5193843268fb8a30538934f89) and easily add additional actions (such as *Show Calendar*, *Show Reminders*) to append your routines.

iOS provides a lot of ways to run a shortcut:

- Siri (Invoke Siri and say the Shortcut name)
- From the **Shortcuts** app
- Add a shortcut to **Home Screen** and run from there
- **Shortcuts** widgets

Additionally you can also enable [personal automation](https://support.apple.com/guide/shortcuts/create-a-new-personal-automation-apdfbdbd7123/ios) to have the shortcuts run based on a particular trigger.

**Note:** If you want to add external Shortcuts (like [this](https://www.icloud.com/shortcuts/166deff5193843268fb8a30538934f89)) on your phone, you will have to enable **Settings->Shortcuts->Allow Untrusted Shortcuts**.
