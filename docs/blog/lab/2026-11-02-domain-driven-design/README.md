# Lab: the code from the Domain-Driven Design article

Runnable checks for [the article](../../posts/2026-11-02-domain-driven-design.md).
Docker must be running. The script creates and removes its own PostgreSQL container;
it does not use an existing database. Run from this directory in a repository checkout:

```bash
uv run --no-project --python 3.13 --with-requirements requirements.txt ddd_lab.py
```

Dependencies are pinned in `requirements.txt`: sqlalchemy-foundation-kit 0.5.1, omni-box 0.3.1,
SQLAlchemy 2.1.6, asyncpg 0.32.0 and testcontainers 4.15.0. The image is `postgres:17-alpine`;
the script prints its server version (17.11 in the verified run).
sqlalchemy-foundation-kit 0.5.1 is the first release that imports on SQLAlchemy 2.1
([#78](https://github.com/bedrock-python/sqlalchemy-foundation-kit/issues/78), found while writing this lab).

The lab keeps no copy of the article's code. `ddd_lab.py` reads the code blocks from the English
and Russian editions, checks that both show the same code, and runs each block in a fresh namespace
with the names it takes for granted. `support.py` holds what the article leaves out: the tables,
the repositories and the full `User` with CanExecute / Execute and domain events.

In memory it checks that:

- the anemic `PersonService` leaves `is_employee` stale, as the article says;
- the eleventh order makes a `Customer` Advanced, and the orders are read-only;
- `OverbookingPolicy` accepts 110% of capacity and refuses 111%;
- the functional core returns a `FileUpdate` that the shell applies, and the article's test passes without a disk;
- each of the three trilemma options rejects a taken address;
- with CanExecute / Execute the controller asks first, and calling `change_email` around the check raises (the block has no `assert`);
- `Money` is equal by value and checks currency and sign; `Order` is equal by id and stays hashable;
- `transfer`, `DelinquentInvoice` and the `MessageBus` wrapper behave as described.

On PostgreSQL it adds the article's unique constraint with its `ALTER TABLE` and runs the assembled `change_email`:

- the user, the company and the outbox row commit together, and the event carries `aggregate_type="user"`;
- a confirmed email and a taken address leave nothing written;
- a failing outbox write rolls back the user and the company;
- two transactions both read the address as free before either writes; the constraint lets one commit, and the other gets `Email is taken`;
- with ORM-tracked saves, the violation surfaces at the flush that `transaction()` runs before commit, still as `IntegrityError`.

Fragments the article prints as partial classes (the aggregate, the repository over `_db`, the `User` that records events)
are not run as printed; `support.py` has the complete versions the PostgreSQL checks use.
The script prints `PASS: article snippets` only when all assertions succeed.
