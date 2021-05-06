---
title: Converting ISO 8601 formatted date into datetime objects in Python
categories:
    - Tech
tags:
    - python
    - programming
    - Alexa Skills
---

I was playing with Alexa skills few days ago. I stumbled upon the [AMAZON.Date](https://developer.amazon.com/en-US/docs/alexa/custom-skills/slot-type-reference.html#date) slot type which converts the user spoken day and date into ISO formatted string. For e.g. Consider a skill called *Weather Man*, which gives the weather information for a given day. It has an intent with an utterance like `how's weather {date}`. Say, today's date is `01/10/2020` and the user uttered something like `Alexa, ask weather man how's weather tomorrow?`. In the request to the skill endpoint, the value of the date slot will be filled as `2020-01-11`, in **YYYY-MM-DD** format. If the date asked is for a week, then date slot will be filled in the format of **YYYY-Www**, where **ww** is the week number. If the date asked is weekend, then the format followed is **YYYY-Www-WE**. If the user uttered something like `Alexa, ask weather man how's weather this weekend?`, it would translate into **2020-W02-WE** in our example. Here is a snippet of how the skill request json would like. The format varies depending on the utterance.

```json
    "request": {
        "type": "IntentRequest",
        "requestId": "amzn1.echo-api.request.24954898-006a-4d29-b3ea-808ce886ed3e",
        "timestamp": "2020-01-10T04:54:54Z",
        "locale": "en-US",
        "intent": {
            "name": "WeatherIntent",
            "confirmationStatus": "NONE",
            "slots": {
                "date": {
                    "name": "date",
                    "value": "2020-W02-WE",
                    "confirmationStatus": "NONE",
                    "source": "USER"
                }
            }
        }
    }
```

I wanted to parse this date string at the skill endpoint and respond to the user accordingly. Since the endpoint was hosted as python funtion in AWS Lamda, I looked into my go to python reference, the docs page.

If the date format is **YYYY-MM-DD**, Python's `datetime.datetime` has some nifty helpers to convert the date string into a datetime object.

```python
>>> import datetime
>>> datestr = "2020-01-10"
>>> dt = datetime.datetime.fromisoformat(datestr)
>>> dt
datetime.datetime(2020, 1, 10, 0, 0)
```

Unfortunately, `fromisoformat` was introduced only in Python 3.7 and `fromisocalendar` was introduced in 3.8 but I was using only 3.6 with my skill endpoint. So I couldn't use them directly. Also, I wanted to parse other date formats as well. So back to old friend, [datetime.datetime.strptime](https://docs.python.org/3/library/datetime.html?#datetime.datetime.strptime) which is similar to [strptime](http://man7.org/linux/man-pages/man3/strptime.3p.html) in C.

The required format specifiers for the date fields in this case are:

| **Field**                    | **Format specifier** |
| ---------------------------- | -------------------- |
| year in 4 digits             | %Y                   |
| month in 2 digits            | %m                   |
| day of the month in 2 digits | %d                   |
| week number                  | %U, %W               |

> For the week number, `%U` is used if week starts from Sunday and `%W` if the week starts from Monday

Python 3.6 added three new format specifiers conforming to ISO 8601 standards. Amazon.DATE slot also uses the same standards. The new format specifiers are:

| **Format** | **Description**                       |
| ---------- | ------------------------------------- |
| %G         | ISO 8601 year                         |
| %u         | ISO 8601 week day, starting on Monday |
| %V         | ISO 8601 week as decimal number       |

If the date is in YYYY-MM-DD format, the format `%Y-%m-%d` worked good.

```python
>>> datestr = "2020-01-09"
>>> datetime.datetime.strptime(datestr, "%Y-%m-%d")
datetime.datetime(2020, 1, 9, 0, 0)
>>> datestr = "2020-03-09"
>>> datetime.datetime.strptime(datestr, "%Y-%m-%d")
datetime.datetime(2020, 3, 9, 0, 0)
```

When only the week number is available, it is required to specify the weekday as well when using the ISO 8601 based directives.

```python
>>> datestr = "2020-W02"
>>> datetime.datetime.strptime(datestr, "%G-W%V")
Traceback (most recent call last):
  File "<stdin>", line 1, in <module>
  File "/Library/Frameworks/Python.framework/Versions/3.6/lib/python3.6/_strptime.py", line 565, in _strptime_datetime
    tt, fraction = _strptime(data_string, format)
  File "/Library/Frameworks/Python.framework/Versions/3.6/lib/python3.6/_strptime.py", line 483, in _strptime
    raise ValueError("ISO year directive '%G' must be used with "
ValueError: ISO year directive '%G' must be used with the ISO week directive '%V' and a weekday directive ('%A', '%a', '%w', or '%u').
>>> datestr = "2020-W03"
>>> datetime.datetime.strptime(datestr+"-2", "%G-W%V-%u")
datetime.datetime(2020, 1, 14, 0, 0)
>>> datestr = "2020-W01"
>>> datetime.datetime.strptime(datestr+"-2", "%G-W%V-%u")
datetime.datetime(2019, 12, 31, 0, 0)
>>> datestr = "2020-W01-WE"
>>> datetime.datetime.strptime(datestr+"-6", "%G-W%V-WE-%u")
datetime.datetime(2020, 1, 4, 0, 0)
>>> datetime.datetime.strptime(datestr+"-7", "%G-W%V-WE-%u").isocalendar()
(2020, 1, 7)
```

Once the datetime object is created, we can do further manipulations such as calculating deltas, formating date/time into different format etc. Many times, it is important to get the time based on the time zone as well. The ISO 8601 based directives do not offer the support to specify the timezone yet. So I had to create the datetime object and then add the timezone info. Here is an example.

> [pytz](https://pypi.org/project/pytz/) can be installed using `pip install`

```python
>>> import pytz
>>> dt = datetime.datetime.strptime(datestr+"-6", "%G-W%V-WE-%u")
>>> dt
datetime.datetime(2020, 1, 4, 0, 0)
>>> # Set the timezone as America/New_York and make a new datetime object
>>> dt.replace(tzinfo=pytz.timezone("America/New_York"))
datetime.datetime(2020, 1, 4, 0, 0, tzinfo=<DstTzInfo 'America/New_York' LMT-1 day, 19:04:00 STD>)
```
