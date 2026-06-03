# Lab Discipline Rules

These rules apply to every lab in this folder and to any future
lab you contribute.

## Binding

- **All ports bind to `127.0.0.1` only.** Never `0.0.0.0`, never a
  public IP. If a lab requires multi-container networking, use a
  Docker user-defined network and expose the entry container on
  loopback only.

## Secrets

- Lab passwords are literally `"lab"` or `"password"`. Never reuse
  any real secret value.
- Lab "API keys" are placeholders (`AKIAIOSFODNN7EXAMPLE`,
  `sk_test_lab_only_xxxxxx`) and are recognized by `secret_scan.py`'s
  DUMMY_VALUES list.

## Network egress

- Labs should never make outbound HTTP/DNS to anywhere except
  `127.0.0.1` or a clearly-named collaborator (`*.oast.fun`).
- Exception: cloud-emulation labs may talk to LocalStack on
  `localhost:4566`.

## Cleanup

- Every lab folder ships a `make down` / `docker compose down -v`
  target. Run it after every session.
- Labs must not write outside their folder. No `~/.cache` writes,
  no `/tmp/persistent`.

## Realism vs safety tradeoff

Labs are intentionally simpler than real targets in the dimensions
that matter for safety:

- No real outbound C2
- No real persistence
- No real cred theft (everything is `lab` / `password`)

But they're realistic in:

- HTTP protocol details (so smuggling labs reproduce CL.TE faithfully)
- Library behaviour (Jinja2 sandbox modes are real Jinja2)
- Disclosed-CVE behaviour where possible (apache 2.4.49 is the real
  buggy image)

## What labs are **not** for

- Practice for unauthorized testing on real targets
- "Try the same payload here, then on production" — payloads are
  often lab-calibrated and will be noisy on real systems
- A substitute for actual disclosed-program scope

## See also

- `SECURITY.md` (top-level)
- `payload-discipline` skill
