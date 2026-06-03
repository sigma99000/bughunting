# Verification Labs

Intentionally-vulnerable reproduction recipes for skill validation.

## Lab discipline

- **127.0.0.1 only.** Every `docker-compose.yml` binds to localhost.
  Never expose these to the public internet.
- **No real secrets.** Lab keys / passwords are literally `lab` /
  `password`.
- **Reset between runs.** `docker compose down -v` after each run.
- **Don't reuse lab payloads in production.** Lab payloads are
  often calibrated against specific lab quirks.

## Labs

| Folder | Skill(s) exercised | Format |
|---|---|---|
| `phase2e/` | JWT + GraphQL + race condition | Flask app + Foundry-style PoC |
| `phase2f/` | SSTI + OAuth + file upload | Flask app |
| `phase2g/` | Path traversal — Apache CVE-2021-41773 | docker-compose |
| `phase2h/` | HTTP request smuggling (CL.TE) | docker-compose: nginx + origin |
| `phase2i/` | LLM ATO via indirect injection | Flask app emulating agent |
| `phase2j/` | Cloud + LocalStack — SSRF → IMDS → S3 | docker-compose + LocalStack |

## CVE walkthroughs (no lab — uses documented public-PoC steps)

- `apache-cve-2021-41773.md`
- `jenkins-cve-2024-23897.md`
- `spring-cve-2022-22963.md`

## Running a lab

```bash
cd docs/verification/phase2g
docker compose up -d
# follow the README in that folder
docker compose down -v   # clean up
```

If a lab folder is missing a `README.md`, see this index — none of
the labs are production-ready yet; they're operator reference.
