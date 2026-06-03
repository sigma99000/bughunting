# JS Bundle Analysis

## Acquire

```bash
# Single bundle
curl -O https://target/static/js/main.<hash>.js

# All bundles from a target
subjs -i live.txt > js-urls.txt
xargs -I{} curl -O {} < js-urls.txt
```

## Beautify

```bash
js-beautify main.bundle.js > main.pretty.js
# Or use online beautifiers for one-offs
```

## Source map recovery

Bundlers leave a hint at the bottom:

```
//# sourceMappingURL=main.<hash>.js.map
```

If the map file is publicly fetchable:

```bash
curl -O https://target/static/js/main.<hash>.js.map
# Use shuji or unwebpack-sourcemap to recover original source
npx shuji main.<hash>.js.map -o src/
```

Recovered source often contains:
- Original variable names
- Comments
- Test fixtures
- API documentation strings

## Endpoint mining

```bash
linkfinder.py -i main.pretty.js -o cli
# Or simple grep:
grep -oE '"/api[^"]+"' main.pretty.js | sort -u
```

## Secret hunting

```bash
python scripts/secret_scan.py path=main.pretty.js
```

See `secret-patterns.md`.

## React / Vue / Angular specific

Look for:
- Embedded `__PRELOADED_STATE__` — server-side-rendered data
- Webpack module IDs and chunk names — often leak feature flags
- `__REACT_DEVTOOLS_GLOBAL_HOOK__` referenced in prod (DevTools on)
- Apollo client config — GraphQL endpoint, persisted query URL
- Firebase config — `apiKey`, `authDomain`, `databaseURL`

## Wallet / Web3

Embedded RPC URLs, contract ABIs (`abi: [...]`), private network IDs.

## See also

- `secret-patterns.md`
- `dork-corpus.md` (GitHub mirror of source)
- `hunt-graphql` for endpoint mining
