# Lab: bare cores and optional integrations {#lab-what-a-library-costs-to-install-and-to-import}

Executable example for [A core without dependencies](../../posts/2026-09-07-zero-dependency-cores.md). It tests what works before an extra is installed and what becomes available afterwards.

## Run {#run}

With uv installed, run from the website repository root:

```bash
cd docs/blog/lab/2026-09-07-zero-dependency-cores
uv run --no-project --python 3.13 python footprint.py
```

The runner uses the standard library. It creates three temporary Python 3.13 environments without pip or access to the caller's site-packages, installs packages through `uv pip` with `constraints.txt`, and executes assertions in fresh subprocesses. Environment paths support Windows and POSIX. No Docker or external HTTP endpoint is required; downloading Python and packages requires network access. Temporary environments are removed when their checks finish.

## Checks {#checks}

| Installation | Assertion |
|---|---|
| `deadline-budget==0.1.3` | Only one distribution; the budget works without clientwright or web packages |
| `clientwright==0.5.0` | Only one distribution; configuration, registry and capabilities work without HTTP SDKs |
| Missing httpx | `build("httpx", config)` raises an error naming `clientwright[httpx]` |
| `clientwright[httpx]==0.5.0` | Real local HTTP request, native client type, client cleanup; deadline-budget remains absent |
| Missing application budget | Importing `budget_flow.py` fails instead of silently disabling its required deadline |
| `clientwright[httpx,deadline]==0.5.0` | The same HTTP request carries at most 500 ms instead of the configured two seconds |
| `servicewright==0.13.1` | Only one distribution; importing the FastAPI adapter names the missing extra |
| `servicewright[fastapi]==0.13.1` | The adapter imports and an entrypoint object can be constructed |

The three bare installs are independent. HTTP and deadline extras are added in sequence to the clientwright environment; the FastAPI extra is added to the servicewright environment. `--constraint` pins versions without installing unrelated packages. A failed command or assertion makes the runner exit unsuccessfully. Subprocesses and HTTP operations have time limits.

The servicewright check covers installation and entrypoint construction, not starting a complete service. The [composition lab](../2026-09-07-what-every-microservice-reimplements/README.md) checks the latter. The warehouse fixture only records the deadline header; it does not enforce a server-side deadline.

## Optional measurements {#measurements}

```bash
uv run --no-project --python 3.13 python footprint.py --measure --report footprint-results.json
```

The JSON report includes UTC time, platform, Python version, every installed distribution and version, `site-packages` file size in MiB, five import samples and their median for each installation stage. The count includes the library itself. Size is the sum of file lengths, not downloaded wheel size or allocated filesystem space; imports use `-B` to avoid writing bytecode during the probe.

Each timing sample imports the package root in a fresh process. It excludes interpreter startup, leaves the OS file cache active and does not import every optional integration. These are local observations, not a benchmark ranking. The functional checks do not assert exact timings or disk sizes. The report is written only when all scenarios pass.

## Files {#files}

- `warehouse_policy.py`: configuration that imports only clientwright.
- `http_flow.py`: the HTTP operation using that configuration.
- `budget_flow.py`: the same operation with a required deadline-budget context.
- `probe.py`: absence checks, import errors and local HTTP assertions.
- `footprint.py`: temporary environments, installation, subprocesses and report.
- `constraints.in` and `constraints.txt`: selected integrations and resolved dependency versions.

To refresh pins deliberately, update `constraints.in` and the versions in `footprint.py`, compile the constraints, then rerun the lab. The checked-in constraints were resolved for Python 3.13 across platforms; platform markers still control which distributions get installed.
