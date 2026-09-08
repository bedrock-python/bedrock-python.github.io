# Lab: who creates the Kafka topic

One Kafka container and six questions: what a producer writing to a topic that does not exist
leaves behind, what a consumer subscribing to one leaves behind, what the application's own
creation produces, what happens when the next deploy asks for a different shape, what three
replicas starting at once do, and what a shape the cluster cannot honour does to startup.

```bash
uv venv --python 3.13 .venv
uv pip install --python .venv/bin/python "aiokafka-foundation-kit[models]==0.1.3" "testcontainers[kafka]"
.venv/bin/python topics_lab.py
```
