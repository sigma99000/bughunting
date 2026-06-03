# Secret Patterns

80+ regex patterns for hardcoded secrets, with entropy thresholds.
Used by `scripts/secret_scan.py` and inline by `/token-scan`.

## Format

Each pattern row:

| Class | Regex | Entropy ≥ | Notes |

`Entropy ≥` is Shannon entropy of the matched value (bits per char).
Matches below threshold are noise (e.g., example strings in docs).

## Cloud — AWS

| Class | Regex | Entropy ≥ | Notes |
|---|---|---|---|
| AWS Access Key ID | `AKIA[0-9A-Z]{16}` | 3.5 | IAM long-term key |
| AWS Temp Access Key ID | `ASIA[0-9A-Z]{16}` | 3.5 | STS / SSO temp key |
| AWS Secret Access Key | `(?i)aws.{0,20}?(?:secret|key).{0,20}?['"]([A-Za-z0-9/+=]{40})['"]` | 4.5 | |
| AWS Session Token | `(?:AQoDYXdzEPT//[A-Za-z0-9/+=]{100,})` | 5.0 | |
| AWS Account ID (12 digits) | `\b\d{12}\b` near `aws` | -- | Not secret per se, but leak-correlation |

## Cloud — GCP

| GCP API Key | `AIza[0-9A-Za-z\-_]{35}` | 4.0 | Browser/Server keys both |
| GCP OAuth Client Secret | `[0-9]{12}-[a-z0-9]{32}\.apps\.googleusercontent\.com` paired with `GOCSPX-[a-zA-Z0-9_-]{28}` | 4.5 | |
| GCP Service Account JSON | `"type":\s*"service_account".*"private_key_id"` | -- | Multi-line JSON |
| Firebase Cloud Messaging Server Key | `AAAA[A-Za-z0-9_-]{7}:[A-Za-z0-9_-]{140}` | 4.5 | |

## Cloud — Azure

| Azure Storage Key | `[A-Za-z0-9+/=]{88}` near `accountkey=` | 5.0 | |
| Azure Storage SAS | `\?sv=\d{4}-\d{2}-\d{2}&[^"]*sig=` | -- | URL-embedded |
| Azure AD App Client Secret | `[A-Za-z0-9~_.\-]{34,40}` near `client_secret` | 4.0 | |

## Stripe

| Stripe Live Secret | `sk_live_[0-9a-zA-Z]{24,99}` | 4.5 | High-value: always validate |
| Stripe Test Secret | `sk_test_[0-9a-zA-Z]{24,99}` | 4.5 | Less impact but reportable |
| Stripe Restricted Key | `rk_live_[0-9a-zA-Z]{24,99}` | 4.5 | Scope-limited but still useful |
| Stripe Publishable | `pk_live_[0-9a-zA-Z]{24,99}` | 3.5 | Public key — usually not a finding |

## Twilio

| Twilio Account SID | `AC[a-f0-9]{32}` | 3.5 | Public-ish |
| Twilio Auth Token | `[a-f0-9]{32}` near `twilio` | 4.0 | Pair with SID |
| Twilio API Key SID | `SK[a-f0-9]{32}` | 3.5 | |

## SendGrid

| SendGrid API Key | `SG\.[A-Za-z0-9_-]{22}\.[A-Za-z0-9_-]{43}` | 4.5 | |

## Slack

| Slack Bot Token | `xoxb-[0-9]{10,12}-[0-9]{10,13}-[A-Za-z0-9]{24,34}` | 4.0 | |
| Slack User Token | `xoxp-[0-9]{10,12}-[0-9]{10,13}-[0-9]{10,13}-[a-f0-9]{32}` | 4.0 | |
| Slack Workspace Token | `xoxa-[0-9]+-[A-Za-z0-9-]+` | 4.0 | |
| Slack Webhook | `https://hooks\.slack\.com/services/T[A-Z0-9]+/B[A-Z0-9]+/[A-Za-z0-9]{24}` | -- | URL form |
| Slack Refresh Token | `xoxe-[0-9]+-[A-Za-z0-9-]+` | 4.0 | |

## GitHub

| GitHub PAT (classic) | `ghp_[A-Za-z0-9]{36}` | 4.5 | |
| GitHub PAT (fine-grained) | `github_pat_[A-Za-z0-9_]{82}` | 4.5 | |
| GitHub OAuth | `gho_[A-Za-z0-9]{36}` | 4.5 | |
| GitHub App | `(ghu|ghs)_[A-Za-z0-9]{36}` | 4.5 | |
| GitHub Refresh | `ghr_[A-Za-z0-9]{36}` | 4.5 | |

## GitLab

| GitLab PAT | `glpat-[A-Za-z0-9_-]{20}` | 4.0 | |
| GitLab Runner | `glrt-[A-Za-z0-9_-]{20}` | 4.0 | |
| GitLab Deploy Token | `gldt-[A-Za-z0-9_-]{20}` | 4.0 | |

## Bitbucket

| Bitbucket App Password | `ATBB[A-F0-9]{32}` | 3.5 | |

## NPM / package registries

| NPM Token | `npm_[A-Za-z0-9]{36}` | 4.5 | |

## Docker

| Docker Hub Token | `dckr_pat_[A-Za-z0-9_-]{27,}` | 4.0 | |

## Hugging Face

| HF Token | `hf_[A-Za-z]{34}` | 4.0 | |

## OpenAI / Anthropic

| OpenAI API Key | `sk-[A-Za-z0-9]{20,}` | 4.0 | Includes project-scoped variants |
| OpenAI Project Key | `sk-proj-[A-Za-z0-9_-]{40,}` | 4.5 | |
| Anthropic API Key | `sk-ant-api03-[A-Za-z0-9_-]{93}-[A-Za-z0-9_-]{3}AA` | 4.5 | |
| Google AI Studio | `AIza[A-Za-z0-9_-]{35}` | 4.0 | (same shape as GCP key) |

## Other SaaS

| Mailgun Private | `key-[a-f0-9]{32}` | 3.5 | |
| Mailgun Public | `pubkey-[a-f0-9]{32}` | 3.5 | (less sensitive) |
| Mailchimp | `[a-f0-9]{32}-us[0-9]+` | 4.0 | |
| Postmark | `[A-Za-z0-9]{36}` near `postmark` | 4.0 | |
| Algolia Admin | `[a-f0-9]{32}` near `algolia.*admin` | 4.0 | |
| Datadog API | `[a-f0-9]{32}` near `datadog` | 4.0 | |
| Datadog APP | `[a-f0-9]{40}` near `datadog` | 4.0 | |
| New Relic User | `NRAK-[A-Z0-9]{27}` | 4.0 | |
| New Relic License | `[a-f0-9]{40}NRAL` | 4.0 | |
| Linear | `lin_api_[A-Za-z0-9]{40}` | 4.5 | |
| Notion Internal | `secret_[A-Za-z0-9]{43}` | 4.5 | |
| Asana | `[0-9]/[0-9a-f]{32}` near `asana` | 4.0 | |
| Atlassian API | `ATATT3xFfGF0[A-Za-z0-9_-]{180}=[A-Za-z0-9]{8}` | 4.5 | |
| Square | `sq0(c|i)sp-[A-Za-z0-9_-]{43}` | 4.5 | |
| Square Access | `EAAA[A-Za-z0-9_-]{60}` | 4.5 | |
| PayPal Braintree | `access_token\$production\$[0-9a-z]{16}\$[0-9a-f]{32}` | 4.5 | |
| Heroku | `[a-f0-9]{8}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{12}` near `heroku` | 4.0 | (UUID shape) |
| Cloudflare API Token | `[A-Za-z0-9_-]{40}` near `cloudflare` + `Bearer` | 4.5 | |
| Cloudflare Global API Key | `[a-f0-9]{37}` near `cloudflare` | 4.0 | |
| DigitalOcean PAT | `dop_v1_[a-f0-9]{64}` | 4.5 | |
| Linode | `[a-f0-9]{64}` near `linode` | 4.5 | |
| Vultr | `[A-Z0-9]{36}` near `vultr` | 4.0 | |
| Doppler | `dp\.pt\.[A-Za-z0-9]{43}` | 4.5 | |
| Vault | `hvs\.[A-Za-z0-9_-]{90,}` | 4.5 | |
| Pulumi | `pul-[a-f0-9]{40}` | 4.5 | |
| Sentry DSN | `https://[a-f0-9]{32}@[a-z0-9.]+\.ingest\.sentry\.io/[0-9]+` | -- | URL form |
| Rollbar Server | `[a-f0-9]{32}` near `rollbar.*server` | 4.0 | |
| Bugsnag | `[a-f0-9]{32}` near `bugsnag` | 4.0 | |
| Mapbox | `pk\.eyJ[A-Za-z0-9_-]+\.[A-Za-z0-9_-]+` | 4.5 | (JWT-shaped) |
| Google Maps Key | `AIza[A-Za-z0-9_-]{35}` near `maps` | 4.0 | (same shape) |
| Telegram Bot | `[0-9]{8,10}:[A-Za-z0-9_-]{35}` | 4.5 | |
| Discord Bot | `[MN][A-Za-z0-9]{23}\.[\w-]{6}\.[\w-]{27}` | 4.5 | |
| Discord Webhook | `https://discord(?:app)?\.com/api/webhooks/[0-9]+/[A-Za-z0-9_-]+` | -- | URL form |

## Generic / private keys

| RSA Private Key | `-----BEGIN RSA PRIVATE KEY-----` | -- | Block match |
| OpenSSH Private Key | `-----BEGIN OPENSSH PRIVATE KEY-----` | -- | |
| EC Private Key | `-----BEGIN EC PRIVATE KEY-----` | -- | |
| PGP Private Key | `-----BEGIN PGP PRIVATE KEY BLOCK-----` | -- | |
| DSA Private Key | `-----BEGIN DSA PRIVATE KEY-----` | -- | |
| Generic API Key | `(?i)(api[_-]?key|apikey|api_secret|access[_-]?token)[\s:='"]+([A-Za-z0-9_/+=-]{20,})` | 4.0 | Lots of FP without entropy check |
| Generic Password Assignment | `(?i)password\s*=\s*['"]([^'"]{8,})['"]` | 3.5 | Lots of FP |
| Generic JWT | `eyJ[A-Za-z0-9_-]+\.eyJ[A-Za-z0-9_-]+\.[A-Za-z0-9_-]{10,}` | -- | Decode + check claims |

## Database connection strings

| Postgres | `postgres(?:ql)?://[^:]+:[^@]+@[^/]+/\w+` | -- | Embedded creds |
| MySQL | `mysql://[^:]+:[^@]+@[^/]+/\w+` | -- | |
| MongoDB | `mongodb(?:\+srv)?://[^:]+:[^@]+@[^/]+` | -- | |
| Redis | `redis://[^:]*:[^@]+@[^/]+` | -- | |
| RabbitMQ | `amqp://[^:]+:[^@]+@[^/]+` | -- | |
| Generic JDBC | `jdbc:[a-z]+://[^?]+\?password=` | -- | |

## How it's used by `secret_scan.py`

```
for line in file:
    for class, regex in patterns:
        for m in regex.findall(line):
            if entropy(m) >= class.threshold:
                yield Hit(class, m, file, line_no)
```

## False-positive controls

- Skip matches whose 16-char context is a known dummy
  (`AKIAIOSFODNN7EXAMPLE`, `xoxb-EXAMPLE`, `sk_test_4eC39H...`)
- Skip matches inside `# noqa: secret` / `# pragma: allowlist secret`
  comments
- Skip files in `node_modules/`, `vendor/`, `.git/objects/`

## See also

- `secret-validators.md` — one-liner to confirm a found key is live
- `scripts/secret_scan.py` — the runner
