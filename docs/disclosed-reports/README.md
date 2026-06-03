# Disclosed Reports — Index

This folder aggregates patterns distilled from 681 disclosed
HackerOne reports, grouped by vulnerability class. Each file
references the H1 report by ID and summarizes the attack
pattern for skill-authorship use.

## File index

| File | Class | Reports surveyed |
|---|---|---|
| `hunt-xss.md` | XSS | 87 |
| `hunt-sqli.md` | SQL injection | 39 |
| `hunt-ssrf.md` | SSRF | 56 |
| `hunt-oauth.md` | OAuth | 41 |
| `hunt-saml.md` | SAML | 18 |
| `hunt-jwt.md` | JWT | 22 |
| `hunt-idor.md` | IDOR | 78 |
| `hunt-graphql.md` | GraphQL | 31 |
| `hunt-rce.md` | RCE / chains | 64 |
| `hunt-deserialization.md` | Deserialization | 26 |
| `hunt-file-upload.md` | File upload | 49 |
| `hunt-redirect.md` | Open redirect (in chains) | 35 |
| `hunt-cache-poison.md` | Cache poisoning | 19 |
| `hunt-smuggling.md` | HTTP smuggling | 14 |
| `chains.md` | Multi-vuln chains | 102 |

Total: 681 reports.

## Methodology

For each class:

1. Search hacktivity for the keyword + close-as-resolved filter.
2. Filter by disclosure date (≥ 2018 for pattern relevance).
3. Tag each report with: severity, root cause, bypass technique,
   chain components.
4. Aggregate into the per-class file.
5. Cross-reference into the SKILL.md "Disclosed-report patterns"
   tables.

## How to use

- These files are **input** to skill bodies, not duplicates. The
  SKILL.md tables select the most pedagogically useful subset.
- Refer back here when you need full pattern coverage for a class.
- New reports: PR against the class file with the H1 ID and the
  one-line pattern summary; the maintainer decides whether to
  also surface in SKILL.md.

## See also

- `docs/credits.md` — source acknowledgments
- `CONTRIBUTING.md` — how to add a new pattern
