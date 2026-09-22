# Lab: Circuit breakers per origin {#lab-circuit-breakers-should-be-per-origin}

One HTTPX client calls two local HTTP origins: inventory and payments. Payments always returns 503. Three logical calls make nine attempts; the fourth call is refused without reaching the server. Inventory still returns 200.

A separate case checks that 400 does not trip the breaker and that an allowed recovery probe closes it after success. `AdapterDeps(clock=ManualClock())` advances the recovery clock deterministically; requests still use actual localhost HTTP. This checks the `open → half_open → closed` transition, not the real duration of infrastructure recovery.

The source and fixtures are in the neighbouring [HTTP clients lab](../2026-09-07-why-i-stopped-wrapping-http-clients/README.md); keep that directory. Assertions inspect public metrics and server counts, not private breaker state.

Run from `docs/blog/lab/2026-09-07-circuit-breakers-per-origin` in the repository checkout. Dependencies are pinned in `requirements.txt`.

```bash
uv run --no-project --python 3.13 --with-requirements requirements.txt python breakers_lab.py
```

[Lab source on GitHub](https://github.com/bedrock-python/bedrock-python.github.io/tree/master/docs/blog/lab/2026-09-07-circuit-breakers-per-origin).
