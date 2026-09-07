# Lab: the production checklist for aiokafka

One Kafka container and a script per question: what the producer refuses to be built with, what
the value and key serializers do, what a replacement consumer re-reads, what auto-commit commits,
what happens when a batch outlives `max_poll_interval_ms`, what topic creation does, and what a
health probe costs against a paused broker.

- `checklist_lab.py` — the checklist, section by section.
- `topic_probe.py` — whether `ensure_topics_async` can create a topic at all.

```bash
uv venv --python 3.13 .venv
uv pip install --python .venv/bin/python "aiokafka-foundation-kit[models]==0.1.3" "testcontainers[kafka]"
.venv/bin/python checklist_lab.py
.venv/bin/python topic_probe.py
```
