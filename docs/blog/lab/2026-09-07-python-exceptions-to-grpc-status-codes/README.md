# Lab: Python exceptions to gRPC status codes

Eleven exceptions — five standard ones the kit maps by default, three that fall through, and three
domain errors — sent through one gRPC server in four configurations: no exception handling, the
default map, the default map plus this service's domain errors, and the same with a detail factory
that returns a useful message for domain errors and a generic one for everything else. The lab
prints the status code and the details string the client received, and flags any line that leaked
a password.

```bash
uv venv --python 3.13 .venv
uv pip install --python .venv/bin/python "grpc-server-kit==0.1.1"
.venv/bin/python mapping_lab.py
```
