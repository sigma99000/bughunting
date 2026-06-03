---
name: surface
description: Build initial scope + asset inventory for a new engagement. Creates engagement folder with scope.md, recon-notes.md, chains.md, findings/, evidence/.
---

# /surface

**Args:** `target=<primary-host> [program=<h1-slug|bc-slug|client>] [type=bugbounty|pentest|redteam]`

## What this command does

1. Loads skills: `scope-discipline`, `offensive-osint`, `surface-mapping`.
2. Creates `engagements/<target>-<YYYY-MM-DD>/` with the scaffold
   defined in `ENGAGEMENTS.md`.
3. Pre-fills `scope.md` with:
   - The universal never-submit list (logout CSRF, self-XSS, banner
     grab, EXIF, rate-limit-only, missing-headers-only, clickjacking
     on non-state-changing pages).
   - If `program=` resolves to a known bounty slug, fetches the public
     scope rules and seeds the in-scope / out-of-scope / accepted-impact
     sections. Otherwise leaves placeholders.
4. Performs initial asset enumeration **only on the primary host**:
   - Crawl the homepage, harvest links one hop deep.
   - Enumerate JavaScript bundles and queue them for `/token-scan`.
   - Note observable tech-stack signals (server header, framework
     fingerprints, login providers).
5. Writes a checklist into `recon-notes.md` listing the next-phase
   actions for `/recon`.

## Output contract

Claude must end its response with:

```
✅ Engagement scaffolded at engagements/<target>-<date>/
   Next: /recon target=<target>
```

## Discipline rules

- **Never** probe a host not listed in the freshly-written `scope.md`.
- If `type=redteam`, also load `redteam-mindset`.
- If `program=` looks like a real H1 slug but cannot be verified
  offline, ask the operator to paste the program's accepted-impact
  list rather than guess.
