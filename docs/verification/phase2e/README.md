# Phase 2e — JWT + GraphQL + Race Lab

## What this exercises

- `hunt-jwt` — HS/RS confusion, kid injection
- `hunt-graphql` — alias batching
- `hunt-race` — single-packet attack on a coupon-redemption mutation

## Components

A Flask app with:

- `/login` issues a JWT signed RS256
- `/.well-known/jwks.json` exposes the RSA public key
- `/graphql` accepts `redeemCoupon(code: String)` mutation
- The mutation is NOT idempotent — race window exists
- JWT verification incorrectly uses `verify=False` on RS256 path

## Files

- `app.py` — Flask app (~120 lines)
- `requirements.txt` — flask, pyjwt, graphene
- `Makefile` — `make up`, `make down`
- `exploits/jwt-confusion.sh` — RS→HS confusion PoC
- `exploits/alias-batch.sh` — coupon race
- `exploits/single-packet.py` — turbo-intruder-style race

## Lab quirks (intentional)

- The "coupon redemption" decrements counter in a SQLite write
  WITHOUT `BEGIN IMMEDIATE` — race window ~50ms wide
- `jwt.decode()` is called with `algorithms=['HS256','RS256']` and
  HS256 falls back to using the loaded public-key PEM as secret

## Walk-through (high level)

1. Get a low-priv JWT via `/login`
2. Fetch public key from `/.well-known/jwks.json`
3. Forge admin JWT signed HS256 with the pubkey
4. Submit a single coupon code via `redeemCoupon` — 1 credit
5. Submit the same code via 20-aliased GraphQL mutation in a single
   single-packet request — observe 17 credits

## See also

- `skills/hunt-jwt/SKILL.md`
- `skills/hunt-graphql/SKILL.md`
- `skills/hunt-race/SKILL.md`
