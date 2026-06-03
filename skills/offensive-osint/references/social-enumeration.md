# Social Enumeration

## What's OK

- Identifying that an employee exists publicly (LinkedIn search
  result) for scope-mapping purposes
- Cross-referencing public conference talks
- Reading public GitHub profile bios

## What's not OK

- Pretending to be a colleague to chat with employees
- Targeted harassment / phishing of named individuals
- Creating fake accounts to friend / follow employees
- Sending DM with payload to specific employees without
  engagement authorization (this is a *social engineering*
  engagement, which is a separate SOW)

## Hard guardrails

CBH refuses to:

- Generate phishing email templates targeting a named person
- Draft pretexting scripts unless `scope.md` explicitly authorizes
  social engineering
- Output anything that looks like an OSINT dossier on a single
  person (`alice@example.com works at Acme, last attended X
  conference, posts on Reddit as Y, runs in Z park at 7am on
  Strava…`)

Operators who need this should:

1. Confirm the engagement covers SE in writing.
2. Use a dedicated SE platform (Gophish, etc.) — not CBH.
3. Operate under their firm's SE methodology, not ad-hoc.

## What CBH does help with

- Identifying the **categories** of employees with elevated risk
  (e.g., "the program's CISO blog mentions they use Okta — that's
  a config signal")
- Identifying the **org chart depth** for blast-radius scoping —
  no names needed

## See also

- `redteam-mindset` (rule 10: preserve attribution; rule 1 doesn't
  include "social engineering" as a default attack path)
- `payload-discipline`
