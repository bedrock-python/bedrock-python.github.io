---
date: 2026-09-07
authors:
  - alex
categories:
  - Design
tags:
  - deadline-budget
  - clientwright
  - servicewright
  - packaging
  - dependencies
---

# Zero-dependency cores: why optional dependencies matter in infrastructure libraries

An infrastructure library is one that ends up in every service, and every dependency it declares ends up there too. That is the whole argument, and it is usually made in the abstract. So I measured it: for eight libraries, what a bare install actually pulls in, how many megabytes it puts on disk, and how long importing it costs. The smallest core installs one distribution and imports in 1.2 milliseconds. The one with a hard database driver installs nine and imports in 117.

<!-- more -->

The numbers come from [the post's lab](https://github.com/bedrock-python/bedrock-python.github.io/tree/master/docs/blog/lab/2026-09-07-zero-dependency-cores), which builds a throwaway virtual environment per package, counts what landed in it and times the import five times. Python 3.13, measured today against the published versions.

## What each library costs

```text
    package                     deps      MB  import ms   with the extra
    deadline-budget                1     0.1        1.2
    clientwright                   1     0.3       23.9
    grpc-client-kit                3    38.3       27.6   [deadline]: +1 deps, +0.7 MB
    redis-client-kit               2     2.6       43.4   [settings]: +7 deps, +8.7 MB
    servicewright                  1     0.4       30.1   [fastapi]: +22 deps, +16.4 MB
    sqlalchemy-foundation-kit      9    18.1      124.7   [metrics]: +1 deps, +7.9 MB
    aiokafka-foundation-kit        5     2.0       33.4   [models]: +4 deps, +7.1 MB
    pg-partsmith                  10    17.4      107.6   [cli]: +9 deps, +14.1 MB
```

Three libraries install exactly one distribution: themselves. `deadline-budget` is a deadline that propagates, and it needs nothing to be one. `clientwright` builds HTTP clients and depends on no HTTP library, because which one you use is your decision, not its. `servicewright` runs an application's lifecycle and depends on no web framework, for the same reason.

The `[fastapi]` column is the number that makes the case: **twenty-two distributions and sixteen megabytes**, for a library whose core is one distribution and four hundred kilobytes. A service that runs a gRPC entrypoint and no HTTP one pays none of that.

## The failure mode this prevents

The reason to care is not disk. It is the resolver.

A library that hard-depends on FastAPI pins a range of FastAPI, which pins a range of Starlette and Pydantic. A service that uses that library and also uses another library with its own FastAPI range now has a resolution problem that neither library's author knew about. The more services and the more shared libraries, the more likely it is that some pair of them cannot be installed together — and that the fix is upgrading something unrelated across the whole fleet.

Every dependency an infrastructure library declares is a constraint it imposes on every service it touches. An optional one is a constraint only on the services that opted in.

Import time is the smaller effect and it is not nothing: 1.2 milliseconds against 124.7 is two orders of magnitude, and it lands on every process start, every CI job, every serverless cold start, and every `--help`.

## What a good core looks like

The pattern that produces the three one-distribution rows is: **the core is the decisions, the extras are the integrations.**

`clientwright` is the clearest case. Its core knows about timeouts, retries, budgets, breakers and metrics — the policy layer, which is the part worth sharing between services. It knows nothing about httpx, aiohttp, requests or urllib3; each of those is an adapter behind an extra, resolved by name at build time:

```text
    registered adapters without any HTTP library: ('aiohttp', 'httpx', 'httpx2', 'requests', 'urllib3')
```

All five are *registered* with no HTTP library installed, because the registry is a table of names and import paths, not a set of imports. That is what lets the capabilities matrix be documented and compared without installing anything, and it is why the adapter's absence only becomes an error when you ask for it:

```text
    build('httpx') -> ImportError: httpx support requires clientwright[httpx]; install it.
```

## The message is the feature

An optional dependency is a feature with a failure mode, and the failure mode is a message. There are three shapes in the lab, and the difference between them is the difference between a two-minute problem and a twenty-minute one:

```text
    servicewright     ImportError: FastAPI support requires servicewright[fastapi]; install it.
    redis-client-kit  ImportError: pydantic-settings not installed. Install
                      redis-client-kit[settings] to use BaseRedisSettings.
    grpc-client-kit   imported; HAS_DEADLINE_BUDGET = False
```

The first two name the extra. That is the whole requirement: the user typed an import, and the answer tells them exactly what to install. A bare `ModuleNotFoundError: No module named 'starlette'` — which is what the first line said before today's fix — names a package the user never asked for and cannot obviously map back to an extra.

The third is a different and deliberate shape: a feature that degrades instead of failing. The deadline layer is a no-op when the deadline package is absent, announced with a warning and a flag anyone can check, because a client without deadline propagation is still a working client. That choice is only right when the degraded behaviour is *safe*; a security check that silently no-ops is the same pattern and a disaster.

The rule I use: **raise when the absence changes correctness, degrade when it changes only capability, and never make either one silent.**

## When a hard dependency is right

Two rows in the table have real dependencies, and both are correct.

`sqlalchemy-foundation-kit` hard-depends on SQLAlchemy and asyncpg: nine distributions, 18 MB, 124 ms. It is a library *about* async SQLAlchemy against PostgreSQL; making the driver optional would be pretending the library has a use without it. `pg-partsmith` is the same argument with SQLAlchemy and Pydantic.

The test is not "can this be optional" but "is there a real user who wants this library without it". For a Redis client, there is no user who does not want redis-py. For a service lifecycle, there are many users who do not want FastAPI.

Where the answer is genuinely "some do, some do not", the shape is an extra plus a protocol: the core defines what it needs structurally, the extra ships an implementation. That is how metrics work across these libraries — the core takes anything with the right methods, and `[metrics]` adds one distribution and a Prometheus implementation for the services that want it.

## The checklist

- **Can a service use this library without dependency X?** If yes, X is an extra.
- **Does the core import X at module level anywhere?** One drifted import turns an extra into a hard dependency, silently, and the only way to know is a test that imports each optional subpackage in an environment without it.
- **Does the failure name the extra?** Test the message, not just the exception type.
- **Is the degraded path safe?** If it is not, do not degrade.
- **Would you accept this dependency in every service you own?** Because that is what declaring it means.

## The pieces

The measurements are across the [Bedrock Python](https://bedrock-python.github.io/) libraries, and the shape is the same in each: a core with no dependencies it can avoid, integrations behind extras, structural protocols instead of imports where a seam is enough. Two of the messages in this post were fixed today, because writing this post is what measured them.

One distribution and 1.2 milliseconds, or twenty-three distributions and sixteen megabytes. The difference is whether the library decided for you.
