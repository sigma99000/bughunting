# Recon Stack (Reference)

Companion to the `recon-stack` skill. Tool catalog with install +
one-line invocations.

## Subdomain
- `subfinder -d <d> -all -recursive -silent`
- `assetfinder --subs-only <d>`
- `amass enum -passive -d <d> -silent`
- `findomain -t <d>`
- `chaos-client -d <d>` (entitled)
- `crt.sh` JSON query
- `dnsx -l subs.txt -resp -resp-only` (resolve only the live)

## DNS
- `dnsx`, `puredns`, `massdns`
- `dnsrecon -d <d>` (zone-transfer attempt)

## HTTP probe
- `httpx -tech-detect -title -status-code -ip -favicon`
- `httprobe`
- `gowitness file -f live.txt` (screenshot grid)
- `aquatone` (alternative screenshotter)

## Endpoints
- `gau`, `waybackurls`, `katana`
- `hakrawler -url <url> -depth 3`
- `linkfinder.py -i bundle.js -o cli` (JS endpoint mining)

## Fuzzing
- `ffuf -u .../FUZZ -w wl.txt -mc all -fc 404`
- `feroxbuster -u <url> -w wl.txt`
- `gobuster dir|dns|vhost`

## Vuln scanning
- `nuclei -t cves/ -t exposures/`
- `nuclei -tags takeover`
- `bbot -t <d> -f cloud-enum,subdomain-enum,web-basic`

## Wordlists
- SecLists (`/usr/share/wordlists/seclists/`)
- assetnote `commonspeak2-wordlists`
- `1ndianl33t/Pentest_Wordlist`

## Cloud
- `cloud_enum`
- `s3scanner`
- `gcpbucketbrute`
- `azurehound` (post-cred)

## Mobile
- `apktool d app.apk`
- `jadx-gui` for decompiled Java
- `class-dump`, `r2`, `frida` for iOS

## Discipline

All tools should be run with rate-limit flags (`-rate-limit`, `-t`).
Passive sources only when the program disallows active scans.
