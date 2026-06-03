# Wayback Strategy

## Time-diff for endpoint discovery

The Wayback Machine preserves historical responses. Useful when:

- Production endpoint hardened — old responses show pre-hardening shape
- Endpoint removed but still exists at the same path
- Old API responses include now-removed fields

## Tools

```bash
gau <domain> > endpoints.txt
waybackurls <domain> >> endpoints.txt
```

## Specific patterns

```bash
# All historical endpoints with a juicy param
cat endpoints.txt | grep -E '(\?|&)(redirect|url|return|token|api_key)=' | sort -u

# Old admin paths now removed (404 today but worth probing)
cat endpoints.txt | grep -E '/(admin|console|debug)' | sort -u

# Files that may still exist
cat endpoints.txt | grep -E '\.(bak|old|tmp|swp|sql|env|zip)' | sort -u
```

## Re-fetch the cache

```bash
# Get historical snapshot
curl -s "http://archive.org/wayback/available?url=https://target/old-path"
# Then fetch the snapshot URL it returns
```

## Diff old vs new

For each old endpoint that still 200's today:

```bash
diff <(curl -s https://target/old-path) <(curl -s "https://web.archive.org/web/<timestamp>/https://target/old-path")
```

Differences are interesting — sometimes show fields removed from
modern response but still present in DB queries.

## Common finds in Wayback

- Forgotten API v1 endpoints still serving (after v2 migration)
- Old admin paths now firewalled at edge but reachable internally
  (combine with SSRF)
- Internal hostnames in JSON responses pre-redaction
- Stack traces in old error pages

## See also

- `dork-corpus.md`
- `recon-stack.md`
