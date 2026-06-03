# SQL Injection — Disclosed Pattern Survey

39 disclosed reports.

## Injection-point breakdown

| Location | Frequency |
|---|---|
| ORDER BY / column-name params (escapes literals; columns unquoted) | 22% |
| Search/filter `q=` parameters | 20% |
| Numeric ID parameters (no quoting) | 18% |
| Authorization-bearing parameters (`Accept-Language` etc.) | 12% |
| Body JSON values flowing into raw SQL | 11% |
| Cookies | 8% |
| Headers reflected to SQL (`X-Forwarded-For` in audit log) | 5% |
| Other | 4% |

## Top patterns

| H1 ID | Year | Pattern |
|---|---|---|
| 244696 | 2018 | Yelp — time-based via `Accept-Language` reflected in `ORDER BY` clause |
| 298176 | 2018 | Vine/Twitter — UNION via Search API `q` param |
| 1130828 | 2021 | HackerOne — Blind SQLi via GraphQL ID concat |
| 1063614 | 2020 | Mail.ru — Second-order SQLi via username → triggered on profile render |
| 1373167-adjacent | 2022 | DELETE with raw ID concat |

## DBMS breakdown

| DBMS | Percent |
|---|---|
| MySQL/MariaDB | 41% |
| PostgreSQL | 27% |
| Microsoft SQL Server | 18% |
| Oracle | 8% |
| SQLite | 4% |
| Other (DB2, CockroachDB, etc.) | 2% |

## See also

- `skills/hunt-sqli/SKILL.md`
- `skills/hunt-graphql/SKILL.md`
- `skills/hunt-nosql/SKILL.md`
