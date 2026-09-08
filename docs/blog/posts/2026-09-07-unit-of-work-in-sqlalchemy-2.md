---
date: 2026-09-07
authors:
  - alex
categories:
  - Tutorials
tags:
  - sqlalchemy-foundation-kit
  - sqlalchemy
  - unit-of-work
  - postgresql
  - transactions
  - testing
---

# The Unit of Work pattern in SQLAlchemy 2

<div class="bdr-post__hero" data-bdr-post="2026-09-07-unit-of-work-in-sqlalchemy-2" role="img" aria-label="One transaction boundary owned by the use case, one commit at its edge" markdown="0"></div>

Every repository I have ever seen written for the first time has a `commit()` in it. It is there so that the id comes back, so that the next repository can use it, so that the test can read the row, and it is the single decision that makes a service's data model impossible to reason about, because a use case that touches two repositories now has two commits and a failure between them leaves half of itself in the database. The fix is old, it has a name, and SQLAlchemy 2 makes it short: the use case owns the transaction, the repositories write into it, and the commit happens once, at the end, or not at all. This post is that pattern with the before and after measured, plus the two things it makes possible that the self-committing repository cannot do: a read-only block that discards writes, and a use case that can be tested without a database.

<!-- more -->

The numbers come from [the post's lab script](https://github.com/bedrock-python/bedrock-python.github.io/tree/master/docs/blog/lab/2026-09-07-unit-of-work-sqlalchemy-2), against PostgreSQL 17 in a container. Versions: SQLAlchemy 2.0.52, asyncpg 0.31.0, sqlalchemy-foundation-kit 0.3.0, Python 3.13.

## Before: repositories that commit

Two tables, `users` and `orders`, and a check constraint that says an order's amount must be positive. Two repositories written the way they usually are the first time:

```python
class SelfCommittingUserRepo:
    async def add(self, email: str) -> User:
        user = User(email=email)
        self.session.add(user)
        await self.session.commit()          # "so the id is there"
        return user


class SelfCommittingOrderRepo:
    async def add(self, user_id: int, amount: int) -> Order:
        order = Order(user_id=user_id, amount=amount)
        self.session.add(order)
        await self.session.commit()
        return order
```

And a use case that creates a user and their first order, where the order is invalid:

```text
repositories commit for themselves -> users=1 orders=0   (a user with no order: half a use case)
```

The user is in the database. The order is not. From the caller's point of view the operation failed; from the database's point of view it half succeeded, and the next attempt will fail differently, on the unique email. This is not an edge case of this particular code, it is the property of any design where the unit of persistence is smaller than the unit of business meaning. The repository does not know that the user only makes sense with the order, because the repository is not where that knowledge lives.

## After: the use case owns the boundary

Same tables, same repositories minus one line each. `flush()` instead of `commit()`: the row is sent to the database, the id comes back, and nothing is committed:

```python
class UserRepo:
    async def add(self, email: str) -> User:
        user = User(email=email)
        self.session.add(user)
        await self.session.flush()           # the id is there; nothing is committed
        return user
```

The transaction is a class that exposes the repositories over one session, and the unit of work is what opens it:

```python
class Transaction(AsyncSQLAlchemyUowTransaction):
    @property
    def users(self) -> UserRepo:
        return UserRepo(self.session)

    @property
    def orders(self) -> OrderRepo:
        return OrderRepo(self.session)


class PlaceOrder:
    def __init__(self, uow: AsyncSQLAlchemyUnitOfWork[Transaction]) -> None:
        self.uow = uow

    async def execute(self, email: str, amount: int) -> int:
        async with self.uow.transaction() as tx:   # commits on exit, rolls back on exception
            user = await tx.users.add(email)
            order = await tx.orders.add(user.id, amount)
            return order.id
```

The use case never sees a session. It opens a transaction, works through the repositories it exposes, and returns; the block commits on the way out, or rolls back if anything raised. The same invalid order:

```text
the use case owns the transaction  -> users=0 orders=0   (nothing happened)
```

And the valid one:

```text
order 2 -> users=1 orders=1   (one commit, both rows)
```

One commit, both rows, or no commit and no rows. The order id is 2 and not 1 because the failed attempt consumed a sequence value before it rolled back; sequences are the one thing in PostgreSQL that does not participate in the transaction, which is worth knowing the first time a gap in the ids gets reported as a bug.

## Read-only means read-only

The second thing the pattern gives you is a block that promises it will not write:

```python
async with uow.query() as qx:
    users = await qx.users.list()
```

The promise is enforced, not documented. A write that sneaks into a query block is not committed:

```text
after uow.query() -> users=1 orders=1   (the write was discarded)
```

That is the difference between a comment saying "read only" and a boundary that means it. Every read path in the service goes through `query()`, every write path through `transaction()`, and a reviewer can tell from the block which one they are looking at without reading the repository.

## Savepoints: one failed step, not one failed transaction

On PostgreSQL a failed statement aborts the whole transaction: every statement after it fails until rollback, including the ones you would use to record which step failed. A savepoint is a nested transaction that can fail on its own:

```python
async with uow.transaction() as tx:
    user = await tx.users.add("b@example.com")
    try:
        async with tx.savepoint():
            await tx.orders.add(user.id, amount=-1)      # fails; the savepoint rolls back
    except IntegrityError:
        pass
    await tx.orders.add(user.id, amount=20)              # still inside a live transaction
```

```text
-> users=2 orders=2   (the bad order rolled back, the good one and the user committed)
```

Without the savepoint the second `add` would have failed with "current transaction is aborted", and so would the commit. With it, the boundary of the failure is the boundary you drew.

## The use case under test

The third thing, and the reason the pattern pays for itself in the first week: the use case depends on an object with a `transaction()` method that yields something with `users` and `orders` on it. Nothing in that description says SQLAlchemy. A fake with a list instead of a database is twenty lines, and the use case runs against it unchanged:

```text
order 2, rows written=[('t@example.com',), (1, 7)], commits=1, 0.0 ms, no PostgreSQL
```

The unit test asserts what the use case did, the rows it asked for and that it committed exactly once, in a fraction of a millisecond, with no container. The integration tests, the ones above, prove the real unit of work honours the same contract. That split is only possible because the session never leaked into the use case's signature.

## Who owns the transaction

The rule that comes out of all of this is short enough to enforce in review. Repositories flush; they never commit and never roll back. Use cases open one transaction, do all their work inside it, and let the block decide. Reads go through a block that cannot write. Anything that has to survive a failing step gets a savepoint around the step, not a second transaction. And the session is a resource with a lifetime equal to one block, handed to repositories by the transaction object, which is why no signature in the service takes an `AsyncSession` and why the use case can be tested with a list.

The unit of work above is [sqlalchemy-foundation-kit](https://bedrock-python.github.io/sqlalchemy-foundation-kit/guide/advanced/#unit-of-work-uow)'s `AsyncSQLAlchemyUnitOfWork`, which is the `transaction()`, `query()` and `savepoint()` blocks over any `async_sessionmaker` and a transaction class you write with your repositories on it; the session manager it sits on is the one from [the PgBouncer post](2026-09-07-pgbouncer-transaction-mode-async-sqlalchemy.md).

The point was the first two lines. `users=1 orders=0`, then `users=0 orders=0`.
