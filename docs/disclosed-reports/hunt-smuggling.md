# HTTP Smuggling — Disclosed Pattern Survey

14 disclosed reports + research corpus.

## Variant frequency

| Variant | Frequency |
|---|---|
| HTTP/2 downgrade (H2.CL / H2.TE) | 36% |
| Classic CL.TE | 21% |
| Classic TE.CL | 14% |
| TE.TE (parser obfuscation) | 14% |
| H2C smuggling | 9% |
| Response queue poisoning | 6% |

## Top reports & research

| Source | Pattern |
|---|---|
| H1 #498052 (Slack) | CL.TE via load balancer |
| H1 #737140 (Twitter) | TE.TE via header obfuscation |
| H1 #1063571 | H2 downgrade + cache poisoning |
| CVE-2021-22965 (BIG-IP) | h2c smuggling |
| CVE-2023-25690 (Apache mod_proxy) | Smuggling via RewriteRule |
| CVE-2024-27316 (Apache HTTP/2 CONTINUATION DoS) | DoS-only |
| PortSwigger 2023 research | Single-packet attack; response queue poisoning |

## Impact patterns

| Pattern | How |
|---|---|
| Cross-user request stealing | Response-queue poisoning — most-impactful variant |
| Auth bypass | Smuggle to path that frontend rejects, backend accepts |
| Cache poisoning | Smuggled response cached for legitimate URL |
| Internal SSRF | Smuggled headers reach backend (`X-Forwarded-Host`) |
| Stored XSS via victim's request | Smuggle a POST that triggers stored XSS with victim as poster |

## See also

- `skills/hunt-smuggling/SKILL.md`
- `skills/hunt-cache-poison/SKILL.md`
- `docs/verification/phase2h/` — local Docker lab for CL.TE reproduction
- PortSwigger HTTP request smuggling research series
