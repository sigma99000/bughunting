---
name: hunt-saml
description: SAML SSO attack — XML signature wrapping (XSW), assertion replay, audience confusion, XXE in SAML.
keywords: [saml, sso, assertion, xml signature wrapping, xsw, audience, idp-initiated, sp-initiated, ws-fed]
---

# hunt-saml

## When this skill loads

Triggers: "saml", "ws-fed", "assertion", "samlresponse", "idp-init",
"sp-init", "metadata.xml", "single sign-on".

## Pre-flight

Capture a full SAML round trip with SAML Raider / Burp SAML extension.
You need:

- The IdP's signing certificate (from metadata)
- A SAML Response with a known-valid signature
- The audience/recipient URLs the SP enforces

## Phase 1 — XML Signature Wrapping (XSW)

Eight canonical XSW patterns. Library bugs in older versions of
OpenSAML, python3-saml, ruby-saml, simplesamlphp, Spring Security
SAML, .NET WIF all had at least one of these.

| XSW # | Technique |
|---|---|
| XSW-1 | Wrap original Response in a new envelope; signature points to original |
| XSW-2 | New Response sibling to original; signature in original |
| XSW-3 | Replace assertion contents; signature still validates over wrapped original |
| XSW-4 | Reference moved; canonicalization difference |
| XSW-5 | Two assertions: one signed (ignored), one evaluated (unsigned) |
| XSW-6 | Comment injection in NameID (`admin<!-- -->@example.com` ≠ `admin@example.com` in some parsers) |
| XSW-7 | Extensions element wrap |
| XSW-8 | Object element wrap |

Use **SAML Raider** to auto-generate XSW1-8 with one click. For each,
change the NameID / attribute to a different user (e.g.,
`admin@example.com`) and submit.

## Phase 2 — comment injection in NameID

This is the famous "Duo SAML" / "GitHub SAML" 2018 bug:

```xml
<NameID>victim<!---->@example.com</NameID>
```

Some XML parsers strip the comment before the SP reads NameID; others
keep it. If signing happens on the un-stripped value but SP reads the
stripped value, you assert as `victim@example.com` while signing the
attacker's legit `victim<!---->@example.com` value.

Test variations:

```
admin<!---->@example.com
admin@<!---->example.com
victim%00admin@example.com   (null byte; less common but try)
```

## Phase 3 — assertion replay

Capture a valid Response. Try:

- Replay verbatim → SP should reject (`NotOnOrAfter` enforcement)
- Replay with extended `NotOnOrAfter` (but signature breaks) →
  combine with XSW
- Replay in a different session (no `InResponseTo` binding) →
  IdP-initiated flows often skip this

## Phase 4 — audience confusion

`<Audience>` should equal the SP's `EntityID`. Test:

- Multi-audience: add `<AudienceRestriction>` with multiple URIs
- Substring confusion: `Audience=https://app.example.com.attacker.com`
- Missing entirely

## Phase 5 — algorithm downgrade

- Change signature algorithm to `none` (some SAML libs accept)
- Downgrade `sha256` → `sha1` if SP accepts; collision possible
- HMAC vs RSA confusion: replace `<SignatureMethod Algorithm="rsa-sha256">`
  with `hmac-sha256`; if SP uses the public cert as HMAC key, you can
  forge

## Phase 6 — XXE in SAML

SAML is XML — every parser is a potential XXE sink:

```xml
<!DOCTYPE samlp:Response [ <!ENTITY xxe SYSTEM "file:///etc/passwd"> ]>
<samlp:Response ...>
  <Issuer>&xxe;</Issuer>
  ...
</samlp:Response>
```

Test in:
- `<Issuer>`
- Attribute values
- Subject NameID

Disclosed in OpenSAML CVE-2014-1456, ruby-saml CVE-2017-11427.

## Phase 7 — encryption stripping

If `<EncryptedAssertion>` is used, try:

- Submit unencrypted assertion alongside encrypted → some libs read both
- Strip encryption → SP must enforce `WantAssertionsEncrypted` from
  metadata

## Phase 8 — IdP-init vs SP-init

| Mode | Attack |
|---|---|
| IdP-initiated | No `InResponseTo` → no CSRF protection. Lure victim to click attacker-hosted form posting an attacker assertion → SP logs victim in as attacker (CSRF to authenticated session) — useful for credential theft via session fixation later |
| SP-initiated | `InResponseTo` should bind to AuthnRequest ID; if not enforced, accept arbitrary responses |

## Disclosed-report patterns

| Source | Pattern |
|---|---|
| Duo 2018 advisory | NameID comment-truncation across 4+ libraries |
| GitHub 2018 | XSW + comment injection → ATO via SAML |
| CVE-2017-11427 (ruby-saml) | XSW XSW-1 |
| CVE-2024-45409 (Ruby OmniAuth-SAML) | Signature bypass via XSW |
| H1 #1031218 (Slack-like) | Audience confusion accepting `app.example.com.attacker` |
| CVE-2022-29874 (Apache Pulsar) | XML external entity in SAML |

## Never-submit fallbacks

- "SP accepts unsigned assertion" without proving forgery → KILL
  (need a verified-forged assertion with different NameID).
- XSW that returns 500 but doesn't log in → CHAIN REQUIRED (find the
  parser bug that flips it to 200).

## See also

- `hunt-xxe` — SAML is XML; XXE sinks are commonly here
- `hunt-jwt` — siblings in OIDC space
- `m365-entra-attack` — Entra-specific SAML quirks (claim transforms)
