"""Assertions executed inside each isolated installation by footprint.py."""

import asyncio
import importlib
import importlib.util
import sys
from importlib.metadata import distributions


def absent(*modules):
    for module in modules:
        assert importlib.util.find_spec(module) is None, module
        assert module not in sys.modules, module


def expect_extra(action, extra):
    try:
        action()
    except ImportError as error:
        assert extra in str(error), str(error)
        print(f"ImportError: {error}", flush=True)
    else:
        raise AssertionError(f"Missing {extra} was not reported")


def check_client_core():
    from clientwright import build, capabilities_matrix, registered_adapters
    from warehouse_policy import warehouse_config

    config = warehouse_config("http://127.0.0.1:1")
    assert config.timeout.total == 2
    names = registered_adapters()
    assert names == ("aiohttp", "httpx", "httpx2", "requests", "urllib3")
    assert set(capabilities_matrix()) == set(names)
    importlib.import_module("clientwright.adapters.httpx")
    absent("httpx", "httpx2", "aiohttp", "requests", "urllib3", "deadline_budget")
    expect_extra(lambda: build("httpx", config), "clientwright[httpx]")
    print(f"registered adapters: {names}", flush=True)


def check_deadline_core():
    from deadline_budget import BudgetContext

    budget = BudgetContext.create(total_seconds=1)
    assert 0 < budget.remaining() <= 1
    assert not budget.expired()
    absent("httpx", "fastapi", "clientwright", "servicewright")


def check_service_core():
    from servicewright import AppSpec, Service

    assert AppSpec is not None and Service is not None
    absent("fastapi", "starlette", "pydantic", "uvicorn")
    expect_extra(
        lambda: importlib.import_module("servicewright.adapters.fastapi"),
        "servicewright[fastapi]",
    )


def check_fastapi_extra():
    from servicewright.adapters.fastapi import FastApiEntrypoint, HttpConfig

    entrypoint = FastApiEntrypoint(config=HttpConfig(host="127.0.0.1", port=0))
    assert "fastapi" in sys.modules
    assert entrypoint.app is None and entrypoint.bound_port is None
    absent("httpx", "clientwright")


async def check_http_extra(with_budget):
    import httpx
    from clientwright import build
    from http_flow import fetch_stock
    from warehouse_policy import warehouse_config

    calls = []
    tasks = set()
    errors = []

    async def serve(reader, writer):
        try:
            async with asyncio.timeout(5):
                raw = (await reader.readuntil(b"\r\n\r\n")).decode("ascii")
                lines = raw.split("\r\n")
                headers = dict(
                    line.lower().split(": ", 1) for line in lines[1:] if line
                )
                calls.append((lines[0], int(headers["x-deadline-ms"])))
                body = b'{"available": 3}'
                writer.write(
                    b"HTTP/1.1 200 OK\r\nContent-Type: application/json\r\n"
                    + f"Content-Length: {len(body)}\r\nConnection: close\r\n\r\n".encode()
                    + body
                )
                await writer.drain()
        except Exception as error:  # noqa: BLE001 - fail the main assertion with fixture errors
            errors.append(error)
        finally:
            writer.close()
            await writer.wait_closed()

    def connected(reader, writer):
        tasks.add(asyncio.create_task(serve(reader, writer)))

    async with await asyncio.start_server(connected, "127.0.0.1", 0) as server:
        port = server.sockets[0].getsockname()[1]
        base_url = f"http://127.0.0.1:{port}"
        async with build("httpx", warehouse_config(base_url)) as client:
            assert type(client) is httpx.AsyncClient
        assert client.is_closed
        if with_budget:
            from budget_flow import fetch_with_budget

            result = await fetch_with_budget(base_url)
            limit = 500
        else:
            absent("deadline_budget", "fastapi", "aiohttp", "requests")
            try:
                importlib.import_module("budget_flow")
            except ModuleNotFoundError as error:
                assert error.name == "deadline_budget"
            else:
                raise AssertionError(
                    "Required application budget was silently disabled"
                )
            result = await fetch_stock(base_url)
            limit = 2000
        assert result == {"available": 3}
        await asyncio.gather(*tasks)
        assert not errors, errors
        assert len(calls) == 1 and calls[0][0] == "GET /stock/sku-42 HTTP/1.1", calls
        assert 0 < calls[0][1] <= limit, calls
        print(f"HTTP 200; propagated budget <= {limit} ms", flush=True)


if __name__ == "__main__":
    case = sys.argv[1]
    if case.endswith("-core"):
        expected = case.removesuffix("-core")
        names = {dist.metadata["Name"].lower() for dist in distributions()}
        assert names == {expected}, names
    if case == "clientwright-core":
        check_client_core()
    elif case == "deadline-budget-core":
        check_deadline_core()
    elif case == "servicewright-core":
        check_service_core()
    elif case == "servicewright-fastapi":
        check_fastapi_extra()
    elif case in ("clientwright-httpx", "clientwright-httpx-deadline"):
        asyncio.run(check_http_extra(with_budget=case.endswith("-deadline")))
    else:
        raise ValueError(case)
    print(f"PASS: {case}", flush=True)
