# cbh.py — CLI reference

## Installation

`scripts/install.sh` creates `~/.local/bin/cbh` as a shim. Otherwise:

```bash
alias cbh="python3 /path/to/claude-bughunter/scripts/cbh.py"
```

## Subcommands

### `cbh surface --target <host> [--program <slug>] [--type bugbounty|pentest|redteam] [--out engagements/] [--force]`

Scaffolds an engagement folder with the canonical structure
(`scope.md`, `recon-notes.md`, `chains.md`, `findings/`,
`evidence/`).

```bash
cbh surface --target app.example.com --program h1-acme --type bugbounty
# → engagements/app.example.com-2026-01-15/
```

### `cbh recon --target <host>`

Prints the 6-phase recon plan (passive subdomains → tech → endpoints
→ secrets → dorks → nuclei). Doesn't run the tools — just emits the
commands so you can review and execute.

### `cbh classify [--file <dump>]`

Reads an HTTP request/response dump (from stdin or `--file`) and
suggests the relevant `hunt-*` skill(s) based on signal keywords.

```bash
cat suspicious-request.txt | cbh classify
# → {"matched_skills": ["hunt-oauth", "hunt-redirect"]}
```

### `cbh triage --file <finding.md>`

Runs a heuristic version of the 7-question validation gate against
a finding markdown file. Useful for pre-screening before invoking
the full `/validate` in Claude Code.

```bash
cbh triage --file engagements/.../findings/oauth-001.md
# Q1 real HTTP request: ✅
# ...
# VERDICT: SHIP
```

Exit code 0 = SHIP, 1 = REVIEW.

### `cbh report --finding <id> --platform h1|bc|intigriti|immunefi|client`

Stub-only. The full rendering lives in Claude Code's `/report`
command which has access to the skill bodies. CLI version prints
which platform you'd render to.

### `cbh token-scan --path <file|dir|url> [--json]`

Proxies to `skills/offensive-osint/scripts/secret_scan.py`. Scans
for 50+ secret patterns with entropy filtering.

```bash
cbh token-scan --path https://target/static/js/main.abc123.js
# [STRIPE_LIVE_SECRET] /tmp/abc.js:1234  sk_l••••••••••••••••••••••••2x9q  (entropy 4.87)
```

## Environment

| Var | Use |
|---|---|
| `CLAUDE_HOME` | Override `~/.claude` (used by `install.sh`) |
| `NVD_API_KEY` | NVD API key for faster CVE fetches (used by `refresh-cve-index.py`) |

## Exit codes

| Code | Meaning |
|---|---|
| 0 | Success / SHIP verdict |
| 1 | REVIEW verdict / soft failure |
| 2 | Usage error (bad args, missing file) |

## See also

- `architecture.md`
- `commands/` for the Claude Code slash-command equivalents
