---
title: Updating google analytics tag from universal to analytics-4 in minimal mistakes
category:
    - Tech
tags:
    - google
    - learning
    - github
header:
  teaser: /assets/images/teasers/google-analytics.jpeg
---

I have been using Google Universal analytics tag with my blog for a while. Google has been pushing the users to move to Google Analytics 4 from the current Universal Analytics for almost a year. Admittedly, I use it in a very basic ways just to monitor the page visits, so didn't bother much to do the required update. I had been using `google-universal` as the provider in the jekyll config.

```yaml
analytics:
  provider: "google-universal"
  google:
    tracking_id: "UA-908945612-1"
```

To move to GA-4, I had to

- update the provider to **google-gtag**
- get the measurement ID from the data stream (as explained [here](https://support.google.com/analytics/answer/9539598#find-G-ID))

![get-measurement-id](https://storage.googleapis.com/support-kms-prod/4vzOnPW93ZjrGTZKfeIJYHXXPmpfCmc0UMHy)

```yaml
analytics:
  provider: "google-gtag"
  google:
    tracking_id: "G-TYVCJUF74I"
```

Post update, data from the universal analytics tag didn't seem to be carried over. GA-4 property shows only the data from the new traffic. The home page for GA-4 property does look better than the old one though, with cleaner UI, personalized dashboard and customized insights and recommendations.
