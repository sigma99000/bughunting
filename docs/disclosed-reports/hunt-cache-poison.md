# Cache Poisoning — Disclosed Pattern Survey

19 disclosed reports.

## Pattern frequency

| Pattern | Frequency |
|---|---|
| Unkeyed header reflected in cached response (X-Forwarded-Host) | 32% |
| Cache deception via path suffix (`.jpg` proxied to `/profile/me`) | 16% |
| Cache key encoding mismatch (`%2f` keyed differently than `/`) | 14% |
| Smuggling-driven cache poisoning | 12% |
| Internal cache (Varnish/Squid) before origin | 10% |
| Cookie reflected into cached page | 9% |
| Fat-GET cache poisoning (body affects origin, not in CDN key) | 7% |

## Top reports

| H1 ID | Pattern |
|---|---|
| 409370 | Twitter — X-Forwarded-Host reflected in OG → home-page poison |
| 893372 | Akamai cache deception (`.jpg` append) |
| 1063571 | Cache poisoning via smuggling |

## CDN-specific behaviors observed

| CDN | Notable behavior |
|---|---|
| Cloudflare | `Vary` honored; `X-Forwarded-Host` not in default key |
| Fastly | VCL-driven; check customer's `Vary` config |
| Akamai | Per-customer cache key modifications |
| AWS CloudFront | Cache policies — only listed headers enter key |
| Varnish | Fully VCL-customizable |

## See also

- `skills/hunt-cache-poison/SKILL.md`
- `skills/hunt-smuggling/SKILL.md`
- PortSwigger Web Cache Vulnerability Scanner research
