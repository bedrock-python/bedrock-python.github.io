"""Observe error mapping, reporting order, and metrics through real gRPC calls."""
import asyncio
import logging
from pathlib import Path
import sys

import grpc
from grpc_server_kit import GrpcApp
from grpc_server_kit.aio.interceptors import AsyncExceptionHandlerInterceptor, AsyncSentryInterceptor

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "2026-09-07-production-grpc-server"))
from grpc_flow import (
    SERVICE, build_app, exception_handler, register_invoice_service, server_config,
)
from lab_support import (
    PRIVATE_MARKER, InvoiceStore, Metrics, Reporter, call, expect_error, result, wait_until,
)


async def defaults():
    for name, interceptors, code, details in (
        ("bare server", [], grpc.StatusCode.UNKNOWN, None),
        ("kit defaults", [AsyncExceptionHandlerInterceptor()], grpc.StatusCode.INVALID_ARGUMENT, "Invalid request data"),
        ("explicit map", [exception_handler()], grpc.StatusCode.INTERNAL, "internal_error"),
    ):
        app = GrpcApp(server_config(), interceptors=interceptors)
        app.register(lambda server: register_invoice_service(server, InvoiceStore()))
        async with app:
            async with grpc.aio.insecure_channel(f"127.0.0.1:{app.bound_port}") as channel:
                error = await expect_error(call(channel, "value-bug"), code, details)
                assert (PRIVATE_MARKER in error.details()) == (name == "bare server")
        print(f"PASS {name}: internal ValueError -> {code.name}, details_checked=True")


async def explicit_contract():
    metrics, reporter, store = Metrics(), Reporter(), InvoiceStore()
    app = build_app(store, metrics, reporter)

    async def deliberate_abort(request, context):
        await context.abort(grpc.StatusCode.UNAUTHENTICATED, "authentication_required")

    app.register(lambda server: server.add_generic_rpc_handlers((grpc.method_handlers_generic_handler(
        SERVICE, {"Abort": grpc.unary_unary_rpc_method_handler(deliberate_abort)},
    ),)))
    cases = {
        "missing": ("NOT_FOUND", "order_not_found"),
        "unpaid": ("FAILED_PRECONDITION", "invoice_not_ready"),
        "foreign": ("PERMISSION_DENIED", "invoice_access_denied"),
        "offline": ("UNAVAILABLE", "invoice_store_unavailable"),
        "private": ("INTERNAL", "internal_error"),
        "bug": ("INTERNAL", "internal_error"),
        "value-bug": ("INTERNAL", "internal_error"),
    }
    async with app:
        async with grpc.aio.insecure_channel(f"127.0.0.1:{app.bound_port}") as channel:
            assert result(await call(channel))["amount"] == 1999
            for name, (code, details) in cases.items():
                error = await expect_error(call(channel, name), getattr(grpc.StatusCode, code), details)
                assert PRIVATE_MARKER not in error.details()
                await wait_until(lambda: len(metrics.rows) == 1 + list(cases).index(name) + 1)
                assert metrics.rows[-1]["grpc_code"] == code
                assert metrics.rows[-1]["duration"] >= 0
            await expect_error(
                channel.unary_unary(f"/{SERVICE}/Abort")(b"", timeout=2),
                grpc.StatusCode.UNAUTHENTICATED, "authentication_required",
            )
            await wait_until(lambda: len(metrics.rows) == 9)
            assert metrics.rows[-1]["grpc_code"] == "UNAUTHENTICATED"
    assert reporter.errors == ["InvoiceStoreUnavailable", "PrivateLedgerError", "RuntimeError", "ValueError"]
    assert store.active == 0
    print("PASS explicit contract: seven errors, success, deliberate abort, final metrics, four server reports")


async def reporting_order():
    reporter = Reporter()
    app = GrpcApp(server_config(), interceptors=[
        AsyncSentryInterceptor(reporter), exception_handler(),
    ])
    app.register(lambda server: register_invoice_service(server, InvoiceStore()))
    async with app:
        async with grpc.aio.insecure_channel(f"127.0.0.1:{app.bound_port}") as channel:
            await expect_error(call(channel, "bug"), grpc.StatusCode.INTERNAL, "internal_error")
    assert reporter.errors == []
    print("PASS wrong reporter order: client gets INTERNAL, reporter misses the original exception")


async def main():
    async with asyncio.timeout(20):
        await defaults()
        await explicit_contract()
        await reporting_order()


if __name__ == "__main__":
    logging.basicConfig(level=logging.CRITICAL)
    asyncio.run(main())
