---
title: Python requests vs golang http,json
last_modified_at: 2022-02-04T23:20:02-05:00
category:
    - Tech
tags:
    - programming
    - python
    - golang
    - learning
header:
  teaser: /assets/images/teasers/golang-vs-python.png
---

I have been exploring golang recently, refreshing my memory on some of the basics of the language and learning new topics on the go (pun intended :)). I looked into the [http](https://pkg.go.dev/net/http) and the [json](https://pkg.go.dev/encoding/json) packages
golang, trying to work with restful web services and json data. It was fun and interesting to see how these steps in golang compare to python requests.

Taking a GitHub API link for example. A mirror copy of the golang src is hosted in [github](https://github.com/golang/go). The equivalent API link is `https://api.github.com/repos/golang/go`.

## Using golang builtins

The steps to get the data and decode them in json format go like this.

- Make the get call using `http.Get`
- Completion of the Get call doesn't mean all data is received. Response body is streamed on demand.

```go
const goRepoInGithub = "https://api.github.com/repos/golang/go"
response, err := http.Get(goRepoInGithub)
if err != nil {
    log.Fatal(err)
}
defer response.Body.Close()
```

-~~Due to static typing in go, decoding json data requires us to provide a type matching the data being decoded.~~ Update: My bad 😔 I spoke too soon. I was wrong. Go indeed allows to decode json data into a map.

- We can decode one or more specific fields from the JSON data. Defining a struct with fields matching the keys in the data returned by `https://api.github.com/repos/golang/go`

```go
type Repo struct {
    Name, Language, Description string
    Size, Forks                 int
    Created_at, Url             string
}
```

- We then have to build a json decoder that decodes a stream of json data. Json decoder reads the data from a Reader type. Since `response.Body` supports the `io.Reader` interface, we can `response.Body` directly without having to read all data and build a string reader.

```go
decoder := json.NewDecoder(response.Body)
```

- Decode the data from the reader for given the type.

```go
var goRepo Repo
err = decoder.Decode(&goRepo)
if err != nil {
    log.Fatal(err)
}
fmt.Printf("goRepo: %#v\n", goRepo)
```

- This will print the following data

```console
goRepo: main.Repo{Name:"go", Language:"Go", Description:"The Go programming language", Size:288260, Forks:14163, Created_at:"2014-08-19T04:33:40Z", Url:"https://api.github.com/repos/golang/go"}
```

- Depending on the application needs, we can work with the struct type itself or encode the struct into json.

```go
// MarshalIndent returns json encoding (in a byte slice) of 
// the given type, with the given indentation applied.
goRepoJson, err := json.MarshalIndent(goRepo, "", "  ")
if err != nil {
    log.Fatal(err)
}
os.Stdout.Write(goRepoJson)

// This will write the following data on the standard out.
// {
//   "Name": "go",
//   "Language": "Go",
//   "Description": "The Go programming language",
//   "Size": 288260,
//   "Forks": 14163,
//   "Created_at": "2014-08-19T04:33:40Z",
//   "Url": "https://api.github.com/repos/golang/go"
// }
```

## Using Python requests

- Make a GET request using `requests.get`. This completes the call and fetches the data into the response object

```python
>>> import requests
>>> go_repo_github = "https://api.github.com/repos/golang/go"
>>> resp = requests.get(go_repo_github)
```

- If the data is encoded in json format, we can get the data as a dict by simply calling `json()` on the response object.

```python
>>> # json.data() can succeed even when the request hit 
>>> # some error and error data is in json format.
>>> # Boolean check on the response object checks the status code,
>>> # returns true when the status_code indicates OK.
>>> if resp:
...     json_data = resp.json()
...
```

- We can then use the dict as is or filter specific keys as needed.

```python
>>> # fetching specific fields from the 
>>> wanted_fields = ["name", "language", "description", "size", "forks"]
>>> import pprint
>>> pprint.pprint({field:json_data[field] for field in
...     ["name", "language", "description", "size", "forks"]},
...     indent=4)
{   'description': 'The Go programming language',
    'forks': 14162,
    'language': 'Go',
    'name': 'go',
    'size': 288260}
```

requests library makes it super simple and concise to work with web links and json data. All the decoding is done under the hood. The steps needed to get the same functionality in golang are only slightly longer. In a way, that is better too. Explicit defintion of the structure to decode the json stream makes the intention much clearer. I'd continue to use the python requests for my scripting and automation needs, mainly for its ease of use. Nonetheless, this turned out to be an interesting comparison.
