# Claude Bug Hunter

> A battle-tested Claude Code skill bundle that turns Claude into a senior
> offensive-security operator for external attack-surface engagements.

Claude Bug Hunter (CBH) is **not** a toolkit. It is an opinionated knowledge
base that encodes the judgment of a senior bug-hunter / red-team operator:
when to chase a lead, when to kill a false positive, when a chain is
required, and how to stay in scope across bug bounty, authorized pentest,
and external red-team engagements.

```
┌─────────────────────────────────────────────────────────────┐
│                    CLAUDE BUG HUNTER                        │
│                                                             │
│   Recon  →  Surface  →  Hunt  →  Chain  →  Triage  →  Report│
│     │         │         │        │         │          │     │
│     ▼         ▼         ▼        ▼         ▼          ▼     │
│   /recon  /surface  /hunt    /chain   /validate    /report  │
│     │         │         │        │         │          │     │
│     └─── offensive-osint ──┴── 28 hunt-* skills ──┐         │
│                            │                      │         │
│                            ▼                      ▼         │
│                  enterprise platforms     7-Q validation    │
│                  (M365, Okta, VPN,         gate + KILL/     │
│                   SharePoint, vCenter)     DOWNGRADE/CHAIN  │
└─────────────────────────────────────────────────────────────┘
```

## What's in the box

| Layer | Count | Purpose |
|-------|-------|---------|
| `hunt-*` skills | 28 | One per vulnerability class — payload tables, bypass matrices, disclosed-report chain templates |
| Enterprise attack skills | 6 | M365/Entra, Okta, VPN appliances, SharePoint, vCenter, Exchange |
| Discipline skills | 6 | Red-team mindset, triage validation, evidence hygiene, IR detection, scope, payload discipline |
| Reporting skills | 6 | Bugcrowd VRT, H1, Intigriti, Immunefi, generic, red-team DOCX |
| Recon / OSINT | 3 | `offensive-osint` (14 reference files), `recon-stack`, `surface-mapping` |
| Web3 / LLM | 3 | `web3-audit`, `llm-attack`, `llm-ato` |
| **Slash commands** | **15** | `/recon /surface /hunt /chain /triage /validate /report /intel /token-scan /autopilot /pickup /memory-gc /remember /web3-audit` |
| Verification labs | 6 phases | Phase 2e–2j — Flask/Docker reproduction recipes |
| Disclosed-report corpus | 15 files | 681 real H1 reports grouped by class |

## The 7-question validation gate

Every finding routes through `triage-validation` before report-writing:

| # | Question | Fail verdict |
|---|----------|--------------|
| Q1 | Is there a real HTTP request demonstrating impact (not theoretical)? | KILL |
| Q2 | Is the impact on the program's accepted-impact list? | KILL / DOWNGRADE |
| Q3 | Is the asset in-scope per domain/subdomain rules? | KILL |
| Q4 | Are we free of admin-only / self-XSS / same-user assumptions? | DOWNGRADE |
| Q5 | Is it not publicly disclosed or on the program's known-issues list? | KILL |
| Q6 | Is impact concretely demonstrated (not "technically possible")? | CHAIN REQUIRED |
| Q7 | Is it not on the never-submit list (logout CSRF, banner grab, self-XSS, etc.)? | KILL |

## Quick start

```bash
git clone <this-repo> ~/.claude/skills/claude-bughunter
bash ~/.claude/skills/claude-bughunter/scripts/install.sh
```

Then in Claude Code:

```
/hunt target=app.example.com program=h1-acme scope=*.example.com
```

See [`INSTALL.md`](INSTALL.md) and [`USAGE.md`](USAGE.md) for the full
walkthrough.

## Engagement flow

```
                ┌─────────────┐
                │  /surface   │  ── seed scope + asset inventory
                └──────┬──────┘
                       ▼
                ┌─────────────┐
                │   /recon    │  ── subfinder, httpx, gau, dorks, secrets
                └──────┬──────┘
                       ▼
                ┌─────────────┐
                │   /intel    │  ── platform/version fingerprint → CVE matrix
                └──────┬──────┘
                       ▼
                ┌─────────────┐
                │   /hunt     │  ── auto-loads relevant hunt-* skills
                └──────┬──────┘
                       ▼
                ┌─────────────┐
                │   /chain    │  ── compose multi-vuln chains where needed
                └──────┬──────┘
                       ▼
                ┌─────────────┐
                │  /validate  │  ── 7-question gate → KILL / DOWN / CHAIN / SHIP
                └──────┬──────┘
                       ▼
                ┌─────────────┐
                │   /report   │  ── platform template + redacted evidence
                └─────────────┘
```

## Scope philosophy

CBH treats scope as a hard constraint, not a suggestion. Every skill that
performs active probing first defers to `scope-discipline`, which reads
`scope.md` in the engagement folder and refuses to emit payloads for
out-of-scope hosts. Bug bounty triage cost is real — see
[`docs/disclosed-reports/`](docs/disclosed-reports/) for examples of how
out-of-scope submissions damage researcher reputation.

## Engagement scaffold

`/hunt target=<host>` creates:

```
engagements/<host>-<date>/
├── scope.md           # accepted impact, in/out scope, never-submit list
├── recon-notes.md     # subdomains, tech stack, version fingerprints
├── chains.md          # multi-vuln chain working notes
├── findings/          # one .md per validated finding
└── evidence/          # redacted HARs, screenshots (unauth → auth sequence)
```

## License & responsible use

CBH is for **authorized** offensive security work only — bug bounty
programs you are enrolled in, pentests you are contracted for, or
internal red-team engagements with written authorization. See
[`SECURITY.md`](SECURITY.md) for responsible disclosure of issues in CBH
itself.

## Credits

Pattern corpus distilled from 681 disclosed HackerOne reports, the
Bugcrowd VRT, Synack VR taxonomy, OWASP WSTG, PortSwigger Web Security
Academy, and the disclosed CVE record for the platforms covered. See
[`docs/credits.md`](docs/credits.md).
