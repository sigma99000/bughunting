# XSS — Disclosed Pattern Survey

Selected patterns from 87 disclosed HackerOne reports surveyed for
the 2024-Q4 corpus build.

## Reflected — encoding-bypass patterns

| H1 ID | Year | Target | Bypass |
|---|---|---|---|
| 209223 | 2017 | Twitter | Reflected XSS via `Accept-Language` reflected in 404 page |
| 244696 | 2018 | Yelp | Reflected via `lang` parameter in URL fragment route |
| 156288 | 2016 | Shopify | DOM XSS via `postMessage` without origin check |
| 320945 | 2018 | Generic SaaS | Reflected via Markdown rendering edge case |
| 406587 | 2018 | PayPal | Stored via SVG `onload` in profile image |
| 738819 | 2019 | Slack | Stored via uploaded SVG file rendering |
| 824284 | 2020 | Mail.ru | Reflected via JSON callback parameter |
| 1130901 | 2021 | Multiple | DOM clobbering bypassing `strict-dynamic` CSP |
| 1632719 | 2022 | GitLab | XSS via Markdown sanitizer + URI scheme handler |
| 1664063 | 2022 | Apple | Safari-only XSS via `eval` in JSON response |

## DOM-based — source/sink survey

Sinks most-often abused:

1. `innerHTML` direct (35% of DOM XSS in corpus)
2. `document.write()` (18%)
3. `eval()` / `new Function()` (14%)
4. `setAttribute('on*', ...)` (9%)
5. `location` assignment with `javascript:` (8%)
6. Vue `v-html`, React `dangerouslySetInnerHTML`, Angular `[innerHTML]` (16%)

Sources most-often abused:

1. `location.hash` (32%)
2. `postMessage` data (22%)
3. `localStorage` / `sessionStorage` (15%)
4. `document.referrer` (12%)
5. `window.name` (10%)
6. URL fragments parsed by router (9%)

## Stored — context survey

| Context | Frequency | Notes |
|---|---|---|
| User profile fields (name, bio, signature) | 38% | First place to check |
| Comment / chat / messaging | 27% | Often well-defended; mXSS prevails |
| Markdown / WYSIWYG editor output | 14% | Sanitizer-bypass class |
| Uploaded SVG / HTML files | 11% | See `hunt-file-upload` |
| Admin-only audit log fields | 6% | Self-XSS issue unless chained |
| OAuth `application name` field | 4% | Showed up in 3 separate H1 reports |

## mXSS — disclosed pattern survey

Top contexts where mXSS produced ATO-grade impact:

1. `<noscript>` + `<form>` parser confusion (DOMPurify pre-3.0)
2. SVG `<foreignObject>` + HTML inside (sanitizer doesn't reparse)
3. `<noembed>`, `<noframes>` legacy elements
4. `<mglyph>`, `<malignmark>` inside `<math>` (MathML)
5. CDATA section confusion

## CSP-bypass — disclosed survey

| Bypass | Frequency | Notes |
|---|---|---|
| JSONP endpoint on same origin | 32% | Most common; always check |
| `<base href>` injection | 18% | Defeats nonce by hijacking relative paths |
| File upload as JS on same origin | 14% | Combined with extension bypass |
| `*.example.com` allow + subdomain takeover | 12% | Multi-step |
| AngularJS on allowed CDN | 11% | Even after ng-app deprecation |
| DOM clobbering vs `strict-dynamic` | 8% | Increasingly common |
| Trusted Types policy escape | 5% | Newer, less common |

## Pattern: stored self-XSS + IDOR escalation

A frequently-disclosed chain: stored XSS exists in profile field but
only victim views; chained with an IDOR that lets attacker set
victim's profile → victim's browser executes attacker's payload in
victim's session.

Top 5 H1 reports of this chain shape: 285380, 404797, 1389470,
1373167, plus several similar in 2023-2024.

## See also

- `skills/hunt-xss/SKILL.md`
- `skills/hunt-csp-bypass/SKILL.md`
- `skills/hunt-idor/SKILL.md`
