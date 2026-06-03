# Usage

CBH exposes 15 slash commands. Each maps to one phase of an engagement.

## Slash command reference

| Command | Purpose |
|---------|---------|
| `/surface target=<host>` | Build initial scope + asset inventory |
| `/recon target=<host>` | Subdomain / endpoint / secret enumeration |
| `/intel target=<host>` | Fingerprint stack → CVE & misconfig matrix |
| `/hunt target=<host> [class=<vuln>]` | Auto-load relevant `hunt-*` skills |
| `/chain finding=<id>` | Compose multi-vuln chain to reach impact |
| `/validate finding=<id>` | 7-question gate → KILL/DOWN/CHAIN/SHIP |
| `/triage finding=<id>` | Decide reportable, dedupe against known issues |
| `/report finding=<id> platform=<h1\|bc\|intigriti\|immunefi\|client>` | Render report |
| `/token-scan path=<dir>` | Scan JS bundles / Git history for secrets |
| `/web3-audit target=<contract>` | Solidity / OpenZeppelin invariant checks |
| `/autopilot target=<host>` | Run surface→recon→intel→hunt non-stop |
| `/pickup engagement=<dir>` | Resume an engagement: re-read scope, chains, last verdict |
| `/memory-gc` | Compact engagement notes; archive verdicts older than 30 days |
| `/remember note=<text>` | Append a durable note to the engagement memory |

## End-to-end walkthrough

### 1. Start an engagement

```
/surface target=app.example.com program=h1-acme
```

Claude responds with a generated `engagements/app.example.com-2026-01-15/`
folder, pre-populated `scope.md` with common bounty out-of-scope patterns
(rate-limit-only, missing security headers w/o impact, EXIF disclosure,
self-XSS, logout CSRF, banner grabbing). Edit `scope.md` to add the
program's actual accepted-impact list and asset rules.

### 2. Recon

```
/recon target=app.example.com
```

Loads `offensive-osint` and `recon-stack`. Returns a checklist:

- subfinder + assetfinder + amass passive
- httpx for liveness + tech detection
- gau + waybackurls + katana for endpoint corpus
- nuclei with `-t exposures/` + `-t cves/`
- GitHub dorks via `dork-corpus.md`
- `cbh.py token-scan --bundle <js-url>` on each discovered JS bundle

### 3. Intel

```
/intel target=app.example.com
```

Reads `recon-notes.md`, identifies the stack (e.g. "Spring Boot 2.6 +
nginx 1.18 + OAuth via Okta"), and emits:

- CVE list filtered to detected versions
- Misconfig matrix (Okta `prompt=none` IdP-initiated flow, Spring
  Cloud Function SpEL, nginx `merge_slashes off` smuggling)
- Suggested `/hunt class=` invocations

### 4. Hunt

```
/hunt target=app.example.com class=oauth
```

Loads `hunt-oauth`. Claude emits the 5-phase OAuth attack checklist:

1. `redirect_uri` validation (exact-match, suffix, fragment, traversal)
2. `state` parameter CSRF + omission tests
3. Authorization-code interception (referer, PostMessage, open redirect)
4. Implicit-flow misuse (`response_type=token` enabled?)
5. Token leakage in `Referer` / browser history / iframe

For every phase Claude shows the disclosed-report ID(s) the technique
comes from and the curl/Burp commands to reproduce.

### 5. Chain (when single bug ≠ ship)

```
/chain finding=oauth-redirect-uri-bypass
```

Loads `hunt-oauth` + `hunt-redirect` + `triage-validation`. Claude
constructs the chain: open redirect on `/logout?return=` → OAuth
`redirect_uri` allow-list matches `.example.com` via subdomain
takeover → code interception → full account takeover.

### 6. Validate

```
/validate finding=oauth-ato-chain
```

Triggers the 7-question gate. Claude returns:

```
Q1 real HTTP request?      ✅ POC URL + curl chain
Q2 accepted impact?        ✅ ATO is P1 per program
Q3 in scope?               ✅ app.example.com matches *.example.com
Q4 admin-only assumption?  ✅ standard user
Q5 publicly disclosed?     ✅ checked H1 hacktivity + program known-issues
Q6 concrete impact?        ✅ screenshot of victim account post-takeover
Q7 never-submit list?      ✅ not logout CSRF / self-XSS / etc.

VERDICT: SHIP — severity Critical (CVSS 9.6) — H1 template ready
```

### 7. Report

```
/report finding=oauth-ato-chain platform=h1
```

Loads `h1-reporting`. Outputs ready-to-paste H1 markdown with:

- Title following program's convention
- Summary (1 paragraph, no fluff)
- Steps to reproduce (numbered, every URL parameterized)
- Impact (linked to program's accepted-impact taxonomy)
- Remediation
- Evidence (redacted HAR path, screenshot sequence: unauth → auth)
- Severity (CVSS 3.1 vector + program's adjusted SLA)

## Workflows

### Bug bounty triage hygiene

`/triage` runs **before** `/report`. It dedupes against:
- Program-disclosed issues (H1 hacktivity for the program)
- `known-issues` block in `scope.md`
- Your own past submissions in `engagements/*/findings/`

### Red-team engagement

`/autopilot target=corp.acme.com mode=redteam` switches all hunt skills
to red-team mode via `redteam-mindset`:

- Never stop at first vuln if scope is "compromise the domain"
- Always check credential reuse across discovered services
- Document every HTTP request for client evidence
- `mid-engagement-ir-detection` runs in the background — re-probes
  baseline endpoints every 30 minutes to detect blue-team patching

### Resuming

```
/pickup engagement=engagements/app.example.com-2026-01-15
```

Claude re-reads `scope.md`, `chains.md`, last verdict in `findings/`,
and asks "where do you want to continue?"
