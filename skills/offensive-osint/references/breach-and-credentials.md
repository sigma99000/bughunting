# Breach & Credentials

Index of credential / breach sources, HIBP integration, and
credential-stuffing hygiene.

## Discipline first

- **Never** spray a real customer's password against an unrelated
  service. That's account takeover with no authorization.
- For bug-bounty: use only test accounts. The program creates them
  or you create new ones — don't take over a real user "to prove
  the bug".
- For red-team: cred reuse is allowed only against scope, slow rate,
  and with rotation between attempts.

## Have I Been Pwned

Read-only breach lookup:

```bash
# Free unauthenticated rate: 1 req / 1.5s
curl -s "https://haveibeenpwned.com/api/v3/breachedaccount/$(urlenc alice@example.com)?truncateResponse=false" \
     -H "User-Agent: cbh-osint" \
     -H "hibp-api-key: $HIBP_KEY" \
     | jq '.[] | {Name, BreachDate, DataClasses}'
```

Result shape:

```json
[
  {"Name":"AcmeCorp", "BreachDate":"2023-04-15", "DataClasses":["Email addresses","Passwords (hashed)","IP addresses"]},
  {"Name":"OldForum", "BreachDate":"2014-08-02", "DataClasses":["Email addresses","Passwords (plain)"]}
]
```

If `DataClasses` includes `Passwords (plain)` or `Passwords (hashed)`,
the account is in a known-leaked credential set.

## Pwned Passwords (k-anonymity)

Check if a specific password is in breach data without revealing it:

```bash
PWD="ExamplePassword123!"
SHA1=$(echo -n "$PWD" | openssl dgst -sha1 | cut -d' ' -f2 | tr '[:lower:]' '[:upper:]')
PREFIX=${SHA1:0:5}
SUFFIX=${SHA1:5}
curl -s "https://api.pwnedpasswords.com/range/$PREFIX" | grep -i "^$SUFFIX"
```

Returns count if breached, nothing if not.

## Commercial breach indexes

Researchers commonly use:

- **DeHashed** — paid; search by email/username/IP/domain
- **IntelX** — paid; deeper index, also Telegram-leaked dumps
- **Snusbase** — paid; small but fast
- **Constella** — enterprise; legal-process-friendly
- **LeakCheck** — paid

Each requires terms-of-service agreement. CBH **does not** ship
breach data or queries — it documents the surface. You bring your
own subscription and your own ethics.

## Credential-stuffing hygiene (if authorized)

If your engagement explicitly permits credential stuffing:

```python
# Slow spray template — do not run without authorization
import time, random, requests
for cred in credentials:                   # one (email, password) per item
    r = requests.post("https://target/login", json={"email": cred[0], "password": cred[1]})
    log(r.status_code, cred[0])
    time.sleep(random.uniform(30, 60))     # 30-60s gap between attempts
    # rotate egress IP if available
```

Patterns to detect:
- `200 OK` with new cookie → match (account takeover)
- `200 OK` with "MFA required" → match minus MFA
- `429 Too Many Requests` → back off
- `403 Forbidden + captcha-required` → IP burned, rotate

## Don't bypass MFA

If a hit returns `MFA required`, **stop**. The bug-bounty value is
"hash reuse → cleartext via dump → still valid creds on this app
post-rotation policy failure". MFA-required is *not* an ATO.

For red-team where MFA bypass is in scope, route to the relevant
provider skill (`m365-entra-attack`, `okta-attack`).

## Breach data ownership

If you discover a leaked credential **for the target company** in a
public dump (not your private DeHashed query) and the program's
scope includes "credential exposure":

1. Verify the credential is still valid via login attempt — STOP
   at first success (don't enumerate).
2. Report the *source* of the leak, not just the credential. The
   leak source is the actionable finding ("Your `support@example.com`
   credential appears in the AcmeCorp 2023 breach; please rotate
   and force re-auth.").
3. Redact the credential in your report. Triagers can validate via
   their own breach DB lookup.

## See also

- `identity-fabric.md` — email → account expansion
- `redteam-mindset` — cred reuse playbook
- `hunt-auth` — auth-class findings adjacent to credential exposure
- `payload-discipline` — refuse-list for bulk credential spray
