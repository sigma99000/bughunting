---
name: hunt-prototype-pollution
description: JavaScript prototype pollution — client + server gadgets, lodash/jQuery/merge sinks, JSON parser quirks.
keywords: [prototype pollution, __proto__, constructor.prototype, lodash, jquery merge, pp, gadget]
---

# hunt-prototype-pollution

## Triggers

"prototype pollution", `__proto__`, "lodash merge", "jquery extend".

## Phase 1 — find the sink

Server (Node.js):

- `lodash.merge`, `lodash.defaultsDeep`, `lodash.set` ≤ 4.17.20
- `jQuery.extend(true, ...)`
- Plain recursive merge utilities written in-house
- `qs.parse(..., { allowPrototypes: true })`
- Any JSON parser that doesn't filter `__proto__`

Client:

- Same plus URL → object parsers (`querystring`, `qs`, `url-parse`)
- `Object.assign` chains
- DOM-clobbering of `Object.prototype`

## Phase 2 — pollute

POST body with prototype-polluting JSON:

```json
{"__proto__": {"isAdmin": true}}
{"constructor": {"prototype": {"isAdmin": true}}}
```

URL-encoded query string:

```
?__proto__[isAdmin]=true
?__proto__.isAdmin=true
?constructor[prototype][isAdmin]=true
```

After pollution, every freshly-created object inherits `isAdmin: true`.

## Phase 3 — server gadgets to RCE

Once pollution is confirmed, find a gadget that flips behavior. Famous:

| Gadget | Reaches |
|---|---|
| `child_process` `shell` option default | Spawn flag injection → arbitrary command |
| Express `query parser` | Reflected pollution in routing |
| `ejs` template options `outputFunctionName` | RCE on next render |
| `mongoose` `Document.prototype.$session` | Logic bypass |
| `koa` ctx defaults | Inject `Content-Type` / status |

PortSwigger's `Server-Side Prototype Pollution Scanner` Burp ext
finds gadgets.

## Phase 4 — client-side gadgets to XSS

| Library | Gadget |
|---|---|
| jQuery | `<script>` element creation pulls `src` from pollutable property |
| Underscore template | Compiled with polluted options |
| AdyenCheckout (and others) | Look for `Object.assign(defaults, options)` |

## Disclosed-report patterns

| Source | Pattern |
|---|---|
| H1 #2210024 (Backstage) | Pollution → SSRF |
| H1 #1130901 (Slack-like) | Pollution + CSP bypass to XSS |
| CVE-2019-10746 (mixin-deep) | Pollution in npm pkg |
| CVE-2019-11358 (jQuery < 3.4) | Object.prototype pollution via `$.extend` |
| CVE-2022-24999 (qs) | Reflected pollution to Express |
| CVE-2025-25208 (lodash >=4.17.21 escape hatch) | Yet another lodash bypass |

## Never-submit fallbacks

- Pollution without a downstream gadget → CHAIN REQUIRED
- Pollution of a property the app never reads → DOWNGRADE/KILL

## See also

- `hunt-xss`, `hunt-rce`
