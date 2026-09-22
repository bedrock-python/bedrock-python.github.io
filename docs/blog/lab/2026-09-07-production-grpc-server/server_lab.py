"""Real RPC checks: limits, health, cancellation, graceful shutdown, TLS and mTLS."""
import asyncio
from dataclasses import replace
import logging
import os
from pathlib import Path
import tempfile

import grpc
from grpc_server_kit import load_server_credentials

from grpc_flow import (
    METHOD, build_app, enable_readiness, serve_invoices, server_config, tls_config,
)
from lab_support import (
    InvoiceStore, Metrics, Reporter, call, expect_error, health, result, wait_until,
)
from tls_support import certificates


async def limits():
    store = InvoiceStore(blocked=True)
    app = build_app(store, Metrics(), Reporter(), config=replace(server_config(), max_concurrent_rpcs=1))
    async with app:
        async with grpc.aio.insecure_channel(f"127.0.0.1:{app.bound_port}") as channel:
            pending = channel.unary_unary(METHOD)(b"ready", timeout=3)
            try:
                await store.started.wait()
                # The same setting also caps HTTP/2 streams per connection:
                # a call on this connection queues before it reaches the RPC handler.
                await expect_error(call(channel, timeout=0.15), grpc.StatusCode.DEADLINE_EXCEEDED)
                async with grpc.aio.insecure_channel(
                    f"127.0.0.1:{app.bound_port}",
                    options=[("grpc.use_local_subchannel_pool", 1)],
                ) as other:
                    await expect_error(call(other), grpc.StatusCode.RESOURCE_EXHAUSTED)
                assert store.reads == 1
            finally:
                store.release.set()
                await pending
            await expect_error(call(channel, b"x" * (65 * 1024)), grpc.StatusCode.RESOURCE_EXHAUSTED)
            assert store.reads == 1
            assert result(await call(channel))["invoice_id"] == "inv-42"
    print("PASS limits: same-connection call queues; another connection hits RESOURCE_EXHAUSTED; oversize rejected")


async def readiness():
    store, metrics = InvoiceStore(), Metrics()
    app = build_app(store, metrics, Reporter())
    enable_readiness(app, store)
    async with app:
        async with grpc.aio.insecure_channel(f"127.0.0.1:{app.bound_port}") as channel:
            assert await health(channel) == "SERVING"
            store.up = False
            assert await health(channel) == "NOT_SERVING"
            assert result(await call(channel))["invoice_id"] == "inv-42"
            store.up = True
            assert await health(channel) == "SERVING"
            store.ping_release.clear()
            assert await health(channel) == "NOT_SERVING"
            assert len(metrics.rows) == 1  # Health RPCs are excluded by default.
    print("PASS health: SERVING -> NOT_SERVING -> SERVING; timeout is bounded; direct RPC still works")


async def cancellation():
    for mode in ("cancel", "deadline"):
        store, metrics, reporter = InvoiceStore(blocked=True), Metrics(), Reporter()
        app = build_app(store, metrics, reporter)
        async with app:
            async with grpc.aio.insecure_channel(f"127.0.0.1:{app.bound_port}") as channel:
                pending = channel.unary_unary(METHOD)(b"ready", timeout=0.2 if mode == "deadline" else 3)
                await store.started.wait()
                if mode == "cancel":
                    pending.cancel()
                    try:
                        await pending
                    except asyncio.CancelledError:
                        pass
                    else:
                        raise AssertionError("Client cancellation must propagate")
                else:
                    await expect_error(pending, grpc.StatusCode.DEADLINE_EXCEEDED)
                await store.cleaned.wait()
                await wait_until(lambda: len(metrics.rows) == 1)
                assert store.active == 0
                assert metrics.rows[0]["grpc_code"] == "CANCELLED"
                assert reporter.errors == []
        print(f"PASS {mode}: resource released, server metric=CANCELLED, no error report")


async def shutdown():
    for finish in (True, False):
        store, metrics = InvoiceStore(blocked=True), Metrics()
        config = replace(server_config(), grace_period=0.3)
        app = build_app(store, metrics, Reporter(), config=config)
        app.build()
        stop = asyncio.Event()
        task = asyncio.create_task(serve_invoices(app, store, stop))
        try:
            async with grpc.aio.insecure_channel(f"127.0.0.1:{app.bound_port}") as channel:
                await asyncio.wait_for(channel.channel_ready(), 3)
                pending = channel.unary_unary(METHOD)(b"ready", timeout=3)
                await store.started.wait()
                stop.set()
                await asyncio.sleep(0.04)
                assert not task.done() and not store.closed
                if finish:
                    store.release.set()
                    assert result(await pending)["invoice_id"] == "inv-42"
                else:
                    await expect_error(pending, grpc.StatusCode.UNAVAILABLE)
                await asyncio.wait_for(task, 3)
                assert store.active == 0 and store.closed
        finally:
            stop.set()
            store.release.set()
            await asyncio.wait_for(task, 3)
        print(f"PASS shutdown: finish_in_grace={finish}, store closes after handler cleanup")


async def tls():
    with tempfile.TemporaryDirectory(prefix="invoice-grpc-") as temporary:
        files = certificates(Path(temporary))
        for mutual in (False, True):
            config = tls_config(files["server_cert"], files["server_key"], files["ca"] if mutual else None)
            app = build_app(InvoiceStore(), Metrics(), Reporter(), config=config)
            async with app:
                target = f"127.0.0.1:{app.bound_port}"
                ca = files["ca"].read_bytes()
                async with grpc.aio.insecure_channel(target) as channel:
                    await expect_error(call(channel, timeout=1), grpc.StatusCode.UNAVAILABLE)
                credentials = grpc.ssl_channel_credentials(root_certificates=ca)
                async with grpc.aio.secure_channel(target, credentials) as channel:
                    if mutual:
                        await expect_error(call(channel, timeout=1), grpc.StatusCode.UNAVAILABLE)
                    else:
                        assert result(await call(channel))["invoice_id"] == "inv-42"
                credentials = grpc.ssl_channel_credentials(
                    root_certificates=ca, private_key=files["client_key"].read_bytes(),
                    certificate_chain=files["client_cert"].read_bytes(),
                )
                async with grpc.aio.secure_channel(target, credentials) as channel:
                    assert result(await call(channel))["invoice_id"] == "inv-42"
            print(f"PASS TLS: client_certificate_required={mutual}, plaintext refused, valid certificate accepted")

        invalid = Path(temporary) / "invalid.key"
        invalid.write_text("not a PEM key", encoding="utf-8")
        invalid.chmod(0o600)
        try:
            load_server_credentials(tls_config(files["server_cert"], invalid))
        except ValueError:
            pass
        else:
            raise AssertionError("Invalid PEM must fail before serving")
        if os.name != "nt":
            files["server_key"].chmod(0o640)
            try:
                load_server_credentials(tls_config(files["server_cert"], files["server_key"]))
            except PermissionError:
                pass
            else:
                raise AssertionError("Group-readable private key must be refused on Unix")
            finally:
                files["server_key"].chmod(0o600)
            print("PASS Unix private-key permissions")
        else:
            print("SKIP Unix permission bits on Windows; TLS handshakes and PEM validation were checked")


async def main():
    async with asyncio.timeout(40):
        await limits()
        await readiness()
        await cancellation()
        await shutdown()
        await tls()


if __name__ == "__main__":
    logging.basicConfig(level=logging.CRITICAL)
    asyncio.run(main())
