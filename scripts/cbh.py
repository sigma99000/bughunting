#!/usr/bin/env python3
"""
cbh.py — CLI harness for Claude Bug Hunter

Mirror of the Claude Code slash-command surface, runnable outside
the Claude interface. Useful for scripted recon and CI.

Subcommands:
    surface     — scaffold an engagement folder
    recon       — print the phase plan for a target (does not run tools)
    classify    — given an HTTP request/response pair, suggest hunt-* skills
    triage      — run the 7-question gate against a finding markdown file
    report      — render a finding into a platform template
    token-scan  — proxy to secret_scan.py
"""

from __future__ import annotations
import argparse
import json
import os
import shutil
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parent.parent
SKILLS = ROOT / "skills"

SCOPE_TEMPLATE = """# Scope — {program}

## Authorization
- Type: {etype}
- Authority: {auth}
- Window: {window}
- Operator: {operator}

## In scope
- {target}

## Out of scope
- (program-specific — fill in)

## Accepted impact
- Critical: RCE, ATO without UI, data exfil > 10k records
- High:     ATO with 1-click, SQLi to data, SSRF to cloud metadata
- Medium:   stored XSS auth ctx, IDOR with PII
- Low:      reflected XSS, CSRF on state-changing, open redirect (chained)

## Never submit (universal)
- Logout CSRF
- Self-XSS
- Missing security headers without impact
- Banner grabbing / version disclosure alone
- EXIF metadata disclosure
- Rate-limit-only findings
- Clickjacking on non-state-changing pages

## Known issues
- (none yet)
"""

RECON_PLAN = """# Recon plan for {target}

## Phase 1 — passive subdomains
- subfinder -d {target} -all -recursive -silent
- assetfinder --subs-only {target}
- amass enum -passive -d {target} -silent
- crt.sh JSON query

## Phase 2 — liveness + tech
- httpx -l subs.txt -tech-detect -title -status-code -ip -tls-probe -favicon -silent

## Phase 3 — endpoints
- gau {target}
- waybackurls {target}
- katana -u https://{target} -d 3 -jc

## Phase 4 — secret hunting
- cbh.py token-scan --path <each JS bundle URL>

## Phase 5 — dorks
- see skills/offensive-osint/references/dork-corpus.md

## Phase 6 — nuclei
- nuclei -l live.txt -t exposures/ -t misconfiguration/ -t cves/ -severity critical,high
"""

CLASSIFY_RULES = [
    ("hunt-graphql", ["/graphql", "graphql", "__typename"]),
    ("hunt-oauth",   ["redirect_uri", "/oauth/", "response_type=code"]),
    ("hunt-saml",    ["SAMLResponse", "RelayState", "samlp:"]),
    ("hunt-jwt",     ["eyJ", "alg\":", "jku\":"]),
    ("hunt-xxe",     ["<?xml", "<!DOCTYPE", "<!ENTITY"]),
    ("hunt-ssrf",    ["?url=", "?endpoint=", "webhook=", "169.254.169.254"]),
    ("hunt-ssti",    ["{{", "${", "<%=", "#{", "@("]),
    ("hunt-sqli",    ["ORDER BY", "UNION SELECT", "SQLException", "psycopg2"]),
    ("hunt-redirect", ["?return=", "?next=", "?redirect=", "?callback="]),
    ("hunt-file-upload", ["multipart/form-data", "Content-Disposition: form-data"]),
    ("hunt-deserialization", ["aced0005", "rO0AB", "BinaryFormatter", "pickle"]),
    ("hunt-path-traversal", ["../", "..\\", "%2e%2e", "%252e"]),
    ("hunt-smuggling", ["Transfer-Encoding: chunked", "TE.CL", "CL.TE"]),
]


def cmd_surface(args: argparse.Namespace) -> int:
    today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    engagement = Path(args.out or "engagements") / f"{args.target}-{today}"
    if engagement.exists() and not args.force:
        print(f"ERROR: {engagement} already exists (use --force)", file=sys.stderr)
        return 2
    for sub in ("findings", "evidence", "evidence/baseline"):
        (engagement / sub).mkdir(parents=True, exist_ok=True)
    scope = SCOPE_TEMPLATE.format(
        program=args.program or "(fill in)",
        etype=args.type, auth="(SOW / program slug)",
        window="(fill in)", operator=os.environ.get("USER", "operator"),
        target=args.target,
    )
    (engagement / "scope.md").write_text(scope)
    (engagement / "recon-notes.md").write_text(f"# Recon notes — {args.target}\n\n")
    (engagement / "chains.md").write_text("# Chains\n\n")
    print(f"Engagement scaffolded at {engagement}")
    print(f"Next: cbh.py recon --target {args.target}")
    return 0


def cmd_recon(args: argparse.Namespace) -> int:
    print(RECON_PLAN.format(target=args.target))
    return 0


def cmd_classify(args: argparse.Namespace) -> int:
    data = sys.stdin.read() if not args.file else Path(args.file).read_text(errors="replace")
    hits = []
    for skill, signals in CLASSIFY_RULES:
        if any(sig in data for sig in signals):
            hits.append(skill)
    out = {"matched_skills": hits or ["(no high-confidence match)"]}
    print(json.dumps(out, indent=2))
    return 0


def cmd_triage(args: argparse.Namespace) -> int:
    path = Path(args.file)
    if not path.exists():
        print(f"ERROR: {path} not found", file=sys.stderr)
        return 2
    body = path.read_text(errors="replace")
    qs = [
        ("Q1 real HTTP request",       any(k in body for k in ("curl", "POST ", "GET ", ".har"))),
        ("Q2 accepted impact",         "## Impact" in body),
        ("Q3 in scope",                "## Scope" in body or "scope:" in body),
        ("Q4 no admin assumption",     "admin-only" not in body.lower()),
        ("Q5 not disclosed",           "duplicate" not in body.lower()),
        ("Q6 concrete impact",         not any(k in body.lower() for k in ("could be", "may be", "theoretically"))),
        ("Q7 not on never-submit",     not any(k in body.lower() for k in ("self-xss", "logout csrf"))),
    ]
    verdict = "SHIP"
    for q, ok in qs:
        print(f"{q}: {'✅' if ok else '❌'}")
        if not ok:
            verdict = "REVIEW"
    print(f"\nVERDICT: {verdict}")
    return 0 if verdict == "SHIP" else 1


def cmd_report(args: argparse.Namespace) -> int:
    print(f"Render skeleton for platform={args.platform}")
    print("(For full rendering use Claude Code's /report command.)")
    return 0


def cmd_token_scan(args: argparse.Namespace) -> int:
    script = SKILLS / "offensive-osint" / "scripts" / "secret_scan.py"
    if not script.exists():
        print(f"ERROR: secret_scan.py not found at {script}", file=sys.stderr)
        return 2
    py = shutil.which("python3") or shutil.which("python") or sys.executable
    cmd = [py, str(script), "--path", args.path]
    if args.json:
        cmd.append("--json")
    return subprocess.call(cmd)


def main() -> int:
    p = argparse.ArgumentParser(prog="cbh", description="Claude Bug Hunter CLI harness")
    sub = p.add_subparsers(dest="cmd", required=True)

    s = sub.add_parser("surface", help="scaffold an engagement folder")
    s.add_argument("--target", required=True)
    s.add_argument("--program", default=None)
    s.add_argument("--type", default="bugbounty", choices=["bugbounty", "pentest", "redteam"])
    s.add_argument("--out", default=None)
    s.add_argument("--force", action="store_true")
    s.set_defaults(func=cmd_surface)

    r = sub.add_parser("recon", help="emit the recon phase plan")
    r.add_argument("--target", required=True)
    r.set_defaults(func=cmd_recon)

    c = sub.add_parser("classify", help="suggest hunt-* skill(s) for a request/response")
    c.add_argument("--file", default=None, help="file containing the dump (default: stdin)")
    c.set_defaults(func=cmd_classify)

    t = sub.add_parser("triage", help="run the 7-question gate against a finding markdown file")
    t.add_argument("--file", required=True)
    t.set_defaults(func=cmd_triage)

    rp = sub.add_parser("report", help="render a finding (skeleton only; full render in Claude Code)")
    rp.add_argument("--finding", required=True)
    rp.add_argument("--platform", default="h1", choices=["h1", "bc", "intigriti", "immunefi", "client"])
    rp.set_defaults(func=cmd_report)

    ts = sub.add_parser("token-scan", help="scan files/URLs/dirs for hardcoded secrets")
    ts.add_argument("--path", required=True)
    ts.add_argument("--json", action="store_true")
    ts.set_defaults(func=cmd_token_scan)

    args = p.parse_args()
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
