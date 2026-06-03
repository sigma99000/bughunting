# Metadata OSINT

## Document metadata

Office documents (`.docx`, `.xlsx`, `.pptx`) and PDFs embed:

- `Author`, `LastModifiedBy`
- `Company`
- `Application` (e.g., `Microsoft Word 2019`)
- Revision history
- Embedded usernames in tracked changes

Extract:

```bash
exiftool document.docx
unzip -p document.docx docProps/core.xml
unzip -p document.docx docProps/app.xml
```

## Image metadata (EXIF)

```bash
exiftool image.jpg
```

Usually just camera model + GPS. EXIF disclosure alone is a
**never-submit** for bug-bounty — modern programs strip it server-side
or accept the risk explicitly.

## PDF metadata

```bash
exiftool document.pdf
pdfinfo document.pdf
```

PDF can embed JavaScript and form actions — see `hunt-rce` for
PDF-borne RCE via Foxit / Acrobat (CVE-2024-22134 etc.).

## Public author leakage

Search GitHub commit authors for the target's email domain:

```bash
gh search code --owner <org> "@<target-domain>"
```

Author email leaks happen via `.git/config` commits and via Git
commit metadata in `git log`. Catches third-party contractors as
well.

## Domain WHOIS

Mostly redacted in 2026, but corporate registrants often opt out
of privacy:

```bash
whois <domain>
```

Useful: registration date (very new domain may be takeover-target
or phishing infra), registrar (for legal-process correlation),
hostmaster contact.

## Discipline

- Metadata disclosure alone is rarely a finding. Use it as a
  **pivot**: author email → identity fabric → broader recon.
- Don't dump metadata in reports without redaction — sometimes
  contains author home address (PDF) or coordinates (image).

## See also

- `identity-fabric.md`
- `dork-corpus.md`
