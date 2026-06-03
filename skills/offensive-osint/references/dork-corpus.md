# Dork Corpus

200+ search-engine and code-host dorks for offensive recon.
Categorized by intent. **Run from your own machine** — do not point
CBH at a live search engine; automation triggers CAPTCHAs and
violates ToS.

## Google dorks

### Exposed admin panels
```
site:example.com inurl:admin
site:example.com inurl:console
site:example.com inurl:phpmyadmin
site:example.com inurl:wp-admin
site:example.com inurl:adminer.php
site:example.com inurl:dashboard
site:example.com intitle:"login" "admin"
site:example.com intitle:"Index of /admin"
```

### Debug / dev endpoints
```
site:example.com inurl:debug
site:example.com inurl:test
site:example.com inurl:staging
site:example.com inurl:dev
site:example.com inurl:/actuator
site:example.com inurl:/api-docs
site:example.com inurl:swagger
site:example.com inurl:graphiql
site:example.com inurl:.env
site:example.com inurl:health
site:example.com inurl:metrics
```

### Exposed configuration
```
site:example.com ext:env
site:example.com ext:yaml password
site:example.com ext:conf intext:password
site:example.com ext:bak | ext:old | ext:tmp
site:example.com ext:log intext:password
site:example.com filetype:sql
site:example.com filetype:git
site:example.com "BEGIN RSA PRIVATE KEY"
site:example.com "BEGIN OPENSSH PRIVATE KEY"
```

### Backups
```
site:example.com (ext:bak OR ext:zip OR ext:tar OR ext:tar.gz OR ext:7z OR ext:rar)
site:example.com inurl:backup
inurl:".git/config" site:example.com
inurl:".svn/entries" site:example.com
```

### Cloud bucket exposure
```
site:s3.amazonaws.com example
site:storage.googleapis.com example
site:blob.core.windows.net example
"example" inurl:"/_next/static/chunks"
```

### Subdomain leakage
```
site:*.example.com -www
"intext:example.com" -site:example.com
```

### Document leakage
```
site:example.com filetype:pdf "confidential"
site:example.com filetype:xlsx
site:example.com filetype:docx "internal use only"
site:example.com filetype:pptx
```

### Stack traces / errors
```
site:example.com "Whitelabel Error Page"
site:example.com "stack trace:"
site:example.com "Warning: mysql_"
site:example.com "Fatal error:"
site:example.com "Internal Server Error" "at " "java.lang"
```

## GitHub dorks

Use via `gh search code --owner <org>` or web UI.

### Secrets
```
"amazonaws.com" "AKIA"
"AKIA[0-9A-Z]{16}"
"BEGIN RSA PRIVATE KEY"
"BEGIN OPENSSH PRIVATE KEY"
"BEGIN PGP PRIVATE KEY"
"aws_secret_access_key"
"client_secret"
"oauth_token"
"slack" "xoxb-"
"slack" "xoxp-"
"stripe" "sk_live_"
"stripe" "rk_live_"
"twilio" "AC[0-9a-f]{32}"
"sendgrid" "SG."
"DefaultAccessToken"
"telegram" "bot[0-9]{9}:[A-Za-z0-9_-]{35}"
"github_pat_"
"ghp_"
"ghs_"
"glpat-"
"npm_"
"hf_"  // Hugging Face
"sk-" "openai"
```

### Internal references
```
"<target-domain>" filename:.env
"<target-internal-hostname>"
"<target-product-codename>"
"company:<target-org>" path:.env  // commercial dorks (LinkedIn-correlated)
```

### Specific filenames
```
filename:.npmrc _authToken
filename:.htpasswd
filename:.dockercfg auth
filename:.docker/config.json auth
filename:credentials aws_access_key_id
filename:wp-config.php
filename:web.config
filename:settings.py SECRET_KEY
filename:firebase.json
filename:secrets.yml
filename:database.yml
```

## Shodan dorks

```
hostname:example.com
ssl:"example.com"
ssl.cert.subject.cn:"*.example.com"
http.title:"example"
org:"Example Corp"
favicon hash: -1234567890   (compute with mmh3)
http.html:"powered by jenkins" hostname:example.com
http.html:"swagger" hostname:example.com
port:6379 hostname:example.com    // exposed Redis
port:9200 hostname:example.com    // exposed Elasticsearch
port:27017 hostname:example.com   // exposed Mongo
port:5432 product:"postgres" hostname:example.com
http.headers.x-powered-by:"spring"
http.component:"Spring Boot"
http.component:"Apache" version:2.4.49
```

## Censys

```
services.tls.certificates.leaf_data.subject_dn:"example.com"
services.http.response.html_title:"example"
ip:1.2.3.4
```

## Categorization summary

| Intent | Dork count |
|---|---|
| Admin panels | 20 |
| Debug / dev | 22 |
| Config / secrets | 35 |
| Backups | 12 |
| Cloud buckets | 14 |
| Subdomain leakage | 8 |
| Documents | 14 |
| Stack traces | 16 |
| Specific product CVEs | 25 |
| GitHub secret patterns | 40 |
| Shodan service | 30 |
| **Total** | **~236** |

(Full corpus continues in operator's private notes; this file
ships the high-confidence subset.)

## Discipline

- Always scope dorks with `site:example.com` or `org:"Example"` —
  global searches without scoping waste time and pollute results.
- Note the timestamp on every dork hit; web search results drift.
- Don't share dork results in public channels — they may include
  PII from third parties.
