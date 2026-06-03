# Contributing

Claude Bug Hunter is a **knowledge artifact**, not software. Contributions
are PRs that add or sharpen offensive-security expertise, not feature
patches.

## What we accept

| Category | Example PR |
|----------|-----------|
| New disclosed-report pattern | Add a 2023 H1 report on `hunt-graphql` with the exact bypass payload |
| New CVE entry | Add a Fortinet pre-auth SSRF CVE to `enterprise-vpn-attack/cve-index.json` |
| New chain template | Add a SSTI + OAuth + file-upload chain to `docs/verification/phase2f` |
| Sharpen a payload table | Replace a generic XSS payload with the actual one from H1 report 1234567 |
| New skill | A 39th hunt skill for an underrepresented class (e.g., `hunt-dependency-confusion`) |

## What we reject

- Theoretical payloads without a disclosed-report or CVE source
- Skills that exceed scope (e.g., physical pentest, social engineering toolkits)
- Anything that targets specific organizations not authorized for public discussion
- Re-publishing private bounty reports — only public-disclosure references

## Skill authorship format

Each `SKILL.md` follows this structure:

```markdown
---
name: hunt-<class>
description: <one-line trigger description>
keywords: [<comma-separated terms that auto-load this skill>]
---

# hunt-<class>

## When this skill loads
<list of keywords / contexts>

## Phase 1 — <discovery step>
<payload table | bypass matrix>

## Phase 2 — <validation step>
<curl / Burp commands>

## Phase 3 — <chaining>
<links to other skills>

## Disclosed-report patterns
| H1 / CVE | Year | Pattern |
|----------|------|---------|

## Never-submit fallbacks
<self-XSS / theoretical only / etc.>

## See also
<links to related skills>
```

## Style rules

- **No hedging.** "May be vulnerable" → "Vulnerable if X; not vulnerable
  if Y. Test with Z."
- **Disclosed-report citation required** for every claim.
- **Payloads in code fences with language tag** for syntax highlight.
- **No emojis** in skill bodies (skill metadata is OK).
- **Tables over prose** for matrices.
- **One file per skill.** No splitting across includes (only
  `offensive-osint` has a `references/` subfolder; that's an exception).

## Adding a slash command

1. Create `commands/<name>.md` with YAML frontmatter (`name`,
   `description`).
2. Body must be Claude-readable — describe the workflow, expected args,
   and skills to load.
3. Update [`USAGE.md`](USAGE.md) reference table.

## Testing a skill

Skills don't have unit tests, but every new pattern must come with a
**verification recipe**: either a public PoC URL (preferred) or a
self-contained Flask/Docker lab in `docs/verification/`.

## Review bar

- Two maintainer approvals for new skills
- One approval for additive patches to an existing skill
- All disclosed-report cites must resolve to a public URL or a verifiable CVE
