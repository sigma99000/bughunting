---
name: recon-stack
description: Tooling-focused recon — install commands and one-liners for 40+ tools.
keywords: [recon, tools, subfinder, httpx, nuclei, katana, gau, waybackurls, amass, ffuf, gobuster, gowitness]
---

# recon-stack

## When this skill loads

`/recon` invokes this for the actual tooling. `offensive-osint`
provides the corpus / strategy; `recon-stack` provides the
commands.

## Subdomain enumeration

```bash
go install github.com/projectdiscovery/subfinder/v2/cmd/subfinder@latest
subfinder -d example.com -all -recursive -silent -o subs.txt

go install github.com/tomnomnom/assetfinder@latest
assetfinder --subs-only example.com

go install github.com/owasp-amass/amass/v4/...@master
amass enum -passive -d example.com -silent

curl -s "https://crt.sh/?q=%25.example.com&output=json" | jq -r '.[].name_value' | tr ',' '\n' | sort -u
```

## Liveness + tech

```bash
go install github.com/projectdiscovery/httpx/cmd/httpx@latest
httpx -l subs.txt -ports 80,443,8080,8443,8000,3000,5000,9000 \
      -tech-detect -title -status-code -ip -tls-probe -favicon -silent -o live.txt
```

## Vulnerability scanning

```bash
go install -v github.com/projectdiscovery/nuclei/v3/cmd/nuclei@latest
nuclei -l live.txt -t exposures/ -t misconfiguration/ -t cves/ -severity critical,high
```

## Endpoint corpus

```bash
go install github.com/lc/gau/v2/cmd/gau@latest
gau --threads 5 example.com > endpoints.txt

go install github.com/tomnomnom/waybackurls@latest
waybackurls example.com >> endpoints.txt

go install github.com/projectdiscovery/katana/cmd/katana@latest
katana -u https://example.com -d 3 -jc -fs fqdn >> endpoints.txt

sort -u endpoints.txt > endpoints.dedup.txt
```

## Content discovery / fuzzing

```bash
go install github.com/ffuf/ffuf/v2@latest
ffuf -u https://example.com/FUZZ -w /usr/share/wordlists/seclists/Discovery/Web-Content/raft-large-words.txt -mc all -fc 404 -t 50

go install github.com/OJ/gobuster/v3@latest
gobuster dir -u https://example.com -w wordlist.txt -t 50
```

## Cloud asset enum

```bash
pip install cloud_enum
cloud_enum -k example -k example-prod -k example-staging
```

## Visual recon

```bash
go install github.com/sensepost/gowitness@latest
gowitness file -f live.txt
```

## JavaScript analysis

```bash
go install github.com/lc/subjs@latest    # extract JS URLs
subjs -i live.txt > js.txt

go install github.com/projectdiscovery/notify/cmd/notify@latest

pip install Mantra                       # JS secret scanning alternative
```

## Pre-emptive WAF mapping

```bash
go install github.com/EnableSecurity/wafw00f@latest
wafw00f https://example.com
```

## CDN identification

```bash
pip install ipinfo
# Or just curl -sI and inspect Server / Via / Cache headers
```

## Tooling discipline

- Rate-limit every active tool (`-rate-limit`, `-t` threads low)
- Use `-resolvers` from a trusted file to prevent DNS leak to ISP
- For programs that ban active scanning, **passive only**:
  subfinder (no -all unless paid sources), waybackurls, crt.sh
  — none of which touch the target

## See also

- `offensive-osint` — strategy
- `surface-mapping` — turn output into an in-scope inventory
- `scope-discipline` — gating
