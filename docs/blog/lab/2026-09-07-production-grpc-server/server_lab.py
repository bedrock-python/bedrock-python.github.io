"""The anatomy of a production gRPC server, one measurement per part.

An in-process `grpc.aio` server is built several ways and asked what a client sees: what a
handler's exception leaks, what an interceptor in the wrong position reports, what a payload
above the size limit gets, what a shutdown does to a request that is still running, what the
health service says while a dependency is down, and what TLS refuses to start with.
"""

from __future__ import annotations

import asyncio
import os
import stat
import subprocess
import tempfile
import time
from collections.abc import AsyncIterator
from importlib.metadata import version
from pathlib import Path

import grpc
import grpc.aio

from grpc_server_kit import GrpcApp, GrpcServerConfig, build_grpc_options, load_server_credentials
from grpc_server_kit.aio.interceptors import (
    AsyncExceptionHandlerInterceptor,
    AsyncServerInterceptor,
    RpcCall,
)

SERVICE = "lab.Orders"
PLACE = f"/{SERVICE}/Place"
SLOW = f"/{SERVICE}/Slow"
BULK = f"/{SERVICE}/Bulk"


def log(msg: str) -> None:
    print(msg, flush=True)


class Orders:
    """The handler. `Place` fails the way handlers actually fail: an ordinary Python exception."""

    def __init__(self) -> None:
        self.slow_started = 0
        self.slow_finished = 0

    async def place(self, request: bytes, context: grpc.aio.ServicerContext) -> bytes:
        mode = request.decode()
        if mode == "boom":
            secret = "postgresql://orders:hunter2@db.internal:5432/orders"  # noqa: S105 - the point of the test
            raise RuntimeError(f"could not reach the ledger at {secret}")
        if mode == "denied":
            await context.abort(grpc.StatusCode.PERMISSION_DENIED, "not your order")
        return b"ok"

    async def slow(self, request: bytes, context: grpc.aio.ServicerContext) -> bytes:
        self.slow_started += 1
        await asyncio.sleep(float(request))
        self.slow_finished += 1
        return b"done"

    async def bulk(self, request: bytes, context: grpc.aio.ServicerContext) -> bytes:
        return len(request).to_bytes(4, "big")


def handlers(orders: Orders):
    return grpc.method_handlers_generic_handler(
        SERVICE,
        {
            "Place": grpc.unary_unary_rpc_method_handler(orders.place),
            "Slow": grpc.unary_unary_rpc_method_handler(orders.slow),
            "Bulk": grpc.unary_unary_rpc_method_handler(orders.bulk),
        },
    )


class CountingReporter(AsyncServerInterceptor):
    """Stands in for the Sentry interceptor: it counts what reaches it, and how."""

    def __init__(self) -> None:
        super().__init__()
        self.captured: list[str] = []

    async def around_call(self, call: RpcCall) -> AsyncIterator[None]:
        try:
            yield
        except grpc.RpcError as error:  # the filter everybody writes first
            self.captured.append(f"RpcError {type(error).__name__}")
            raise
        except Exception as error:  # noqa: BLE001 - reporting is the job
            self.captured.append(type(error).__name__)
            raise


async def call(target: str, method: str, payload: bytes, *, options=None, timeout: float = 10.0):
    async with grpc.aio.insecure_channel(target, options=options or []) as channel:
        try:
            response = await channel.unary_unary(method)(payload, timeout=timeout)
            return "OK", response
        except grpc.aio.AioRpcError as error:
            return error.code().name, error.details()


# --- 1. what an unhandled exception tells the caller -----------------------------------------


async def part_errors() -> None:
    log("--- 1. a handler that raises, with and without the exception interceptor")
    orders = Orders()
    for label, interceptors in (
        ("no interceptor", []),
        ("AsyncExceptionHandlerInterceptor", [AsyncExceptionHandlerInterceptor()]),
    ):
        app = GrpcApp(GrpcServerConfig(host="127.0.0.1", port=0), interceptors=list(interceptors))
        app.register(lambda server, o=orders: server.add_generic_rpc_handlers((handlers(o),)))
        async with app:
            target = f"127.0.0.1:{app.bound_port}"
            code, details = await call(target, PLACE, b"boom")
            log(f"    {label:<34} RuntimeError -> {code}: {details!r}")
            code, details = await call(target, PLACE, b"denied")
            log(f"    {label:<34} context.abort -> {code}: {details!r}")


# --- 2. where the reporting interceptor goes -------------------------------------------------


async def part_order() -> None:
    log("--- 2. the reporting interceptor before and after the exception handler")
    orders = Orders()
    for label, build in (
        ("reporter first (outermost)", lambda r: [r, AsyncExceptionHandlerInterceptor()]),
        ("reporter after the handler", lambda r: [AsyncExceptionHandlerInterceptor(), r]),
    ):
        reporter = CountingReporter()
        app = GrpcApp(GrpcServerConfig(host="127.0.0.1", port=0), interceptors=build(reporter))
        app.register(lambda server, o=orders: server.add_generic_rpc_handlers((handlers(o),)))
        async with app:
            target = f"127.0.0.1:{app.bound_port}"
            await call(target, PLACE, b"boom")
            await call(target, PLACE, b"denied")
        log(f"    {label:<28} reported: {reporter.captured or 'nothing'}")


# --- 3. message size --------------------------------------------------------------------------


async def part_size() -> None:
    log("--- 3. a payload over the message size limit")
    payload = b"x" * (5 * 1024 * 1024)
    orders = Orders()
    for label, settings in (
        ("kit defaults", GrpcServerConfig(host="127.0.0.1", port=0)),
        (
            "max_receive_message_length=8 MB",
            GrpcServerConfig(host="127.0.0.1", port=0, max_receive_message_length=8 * 1024 * 1024),
        ),
    ):
        app = GrpcApp(settings)
        app.register(lambda server, o=orders: server.add_generic_rpc_handlers((handlers(o),)))
        async with app:
            target = f"127.0.0.1:{app.bound_port}"
            options = [("grpc.max_send_message_length", 16 * 1024 * 1024)]
            code, details = await call(target, BULK, payload, options=options)
            log(f"    {label:<32} 5 MiB request -> {code}: {str(details)[:80]!r}")
    opts = dict(build_grpc_options(GrpcServerConfig(host="127.0.0.1", port=0)))
    for key in sorted(opts):
        log(f"    default option {key:<42} {opts[key]}")


# --- 4. shutdown ------------------------------------------------------------------------------


async def part_shutdown() -> None:
    log("--- 4. a request still running when the server is asked to stop")
    for label, grace in (("grace_period=5.0", 5.0), ("grace_period=0.0", 0.0)):
        orders = Orders()
        app = GrpcApp(GrpcServerConfig(host="127.0.0.1", port=0, grace_period=grace))
        app.register(lambda server, o=orders: server.add_generic_rpc_handlers((handlers(o),)))
        app.build()
        server = app.server
        await server.start()
        target = f"127.0.0.1:{app.bound_port}"
        async with grpc.aio.insecure_channel(target) as channel:
            async def issue():
                return await channel.unary_unary(SLOW)(b"2.0", timeout=10)

            pending = asyncio.create_task(issue())
            await asyncio.sleep(0.4)
            started = time.perf_counter()
            await server.stop(grace)
            stopped = time.perf_counter() - started
            try:
                await pending
                outcome = "the response arrived"
            except grpc.aio.AioRpcError as error:
                outcome = f"{error.code().name}: {error.details()}"
        log(f"    {label:<18} stop() took {stopped:.2f} s, handler finished {orders.slow_finished}/1, "
            f"client: {outcome}")


# --- 5. health --------------------------------------------------------------------------------


class DatabaseChecker:
    """A health checker that flips when the dependency it stands for goes away."""

    def __init__(self) -> None:
        self.up = True

    @property
    def name(self) -> str:
        return "database"

    async def check(self) -> bool:
        return self.up


async def health_status(target: str, service: str = "") -> str:
    from grpc_health.v1 import health_pb2, health_pb2_grpc

    async with grpc.aio.insecure_channel(target) as channel:
        stub = health_pb2_grpc.HealthStub(channel)
        try:
            response = await stub.Check(health_pb2.HealthCheckRequest(service=service), timeout=5)
            return health_pb2.HealthCheckResponse.ServingStatus.Name(response.status)
        except grpc.aio.AioRpcError as error:
            return f"{error.code().name}: {error.details()}"


async def part_health() -> None:
    log("--- 5. the health service, with a dependency that goes down")
    orders = Orders()
    app = GrpcApp(GrpcServerConfig(host="127.0.0.1", port=0))
    app.register(lambda server: server.add_generic_rpc_handlers((handlers(orders),)))
    async with app:
        log(f"    no enable_health(): Check -> {await health_status(f'127.0.0.1:{app.bound_port}')}")

    checker = DatabaseChecker()
    app = GrpcApp(GrpcServerConfig(host="127.0.0.1", port=0))
    app.register(lambda server: server.add_generic_rpc_handlers((handlers(orders),)))
    app.enable_health(checkers=[checker], cache_ttl=0)
    async with app:
        target = f"127.0.0.1:{app.bound_port}"
        log(f"    database up:   Check -> {await health_status(target)}")
        checker.up = False
        log(f"    database down: Check -> {await health_status(target)}")
        code, details = await call(target, PLACE, b"ok")
        log(f"    ... and the service itself still answers: {code}")
        checker.up = True
        log(f"    database back: Check -> {await health_status(target)}")


# --- 6. TLS -----------------------------------------------------------------------------------


def make_certs(directory: Path) -> dict[str, Path]:
    """A CA, a server certificate and a client certificate, with openssl."""
    files = {name: directory / name for name in ("ca.key", "ca.crt", "server.key", "server.csr", "server.crt", "client.key", "client.csr", "client.crt")}
    run = lambda *args: subprocess.run(args, check=True, capture_output=True)  # noqa: E731
    run("openssl", "req", "-x509", "-newkey", "rsa:2048", "-nodes", "-days", "1",
        "-keyout", str(files["ca.key"]), "-out", str(files["ca.crt"]), "-subj", "/CN=lab-ca")
    for who in ("server", "client"):
        cn = "localhost" if who == "server" else "orders-gateway"
        run("openssl", "req", "-newkey", "rsa:2048", "-nodes",
            "-keyout", str(files[f"{who}.key"]), "-out", str(files[f"{who}.csr"]), "-subj", f"/CN={cn}")
        run("openssl", "x509", "-req", "-in", str(files[f"{who}.csr"]), "-days", "1",
            "-CA", str(files["ca.crt"]), "-CAkey", str(files["ca.key"]), "-CAcreateserial",
            "-out", str(files[f"{who}.crt"]))
    for who in ("server", "client"):
        os.chmod(files[f"{who}.key"], 0o600)
    return files


async def part_tls() -> None:
    log("--- 6. TLS and mTLS")
    with tempfile.TemporaryDirectory() as tmp:
        files = make_certs(Path(tmp))
        base = dict(
            host="127.0.0.1",
            port=0,
            ssl_enabled=True,
            ssl_cert_file=str(files["server.crt"]),
            ssl_key_file=str(files["server.key"]),
        )
        os.chmod(files["server.key"], 0o640)
        settings = GrpcServerConfig(**base)
        try:
            load_server_credentials(settings)
            log("    a key readable by the group: accepted")
        except Exception as error:  # noqa: BLE001
            log(f"    a key readable by the group: {type(error).__name__}: {error}")
        os.chmod(files["server.key"], 0o600)

        orders = Orders()
        for label, extra in (
            ("TLS, no client certificate required", {}),
            ("mTLS, client certificate required", {"ssl_ca_file": str(files["ca.crt"]), "ssl_client_auth": True}),
        ):
            app = GrpcApp(GrpcServerConfig(**base, **extra))
            app.register(lambda server, o=orders: server.add_generic_rpc_handlers((handlers(o),)))
            async with app:
                target = f"localhost:{app.bound_port}"
                ca = files["ca.crt"].read_bytes()
                plain = await call(target, PLACE, b"ok")
                creds = grpc.ssl_channel_credentials(root_certificates=ca)
                async with grpc.aio.secure_channel(target, creds) as channel:
                    try:
                        await channel.unary_unary(PLACE)(b"ok", timeout=5)
                        anon = "OK"
                    except grpc.aio.AioRpcError as error:
                        anon = error.code().name
                mtls_creds = grpc.ssl_channel_credentials(
                    root_certificates=ca,
                    private_key=files["client.key"].read_bytes(),
                    certificate_chain=files["client.crt"].read_bytes(),
                )
                async with grpc.aio.secure_channel(target, mtls_creds) as channel:
                    try:
                        await channel.unary_unary(PLACE)(b"ok", timeout=5)
                        mutual = "OK"
                    except grpc.aio.AioRpcError as error:
                        mutual = error.code().name
                log(f"    {label:<36} plaintext client: {plain[0]}, TLS client: {anon}, mTLS client: {mutual}")


async def main() -> None:
    log(f"grpc-server-kit {version('grpc-server-kit')}, grpcio {version('grpcio')}")
    await part_errors()
    await part_order()
    await part_size()
    await part_shutdown()
    await part_health()
    await part_tls()


if __name__ == "__main__":
    asyncio.run(main())
