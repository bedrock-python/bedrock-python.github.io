# Lab: Reuse and isolation of gRPC channels {#lab-grpc-channels-should-not-be-pooled-by-address-alone}

Orders and audit call one inventory address. The server observes three attempts from orders and one from audit, showing that audit did not inherit orders' retry chain.

Using public `ChannelPool.get_channel()`, the lab checks that a stable interceptor chain reuses the same channel while another chain, rebuilt interceptors and changed channel options get separate channels. After the pool scope exits, acquired channels report `SHUTDOWN` through the public gRPC state API. No private entry table is read.

Keep the neighbouring [gRPC retries lab](../2026-09-07-safe-grpc-retries/README.md): its stub, server and application setup are reused here. No Docker is needed.

Run from `docs/blog/lab/2026-09-07-grpc-channel-identity` in the repository checkout. Dependencies are pinned in `requirements.txt`.

```bash
uv run --no-project --python 3.13 --with-requirements requirements.txt python identity_lab.py
```

[Lab source on GitHub](https://github.com/bedrock-python/bedrock-python.github.io/tree/master/docs/blog/lab/2026-09-07-grpc-channel-identity).
