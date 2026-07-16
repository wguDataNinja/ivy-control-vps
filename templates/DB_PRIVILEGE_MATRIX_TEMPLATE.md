# Privilege Matrix Template

**Purpose:** Document positive (allowed) and negative (forbidden) permissions
for each PostgreSQL role. Validate before and after provisioning.

---

## Matrix

| Role | Positive permissions | Negative permissions to test |
|------|---------------------|------------------------------|
| `{project}_owner` | Owns schemas and objects; `NOLOGIN` | Cannot log in |
| `{project}_migrator` | `CONNECT`; migration-time DDL; `SET ROLE` to owner | Cannot run as superuser; cannot access unrelated databases; no DML on app tables outside migration |
| `{project}_writer` | `CONNECT`; DML only on application write tables/sequences | Cannot alter schema; cannot read restricted views; cannot write outside project schema |
| `{project}_reader` | `CONNECT`; `SELECT` on approved tables/views | Cannot INSERT/UPDATE/DELETE; cannot alter schema; cannot create objects |
| `{project}_monitor` | `CONNECT`; `SELECT` on health/current-state views | Cannot read raw sensitive tables; cannot write; cannot access app data |
| `{project}_backup` | `CONNECT`; read privileges needed for `pg_dump` | Cannot write; cannot alter; cannot create objects; cannot set session parameters |

## Validation SQL pattern

### Positive test (example: writer)

```sql
-- Connect as writer role and verify INSERT works
SET ROLE {project}_writer;
INSERT INTO {schema}.{table} (col) VALUES ('test') RETURNING id;
ROLLBACK;
```

### Negative test (example: writer)

```sql
-- Verify writer cannot alter schema
SET ROLE {project}_writer;
CREATE TABLE {schema}.should_not_exist (id int);  -- expected: ERROR
```

## Grant template

```sql
-- Connection
GRANT CONNECT ON DATABASE {project} TO {project}_writer;

-- Schema usage
GRANT USAGE ON SCHEMA app TO {project}_writer;

-- Table DML
GRANT SELECT, INSERT, UPDATE, DELETE ON ALL TABLES IN SCHEMA app TO {project}_writer;
ALTER DEFAULT PRIVILEGES IN SCHEMA app GRANT SELECT, INSERT, UPDATE, DELETE ON TABLES TO {project}_writer;

-- Sequences
GRANT USAGE ON ALL SEQUENCES IN SCHEMA app TO {project}_writer;
ALTER DEFAULT PRIVILEGES IN SCHEMA app GRANT USAGE ON SEQUENCES TO {project}_writer;
```
