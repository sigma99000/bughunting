# File Upload — Disclosed Pattern Survey

49 disclosed reports.

## Bypass-technique frequency

| Technique | Frequency |
|---|---|
| Extension allow/deny list incomplete (`.phtml`, `.phar`, `.php5`) | 23% |
| MIME type trusted client-side | 18% |
| Filename traversal (`shell.php\x00.png`) | 14% |
| Polyglot magic bytes (GIF89a + PHP) | 12% |
| Server-side image processor RCE (ImageMagick, ExifTool) | 11% |
| .htaccess / web.config upload enabling handler | 9% |
| SVG → stored XSS in same-origin | 7% |
| Zip slip in archive upload | 4% |
| Other | 2% |

## Landmark vulnerabilities

- CVE-2016-3714 (ImageTragick) — MVG injection in ImageMagick
- CVE-2018-16509 (Ghostscript) — PostScript via JPEG-2000
- CVE-2021-22204 (ExifTool) — DjVu metadata
- CVE-2022-44268 (ImageMagick PNG) — profile-read arbitrary file
- CVE-2025-31324 (SAP NetWeaver Visual Composer) — unrestricted upload
- H1 #1057296 — Polyglot PNG+PHP via `.phar`

## See also

- `skills/hunt-file-upload/SKILL.md`
- `skills/hunt-rce/SKILL.md`
- `skills/hunt-xss/SKILL.md` (SVG vector)
