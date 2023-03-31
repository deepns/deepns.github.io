---
title: Serializing data with protobuf and json
category: Tech
tags:
    - go
    - programming
    - protobuf
    - json
header:
  teaser: /assets/images/teasers/azure-aci.png
---

I have been reading about gRPC and protobuf in the recent times, exploring [protocol buffers](https://protobuf.dev/programming-guides/proto3/) and [grpc concepts](https://grpc.io/docs/what-is-grpc/core-concepts/). The quick start tutorials provided for different languages were pretty good to start off with. After running through the HelloWorld example and another simple service, I was curious to see where protobuf stands tall and where it stands short, when compared to other data interchange mechanisms like json, xml etc. To begin with,

- **Schema Definition**: Protocol Buffers require a schema definition that defines the structure of the message, which is then used to generate code in various languages. On the other hand, JSON does not require a schema definition, and its structure can vary widely depending on the implementation. Makes it super easy to write and test simple cases. No overhead of compiling the schema definition.

- **Language Support**: Protocol Buffers provide first-class support for multiple languages, including Java, C++, Python, and Go, and support for additional languages can be added through extensions. JSON, on the other hand, has ubiquitous support across all languages.

- **Data Types**: Protocol Buffers support a smaller set of data types than JSON, including strings, numbers, booleans, enums, and arrays. JSON supports a wider range of data types, including null, objects, and custom data types.

- **Parsing Overhead**: JSON requires a parser to be used to parse the data, which can have a performance overhead. Protocol Buffers do not require a parser, and the data can be directly deserialized into objects.

- **Readability**: JSON is more human-readable and easier to understand than Protocol Buffers, making it easier to debug and develop applications that consume JSON data.

Defined a simple protobuf definition with some [scalar types](https://protobuf.dev/programming-guides/proto3/#scalar).

```proto
syntax = "proto3";
option go_package = "github.com/deepns/codegym/go/learning/grpc/echo";

message EchoRequestWithCount {
    string message = 1;
    int32 count = 2;  
}
```

Using Go as the language choice, compiled the above message with a protoc compiler. It created a struct type, with some unexported fields and with the message fields exported.

```go
type EchoRequestWithCount struct {
	state         protoimpl.MessageState
	sizeCache     protoimpl.SizeCache
	unknownFields protoimpl.UnknownFields

	Message string `protobuf:"bytes,1,opt,name=message,proto3" json:"message,omitempty"`
	Count   int32  `protobuf:"varint,2,opt,name=count,proto3" json:"count,omitempty"`
}
```

Lets see how the encoded type loos like.

```go
import (
    "fmt"
    pb "github.com/deepns/codegym/go/learning/grpc/echo/echo"
    "github.com/golang/protobuf/proto"
)

func main() {
	echoRequest := pb.EchoRequestWithCount{
		Message: "Woof!",
		Count:   100,
	}
	echoRequestBinary, _ := proto.Marshal(&echoRequest)
	fmt.Println("echoRequestBinary:", echoRequestBinary)
}
```

The output came as:

```console
echoRequestBinary: [10 5 87 111 111 102 33 16 100]
```

I guess `10` corresponds to `byte`, followed by length of the string (which is 5 in this case), then type of int32, determined by `16` followed by the actual value. For larger integers, the encoding scheme seems different.

To explore further, defined another message one with more types.

```proto
syntax = "proto3";

option go_package = "github.com/deepns/codegym/go/learning/grpc/protobuf/books";

// Book attributes defined with scalar fields
message Book {
    string title = 1;
    uint32 year = 2;
    double price = 3;
    bool is_released = 4;
    BookGenre genre = 5;
}

enum BookGenre {
    FICTION = 0;
    THRILLER = 1;
    MEMOIR = 2;
}

message Shelf { 
    repeated Book books_to_read = 1;
    repeated Book books_read = 2;
}
```

Then tried to create some objects for the above types and serialize them into a file.

```go
package main

import (
	"encoding/json"
	"log"

	pb "github.com/deepns/codegym/go/learning/grpc/protobuf/books"
	"google.golang.org/protobuf/proto"
)

func main() {
    shelf := &pb.Shelf{
		BooksToRead: []*pb.Book{
			{
				Title:      "Sapiens: A Brief History of Humankind",
				Year:       2015,
				Price:      12.99,
				IsReleased: true,
				Genre:      pb.BookGenre_MEMOIR,
			},
			{
				Title:      "The Water Dancer",
				Year:       2019,
				Price:      11.99,
				IsReleased: true,
				Genre:      pb.BookGenre_FICTION,
			},
		},
		BooksRead: []*pb.Book{
			{
				Title:      "The Underground Railroad",
				Year:       2016,
				Price:      9.99,
				IsReleased: true,
				Genre:      pb.BookGenre_FICTION,
			},
			{
				Title:      "The Power of Now: A Guide to Spiritual Enlightenment",
				Year:       1997,
				Price:      7.99,
				IsReleased: true,
				Genre:      pb.BookGenre_MEMOIR,
			},
		},
	}

	// Marshal the "shelf" instance into binary format
	shelfData, err := proto.Marshal(shelf)
	if err != nil {
		log.Fatalln("Error marshaling shelf data", err)
	}

    // Marshal the "shelf" instance into json format
	// Since json encoding is defined in the struct itself, protobuf struct
	// can be readily marshaled to json.
	shelfDataJson, err := json.Marshal(shelf)
	if err != nil {
		log.Fatalln("Error marshaling shelf data to json", err)
	}

    log.Println("Bytes written in pb format:", len(shelfData))
	log.Println("Bytes written in json format:", len(shelfDataJson))
```

```console
2023/03/30 18:30:38 Bytes written in pb format: 205
2023/03/30 18:30:38 Bytes written in json format: 413
```

Protobuf bytes took about 205 bytes whereas the json based data bytes took about 413 bytes in this case, ~50% reduction. This is of course highly simplified example, as this could vary depending on the length of the keys and values. These savings on data size and transfer do provide significant values in high performance applications.
