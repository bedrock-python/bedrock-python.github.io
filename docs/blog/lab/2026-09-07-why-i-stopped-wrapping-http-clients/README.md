# Lab: Native HTTP clients, metrics and nested retries {#lab-why-i-stopped-wrapping-http-clients}

`client_flow.py` contains the article's HTTP snippets. `http_origin.py` runs a local aiohttp server with stock, payment and failure routes; `http_checks.py` contains assertions reused by five labs.

`wrappers_lab.py` checks that HTTPX, aiohttp and Requests keep their native interfaces; a stock read returning 503 twice becomes one successful call and three attempts; clients close after use; unsupported Requests attempt timeouts appear in `inspect(client).report` or fail under `on_unsupported='strict'`; and three outer retries around three client attempts produce nine server requests.

All requests use real localhost HTTP. Requests runs in a thread so it cannot block the local async server. The examples check behavior, not transport performance.

Run from `docs/blog/lab/2026-09-07-why-i-stopped-wrapping-http-clients` in the repository checkout. Dependencies are pinned in `requirements.txt`.

```bash
uv run --no-project --python 3.13 --with-requirements requirements.txt python wrappers_lab.py
```

[Lab source on GitHub](https://github.com/bedrock-python/bedrock-python.github.io/tree/master/docs/blog/lab/2026-09-07-why-i-stopped-wrapping-http-clients).
