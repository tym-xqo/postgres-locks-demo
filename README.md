# PostgreSQL Locks

## ACID Transactions

- **A**tomic
- **C**onsistent
- **I**solated
- **D**urable

## MVCC

**Multi Version Concurrency Control**  
(a mechanism for ensuring transaction isolation)

- Postgres assigns a XID to every transaction
- Every table row has hidden columns `xmin` and `xmax`
- Each query sees only transactions completed before it started
- UPDATE actually creates a new row, with appropriate XID values
- Similarly with DELETE, changes XIDs and marks as deleted
- Eventually some rows are older any active or future transaction; VACUUM freezes and marks these dead
- ___Reads never block writes, writes never block reads___
- Locks are generally lighter weight and fewer than using other concurrency techniques, which depend mainly on locking (e.g. SQL Server default)

## Locks

- Needed to prevent concurrent access to the same data, so that data are not dropped or modified in incompatible ways.
- Lock modes
  - Table-level (*mostly* DDL and VACUUM)
  - Row-level (SELECT, UPDATE, DELETE)
  - Share (many transactions can hold concurrently)
  - Exclusive (only one transaction can hold at a time)
- Postgres lock modes have legacy naming issues
- Essentially defines a hierarchy of lock levels
  > The only real difference between one lock mode and another is the set of lock modes with which each conflicts  
  > – <https://www.postgresql.org/docs/current/explicit-locking.html>
- Whether a transaction can acquire a lock depends on whether its lock level conflicts with that of an existing earlier lock
- Locks can be taken on a variety of objects, including indexes, tuples, system catalog tables, and transactions themselves

## Lock Queue and Blocking Locks

- First request granted first (even if less restrictive)
- Subsequent locks can back up behind a long-waiting lock

Textbook example: Creating a new table, with a foreign-key reference to another table that has a long-running query against it.

## Deadlocks

Occurs when two (or more) transactions are mutually blocking each other's lock acquisition

- Transaction 1:
  - updates row 1 on `table_a` (takes ROW EXCLUSIVE lock)
  - updates row 1 on `table_b` (waits for transaction 2)
- Transaction 2:
  - updates row 1 on `table_b` (ROW EXCLUSIVE lock)
  - updates row 1 on `table_a` (waits for transaction 1)

- Postgres arbitrarily kills one or the other after `deadlock_timeout` elapses (default 1 sec)
- Retry logic is not a bad a way to handle these

## Avoiding lock contention issues

NB: these are suggestions. All are good ideas, but locks are not inherently evil, and application logic is paramount

- Keep transactions as simple as possible; only combine the minimum number of operations
- Make sure to close transactions
  - Understand your ORM (when is it beginning and completing transactions)
  - Close quickly (avoid opening a transaction while waiting for user input, e.g.)
- Avoid explicit locking (SELECT FOR UPDATE)
- In multistep transactions, take aggressive locks late
- Avoid deadlocks by ordering statements
- Migrations/DDL need special handling
  - Often take table-level `ACCESS EXCLUSIVE` locks
  - Set `lock_timeout`
  - Don't add column with default value
  - Create indexes concurrently
  - Create unique index before adding primary key constraint