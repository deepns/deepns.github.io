---
title: Processing JSON data with jq
category:
    - Tech
tags:
    - programming
    - tools
    - api
    - howto
    - learning
header:
  teaser: /assets/images/teasers/processing-json-with-jq.jpg
---

[jq](https://stedolan.github.io/jq/) is an excellent command line tool to operate on JSON data. I have been using it to process, filter and transform json objects for easy inference of the data. Noting down some commonly used operations for my later reference.

- **Syntax** - `jq [options] <filter>`. Reads from stdin by default.
- Filter specifies the expression to apply on the json data.
- `.` - identity filter, output is same as input.

(Using [StackExchange APIs](https://api.stackexchange.com/) to pull some json values here for sample data)

```text
# Listing available tags on StackOverflow
~ % curl -s --compressed "https://api.stackexchange.com/2.2/tags?site=stackoverflow&pagesize=2" | jq '.'
{
  "items": [
    {
      "has_synonyms": true,
      "is_moderator_only": false,
      "is_required": false,
      "count": 2204785,
      "name": "javascript"
    },
    {
      "has_synonyms": true,
      "is_moderator_only": false,
      "is_required": false,
      "count": 1770006,
      "name": "java"
    }
  ],
  "has_more": true,
  "quota_max": 300,
  "quota_remaining": 219
}
```

- `.object` - access `object` in the current stream. `.object1,.object2` to access multiple objects

```text
~ % curl -s --compressed "https://api.stackexchange.com/2.2/sites" | jq '.quota_max,.quota_remaining'
300
216
```

- `.parent.child` - access child of a parent json value. Equivalent to `parent[child]` syntax

Arrays are accessed using `[]` operator

  - `.[]` - access all items in the array
  - `.[i]` - index object at index `i`
  - `.[i:j]` - slice the array between index `i` and `j`.

`https://api.stackexchange.com/2.2/sites` lists the sites supported by StackExchange APIs. Using the results that call to perform some jq operations.

```text
# saving the output to a file for easier access
~ % curl -s --compressed "https://api.stackexchange.com/2.2/sites" > stackexchange_sites  

# Access first site in the list
~ % cat stackexchange_sites | jq '.items[0]'
{
  "aliases": [
    "http://www.stackoverflow.com",
    "http://facebook.stackoverflow.com"
  ],
  "styling": {
    "tag_background_color": "#E0EAF1",
    "tag_foreground_color": "#3E6D8E",
    "link_color": "#0077CC"
  },
  "related_sites": [
    {
      "relation": "meta",
      "api_site_parameter": "meta.stackoverflow",
      "site_url": "https://meta.stackoverflow.com",
      "name": "Meta Stack Overflow"
    },
    {
      "relation": "chat",
      "site_url": "https://chat.stackoverflow.com/",
      "name": "Stack Overflow Chat"
    }
  ],
  "markdown_extensions": [
    "Prettify"
  ],
  "launch_date": 1221436800,
  "open_beta_date": 1217462400,
  "site_state": "normal",
  "high_resolution_icon_url": "https://cdn.sstatic.net/Sites/stackoverflow/Img/apple-touch-icon@2.png",
  "favicon_url": "https://cdn.sstatic.net/Sites/stackoverflow/Img/favicon.ico",
  "icon_url": "https://cdn.sstatic.net/Sites/stackoverflow/Img/apple-touch-icon.png",
  "audience": "professional and enthusiast programmers",
    "site_url": "https://stackoverflow.com",
  "api_site_parameter": "stackoverflow",
  "logo_url": "https://cdn.sstatic.net/Sites/stackoverflow/Img/logo.png",
  "name": "Stack Overflow",
  "site_type": "main_site"
}

# access specific fields of an array item
~ % cat stackexchange_sites | jq '.items[1].name'
"Server Fault"
```

- Filters can be combined using pipe operator `|`. Filter expressions are separated by space.

```text
# api_site_parameter specifies the name of the API to be used in the "site" parameter in StackExchange API requests.

~ % cat stackexchange_sites | jq '.items[] | .api_site_parameter'
"stackoverflow"
"serverfault"
"superuser"
"meta"
"webapps"
"webapps.meta"
"gaming"
"gaming.meta"
"webmasters"
"webmasters.meta"
"cooking"
"cooking.meta"
"gamedev"
"gamedev.meta"
"photo"
"photo.meta"
"stats"
"stats.meta"
"math"
"math.meta"
"diy"
"diy.meta"
"meta.superuser"
"meta.serverfault"
"gis"
"gis.meta"
"tex"
"tex.meta"
"askubuntu"
"meta.askubuntu"
```

- `--raw-output / -r` option outputs the data as raw (without any json formatting). This comes in handy to apply further operations on the data using shell commands.

```text
# list stack exchange sites, starting with S, in sorted order.
~ % cat stackexchange_sites | jq --raw-output '.items[] | .name' | sort | grep "^S"
Seasoned Advice
Seasoned Advice Meta
Server Fault
Stack Overflow
Super User
```

- Can also transform one json stream into another by specifying the structure in `{ key : value}` where `value` is the object to extract from the stream.

```text
# Extracting the site_url from StackExchange sites list
~ % cat stackexchange_sites | jq '.items[0:5] | .[] | { "name" : .name, "site" : .site_url}'          
{
  "name": "Stack Overflow",
  "site": "https://stackoverflow.com"
}
{
  "name": "Server Fault",
  "site": "https://serverfault.com"
}
{
  "name": "Super User",
  "site": "https://superuser.com"
}
{
  "name": "Meta Stack Exchange",
  "site": "https://meta.stackexchange.com"
}
{
  "name": "Web Applications",
  "site": "https://webapps.stackexchange.com"
}
```

- Use `,` operator to feed same input into multiple filters. Comes handy in sequential processing.

```text
~ % cat stackexchange_sites | jq '.items[1:5] | .[].name,.[].site_url'
"Server Fault"
"Super User"
"Meta Stack Exchange"
"Web Applications"
"https://serverfault.com"
"https://superuser.com"
"https://meta.stackexchange.com"
"https://webapps.stackexchange.com"
```

These operations suffice most of my use cases. `jq` also supports more complex queries and operations as explained in the [manual](https://stedolan.github.io/jq/manual).
