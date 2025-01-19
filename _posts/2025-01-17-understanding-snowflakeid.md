---
title: Understanding Snowflake ID and its uses
category: Tech
tags:
    - learning
    - tools
    - python
header:
  teaser: /assets/images/for-posts/understanding-snowflakeid.jpeg
---

In distributed systems, ensuring unique and scalable identifiers is critical. While working on a recent problem, I needed to generate unique 64bit numbers across services. Snowflake ID approach fitted that requirement efficiently and reliably. Lets explore the Snowflake ID algorithm, its applications, and provide a Python implementation example. We'll also cover deploying the application using Docker.

---

## What is Snowflake ID?

Snowflake ID is a 64-bit unique identifier originally developed by Twitter. It is highly efficient and scalable, designed to work in distributed systems. The ID consists of the following components:

1. **Timestamp (41 bits)**: Represents the time in milliseconds since a custom epoch.
2. **Machine ID (10 bits)**: Uniquely identifies the machine or node generating the ID.
3. **Sequence Number (12 bits)**: Ensures uniqueness for IDs generated within the same millisecond.

---

## Why Use Snowflake ID?

1. **Scalability**: Works seamlessly in distributed environments.
2. **Uniqueness**: Combines timestamp, machine ID, and sequence number to ensure no duplicates.
3. **Efficiency**: Generates IDs in constant time, even under high loads.
4. **Compactness**: Represents large IDs in a compact 64-bit format.

---

## Snowflake ID Python Implementation

Below is a Python implementation of a Snowflake ID generator and its integration with MongoDB:

```python
import os
import time
from pymongo import MongoClient

class SnowflakeIDGenerator:
    """
    A class to generate unique Snowflake IDs.

    Attributes:
        epoch (int): The custom epoch timestamp in milliseconds. Default is 1640995200000.
        machine_id (int): The machine ID, derived from the environment variable "MACHINE_ID" and masked with 0x3FF.
        sequence (int): The sequence number for IDs generated within the same millisecond.
        last_timestamp (int): The timestamp of the last generated ID.

    Methods:
        _current_timestamp(): Returns the current timestamp in milliseconds.
        generate_id(): Generates a unique Snowflake ID based on the current timestamp, machine ID, and sequence number.
    """
    def __init__(self, epoch: int = 1640995200000):
        self.machine_id = int(os.getenv("MACHINE_ID", "0")) & 0x3FF
        self.epoch = epoch
        self.sequence = 0
        self.last_timestamp = -1

    def _current_timestamp(self):
        return int(time.time() * 1000)

    def generate_id(self):
        timestamp = self._current_timestamp()

        if timestamp == self.last_timestamp:
            self.sequence = (self.sequence + 1) & 0xFFF
            if self.sequence == 0:
                while timestamp <= self.last_timestamp:
                    timestamp = self._current_timestamp()
        else:
            self.sequence = 0

        self.last_timestamp = timestamp

        return (
            ((timestamp - self.epoch) << 22) |
            (self.machine_id << 12) |
            self.sequence
        )

# MongoDB connection
client = MongoClient(os.getenv("MONGO_URI", "mongodb://mongo:27017/"))
db = client["test_database"]
collection = db["test_collection"]

# Initialize Snowflake Generator
generator = SnowflakeIDGenerator()

# Generate and insert IDs
batch_size = int(os.getenv("BATCH_SIZE", "10000"))
for i in range(batch_size):
    unique_id = generator.generate_id()
    document = {
        "_id": unique_id,
        "pod": os.getenv("HOSTNAME", "unknown"),
        "timestamp": time.time()
    }
    collection.insert_one(document)

print(f"Generated and inserted {batch_size} IDs.")
```

This application generates unique Snowflake IDs and writes them to a MongoDB database. Each ID is stored in a document along with metadata, such as the hostname and timestamp, enabling scalable storage and retrieval in distributed systems.

---

## Deploying the Application Using Docker

To simplify deployment, we use Docker and Docker Compose. Below is the `Dockerfile` and `docker-compose.yml` configuration:

### Dockerfile

```dockerfile
# Use an official Python runtime as the base image
FROM python:3.10-slim

# Set the working directory in the container
WORKDIR /app

# Copy application code
COPY app.py /app

# Install dependencies
RUN pip install pymongo

# Define environment variables
ENV MONGO_URI=mongodb://mongo:27017/
ENV MACHINE_ID=0

# Run the application
CMD ["python", "app.py"]
```

### Docker Compose

```yaml
version: '3.9'

services:
  mongo:
    image: mongo:latest
    container_name: mongo
    ports:
      - "27017:27017"
    volumes:
      - mongo_data:/data/db

  app1:
    image: snowflakeidgen
    build:
      context: .
      dockerfile: Dockerfile
    environment:
      - MONGO_URI=mongodb://mongo:27017/
      - MACHINE_ID=1
    depends_on:
      - mongo

  app2:
    image: snowflakeidgen
    environment:
      - MONGO_URI=mongodb://mongo:27017/
      - MACHINE_ID=2
    depends_on:
      - mongo

  app3:
    image: snowflakeidgen
    environment:
      - MONGO_URI=mongodb://mongo:27017/
      - MACHINE_ID=3
    depends_on:
      - mongo

volumes:
  mongo_data:
```

---

## Running the Application

1. **Build the Docker Image**:

   ```bash
   docker-compose build
   ```

2. **Start the Services**:

   ```bash
   docker-compose up
   ```

3. **Verify the Output**:

   - The MongoDB container will be accessible at `localhost:27017`.
   - The application will generate and insert unique Snowflake IDs into MongoDB.

---

## Conclusion

Snowflake ID is an elegant solution for generating unique identifiers in distributed systems. Its combination of timestamp, machine ID, and sequence ensures scalability, efficiency, and uniqueness. This application demonstrates how to generate and store these IDs in MongoDB, and by using Docker, deploying and running the system becomes seamless and consistent across environments.
