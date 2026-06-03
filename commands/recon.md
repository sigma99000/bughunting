---
name: recon
description: Run passive + light-active reconnaissance — subdomains, endpoints, secrets, dorks.
---

# /recon

**Args:** `target=<host> [depth=passive|light|full]`

## What this command does

Loads `offensive-osint` and `recon-stack`. Emits a phased plan and runs
the tooling that's installed locally. Falls back to manual instructions
where tools are missing.

### Phase 1 — passive subdomains

```bash
subfinder -d <target> -silent -all -recursive
assetfinder --subs-only <target>
amass enum -passive -d <target> -silent
curl -s "https://crt.sh/?q=%25.<target>&output=json" | jq -r '.[].name_value' | tr ',' '\n'
```

Dedupe → write to `recon-notes.md` under `## subdomains`.

### Phase 2 — liveness + tech

```bash
httpx -l subdomains.txt -tech-detect -title -status-code -ip -silent
```

### Phase 3 — endpoint corpus

```bash
gau <target> | tee endpoints.txt
waybackurls <target> >> endpoints.txt
katana -u https://<target> -d 3 -jc >> endpoints.txt
sort -u endpoints.txt > endpoints.dedup.txt
```

### Phase 4 — secret hunting (JS bundles, Git)

For every `*.js` URL discovered:

```
/token-scan path=<url-or-local-clone>
```

Loads `offensive-osint/references/secret-patterns.md` and runs
`secret_scan.py`.

### Phase 5 — dorks

Emit a curated dork list from `offensive-osint/references/dork-corpus.md`
filtered to the target's apex domain. Operator runs them manually
(GitHub / Google / Shodan refuse automation).

### Phase 6 — nuclei

```bash
nuclei -l live.txt -t exposures/ -t misconfiguration/ -t cves/ -severity critical,high
```

## Output contract

Update `recon-notes.md` with:
- Subdomain count
- Tech-stack frequency table
- Discovered secrets (count by class, exact values redacted)
- Top 10 most interesting endpoints (admin, debug, internal, /api/v1/)
- Suggested `/intel` and `/hunt` invocations

## Discipline

- All probes go through `scope.md` filter.
- No active fuzzing in this phase — that's `/hunt`.
- Rate-limit awareness: passive sources only when bounty program
  forbids active scanning.
