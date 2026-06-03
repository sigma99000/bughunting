# Phase 2f — SSTI + OAuth + File Upload Lab

## What this exercises

- `hunt-ssti` — Jinja2 SSTI in email template
- `hunt-oauth` — redirect_uri allow-list bypass via subdomain trust
- `hunt-file-upload` — image-handler RCE via embedded SSTI

## Components

A Flask app with:

- OAuth-like flow at `/auth/authorize` — `redirect_uri` allow-list
  matches `endswith('.lab.local')`
- Email-preview endpoint at `/notify/email/preview` renders user
  input through Jinja2 with default-unsafe `Environment(autoescape=False)`
- Avatar upload at `/profile/avatar` accepts SVG and reflects via
  data URI in subsequent profile views

## Files

- `app.py` (~150 lines)
- `requirements.txt`
- `Makefile`
- `exploits/ssti-config-read.sh` — Jinja2 to read SECRET_KEY
- `exploits/oauth-redirect-bypass.sh` — `.lab.local` suffix bypass
- `exploits/svg-stored-xss.svg` — minimal SVG with onload

## Walk-through

1. Trigger SSTI to read OAuth `client_secret` from app config
2. Discover `redirect_uri` suffix `.lab.local` is matched too loosely
3. Register `attacker.lab.local` (lab DNS resolves to attacker)
4. Run full OAuth ATO chain
5. Bonus: upload SVG with stored XSS to corroborate as second
   chain to ATO

## See also

- `skills/hunt-ssti/SKILL.md`
- `skills/hunt-oauth/SKILL.md`
- `skills/hunt-file-upload/SKILL.md`
- `docs/disclosed-reports/chains.md` — chain archetype #6
