---
name: hunt-auth
description: Authentication flaws — credential stuffing, weak password reset, 2FA bypass, session fixation, JWT (see hunt-jwt).
keywords: [auth, authentication, credential stuffing, password reset, 2fa, mfa, session, login]
---

# hunt-auth

## Triggers

"auth bypass", "login", "credential stuffing", "password reset",
"2fa bypass", "mfa bypass", "session fixation".

## Phase 1 — login surface

Test:

| Vector | Test |
|---|---|
| User enum via login | Compare timing & error text on existing vs non-existent users |
| User enum via password reset | Same |
| User enum via signup ("email already taken" message) | Same |
| Rate-limit bypass | Vary `X-Forwarded-For` per request; GraphQL alias-batching |
| Username injection | NULL byte, case insensitivity (`Admin` vs `admin`), homoglyph |
| Login-with-Google + no `hd=` enforcement | login with random gmail = unbounded signup |

## Phase 2 — password reset

| Issue | Test |
|---|---|
| Token brute-forceable (short / numeric) | Enumerate the space |
| Token reused after first use | Multi-use breaks single-pwd policy |
| Token bound to email but email-change endpoint exists | Change email post-token, reset victim's |
| Reset link in `Referer` header | Visit external link from reset page — leaks via referer |
| `Host` header reflected in reset URL | `Host: attacker.com` → reset email contains attacker URL → token capture |
| Old token after password change | Should invalidate |
| Reset from POST without re-auth | Attacker session can change password |

## Phase 3 — 2FA / MFA bypass

| Issue | Test |
|---|---|
| 2FA optional after login | Skip the 2FA step's URL — go straight to dashboard |
| 2FA endpoint not bound to current login attempt | Submit attacker's 2FA code with victim's userId |
| 2FA brute-force (no rate limit) | Try all 10000 6-digit codes within validity window |
| 2FA race | (see `hunt-race`) — submit valid+invalid codes in parallel |
| 2FA "Trust this device" bypass | Cookie `device_trusted=true` accepted from client |
| Recovery code reuse | Should single-use |
| Backup phone number | Self-add an attacker phone, request reset via SMS |
| 2FA via SMS only | SIM-swap is out of scope for most bug bounty but note |
| WebAuthn fallback to password | Downgrade attack — provide password instead of FIDO |

## Phase 4 — session

| Issue | Test |
|---|---|
| Cookie not invalidated on logout | Reuse old cookie |
| Cookie not rotated on password change | Old session lives |
| Cookie not bound to IP/UA (when claimed to be) | Use from different IP |
| Session fixation | Pre-set cookie, victim logs in, attacker reuses cookie |
| Concurrent session count | If "1 session" advertised but multiple allowed → policy bypass |
| Session timeout enforcement | Server-side vs client-side |

## Phase 5 — credential stuffing posture (research only)

Never use real breached credentials against a target without
explicit authorization. CBH **refuses** to spray imported credential
lists unless `scope.md` explicitly permits.

For research, look at the target's posture:

- Generic `Invalid username or password` vs specific `User not found` → enum on
- CAPTCHA after N attempts → measure N
- IP-based vs account-based lockout
- HIBP-style breach-check on signup? Bonus points

## Disclosed-report patterns

| Source | Pattern |
|---|---|
| H1 #1098438 (Shopify) | 2FA OTP race |
| H1 #157953 | Reset token bound to email but email change unprotected |
| H1 #281572 | Session fixation via OAuth state |
| H1 #946325 | Host header reflection in password reset URL |
| CVE-2024-21413 (Outlook) | NTLM-leak via "moniker" link — auth context theft |

## Never-submit fallbacks

- "Login allows weak passwords (`123456`)" → DOWNGRADE/KILL
- Username enum alone without ATO chain → KILL on most programs
- "Rate-limit absent" without successful brute force → KILL

## See also

- `hunt-oauth`, `hunt-jwt`, `hunt-saml`, `hunt-race`
- `m365-entra-attack`, `okta-attack`
