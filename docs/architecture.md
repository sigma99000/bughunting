# Architecture

## Design philosophy

Claude Bug Hunter is a **knowledge artifact**, not software. There is
no runtime, no daemon, no database — just markdown skills and a thin
Python harness for scripted use.

The system has three load paths into Claude:

1. **Auto-loaded skills**. Claude Code scans `~/.claude/skills/*/SKILL.md`
   at startup. Each SKILL.md declares `keywords:` in frontmatter; when
   a user's prompt contains those keywords, Claude loads the body
   inline.
2. **Slash commands**. `~/.claude/commands/*.md` files become first-class
   commands (`/hunt`, `/triage`, etc.). Each command body tells Claude
   which skills to pull in and what the workflow looks like.
3. **CLI harness**. `scripts/cbh.py` mirrors a subset of the slash
   commands for use outside Claude (CI pipelines, automation, smoke
   tests).

```
┌─────────────────────────────────────────────────────────────┐
│  User                                                       │
│   │                                                         │
│   ▼                                                         │
│  Claude Code  ──reads──▶  ~/.claude/skills/<name>/SKILL.md  │
│   │                       ~/.claude/commands/<name>.md      │
│   │ (keyword match)                                         │
│   ▼                                                         │
│  Loaded skill context                                       │
│   │                                                         │
│   ▼                                                         │
│  Response with payload tables, chain templates, verdicts    │
│                                                             │
│                                                             │
│  Shell                                                      │
│   │                                                         │
│   ▼                                                         │
│  cbh.py {surface, recon, classify, triage, report,          │
│          token-scan}                                        │
│   │                                                         │
│   ▼                                                         │
│  engagement/ artifacts on disk                              │
└─────────────────────────────────────────────────────────────┘
```

## Folder layout

```
claude-bughunter/
├── README.md, INSTALL.md, USAGE.md, CONTRIBUTING.md,
│   SECURITY.md, ENGAGEMENTS.md
├── skills/                    51 skill folders, each with SKILL.md
│   ├── hunt-xss/SKILL.md      (28 hunt-* skills total)
│   ├── ...
│   ├── m365-entra-attack/SKILL.md   (6 enterprise-attack skills)
│   ├── triage-validation/SKILL.md   (6 discipline skills)
│   ├── bugcrowd-reporting/SKILL.md  (6 reporting skills)
│   ├── offensive-osint/
│   │   ├── SKILL.md
│   │   ├── references/        14 reference files
│   │   └── scripts/secret_scan.py
│   ├── web3-audit/, llm-attack/, llm-ato/      (web3/llm cluster)
│   └── ...
├── commands/                  14 slash-command markdowns
│   ├── autopilot.md, chain.md, hunt.md, intel.md,
│   │   memory-gc.md, pickup.md, recon.md, remember.md,
│   │   report.md, surface.md, token-scan.md, triage.md,
│   │   validate.md, web3-audit.md
├── scripts/
│   ├── cbh.py                 CLI harness
│   ├── refresh-cve-index.py   NVD fetcher
│   ├── install.sh             symlink installer
│   └── hunt.sh                bash wrapper
├── docs/
│   ├── architecture.md        (this file)
│   ├── cbh-cli.md             CLI reference
│   ├── cve-coverage.md        CVE matrix index
│   ├── credits.md             sources / attribution
│   ├── disclosed-reports/     15 files — H1-pattern corpus
│   └── verification/          12 files — phase2e-2j labs + CVE walkthroughs
└── assets/
    ├── banner.svg, banner.png
    └── architecture-overview.svg, capability-map.svg,
        engagement-flow.svg, redteam-flow.svg
```

## How skills cross-reference

Skills explicitly cite each other in `## See also` sections. The
graph of skill dependencies looks like:

```
                triage-validation
                  ▲   ▲   ▲
                  │   │   │
hunt-* ────────────────────────── reporting-*
                  │   │   │
                  ▼   ▼   ▼
            evidence-hygiene, scope-discipline, payload-discipline
                          ▲
                          │
                offensive-osint + recon-stack + surface-mapping
```

Three skills are **always loaded** as guardrails:

- `scope-discipline` — refuses out-of-scope payloads
- `payload-discipline` — refuses destructive actions
- `triage-validation` — refuses to ship findings that fail the
  7-question gate

## Why no application runtime?

CBH is designed to be **read by Claude**, not executed. The Python
scripts exist for narrow utility — secret scanning, NVD fetching,
engagement scaffolding — none of which need a server.

Keeping it markdown means:

- Easy to audit (every claim is in plaintext)
- Easy to extend (drop a new SKILL.md)
- Easy to fork per organization (different scope rules, different
  reporting templates)
- No supply-chain surface (no npm/pip deps in the skill bodies)
- Survives Claude version changes (no API contract to break)

## Versioning

Each SKILL.md can carry a `version: <semver>` in frontmatter (most
don't, since most skills are stable). The repo as a whole tags
releases on the `main` branch.

CVE indices update independently via `refresh-cve-index.py`; they
don't trigger a release tag.
