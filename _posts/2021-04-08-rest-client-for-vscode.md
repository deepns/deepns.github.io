---
title: REST Client for VS Code
category:
    - Tech
tags:
    - vscode
    - VSCode
    - programming
    - api
header:
  teaser: /assets/images/teasers/rest-client-for-vscode-teaser.jpg
---

Some times I have had to use REST APIs for configuration and management of hardware and services at work. The usage used to be minimal and the working environment was a terminal application most times, so `curl` was my go to tool to use. Both of them have changed in the recent times. With [remote development support](https://code.visualstudio.com/docs/remote/remote-overview), I have been using VS Code more often than vim on the remote server. I have also been using (and occasianally developing) REST APIs more than before. I wanted an scratch pad kind of place to easily send the requests, read the responses and add my own comments (like a markdown document) with minimal learning curve. Apps like [Postman](https://www.postman.com/) and [Insomnia] are tailor made for API development and work great. I checked out Postman briefly but found the usage to be less friendly for my use case. I stumbled upon [REST Client Extension](https://marketplace.visualstudio.com/items?itemName=humao.rest-client) for VS Code that fit my needs much better.

- The requests are written in plain text, so it can be easily version controlled.
- VSCode supports http language mode that offers additional features (like syntax highlighting, autocomplete) as well.
- Can add custom variables (file level, environment variables, request and response)
- Support at least basic form of authentication

Some sample requests using the REST Client for VSCode (full collection [here](https://gist.github.com/deepns/38c24829361f23c90b3fe74a9af00d13)).

- A simple GET Request

```http
### Get list of sites supported by stackexchange APIs
GET https://api.stackexchange.com/2.2/sites

### Get list of tags by site
GET https://api.stackexchange.com/2.2/tags?site=stackoverflow
```

- GET request with query params

```http
# Query parameters specified one per line.
GET https://api.stackexchange.com/2.2/tags/vscode-extensions/info
    ?site=stackoverflow
```

- Use the request as a variable and refer to it in another request

```http
### Name the request (using @name) and refer to it in a different request
# @name tagsearch
GET https://api.stackexchange.com/2.2/tags?site=askubuntu

### Access values from a request or response in another request
# The general syntax is
# <request-name>.<request|response>.<body|headers>.<path>
# For JSON response, JSONPath syntax (https://goessner.net/articles/JsonPath/)
# is used.
GET "https://api.stackexchange.com/2.2/tags/{% raw %}{{tagsearch.response.body.$.items[0].name}}{% endraw %}/info?site=askubuntu"
#Authorization: Basic base64-user-password
```

- Authenticating with user/password

```http
### Supports different authentication options
# Body can be specified separately from the request
POST  https://example.com/posts
Authorization: Basic username:password

{
    "id": 1,
    "title": "My awesome post",
    "timestamp": 1504932105
}
```

- Using a file level variable

```http
@test_server = dummy.restapiexample.com
POST http://{{test_server}}/api/v1/create
Content-Type: application/json

{
    "name":"Joe",
    "salary":"123456789",
    "age":"23",
}
```

This extension has been very useful to me so far (thanks to the [publisher](https://marketplace.visualstudio.com/publishers/humao)). There are plenty of features that I am yet to explore. Looking forward to a fun drive with this.
