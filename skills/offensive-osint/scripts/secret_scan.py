#!/usr/bin/env python3
"""
secret_scan.py — scan files/dirs/URLs for hardcoded secrets

Reads pattern definitions inline (mirrored from
skills/offensive-osint/references/secret-patterns.md). Computes
Shannon entropy per match and filters below per-pattern threshold.

Usage:
    secret_scan.py path=<file|dir|url|git-url> [validate=true]

Output: JSON-lines to stdout, one hit per line.
"""

from __future__ import annotations
import argparse
import json
import math
import os
import re
import sys
import tempfile
import urllib.request
from collections import Counter
from pathlib import Path
from typing import Iterable, NamedTuple

# Pattern definitions: (class, compiled regex, entropy threshold)
PATTERNS: list[tuple[str, re.Pattern[str], float]] = [
    ("AWS_ACCESS_KEY_ID",       re.compile(r"\bAKIA[0-9A-Z]{16}\b"),                                      3.5),
    ("AWS_TEMP_ACCESS_KEY_ID",  re.compile(r"\bASIA[0-9A-Z]{16}\b"),                                      3.5),
    ("AWS_SECRET_ACCESS_KEY",   re.compile(r"(?i)aws.{0,20}?(?:secret|key).{0,20}?['\"]([A-Za-z0-9/+=]{40})['\"]"), 4.5),
    ("GCP_API_KEY",             re.compile(r"\bAIza[0-9A-Za-z\-_]{35}\b"),                                4.0),
    ("GCP_OAUTH_CLIENT_SECRET", re.compile(r"\bGOCSPX-[A-Za-z0-9_-]{28}\b"),                              4.5),
    ("FIREBASE_FCM_KEY",        re.compile(r"\bAAAA[A-Za-z0-9_-]{7}:[A-Za-z0-9_-]{140}\b"),               4.5),
    ("STRIPE_LIVE_SECRET",      re.compile(r"\bsk_live_[0-9a-zA-Z]{24,99}\b"),                            4.5),
    ("STRIPE_TEST_SECRET",      re.compile(r"\bsk_test_[0-9a-zA-Z]{24,99}\b"),                            4.5),
    ("STRIPE_RESTRICTED",       re.compile(r"\brk_live_[0-9a-zA-Z]{24,99}\b"),                            4.5),
    ("TWILIO_ACCOUNT_SID",      re.compile(r"\bAC[a-f0-9]{32}\b"),                                        3.5),
    ("TWILIO_API_KEY_SID",      re.compile(r"\bSK[a-f0-9]{32}\b"),                                        3.5),
    ("SENDGRID_API_KEY",        re.compile(r"\bSG\.[A-Za-z0-9_-]{22}\.[A-Za-z0-9_-]{43}\b"),              4.5),
    ("SLACK_BOT_TOKEN",         re.compile(r"\bxoxb-[0-9]{10,13}-[0-9]{10,13}-[A-Za-z0-9]{24,34}\b"),     4.0),
    ("SLACK_USER_TOKEN",        re.compile(r"\bxoxp-[0-9]{10,13}-[0-9]{10,13}-[0-9]{10,13}-[a-f0-9]{32}\b"), 4.0),
    ("SLACK_WORKSPACE_TOKEN",   re.compile(r"\bxoxa-[0-9]+-[A-Za-z0-9-]+\b"),                             4.0),
    ("SLACK_WEBHOOK",           re.compile(r"https://hooks\.slack\.com/services/T[A-Z0-9]+/B[A-Z0-9]+/[A-Za-z0-9]{24}"), 0.0),
    ("GITHUB_PAT_CLASSIC",      re.compile(r"\bghp_[A-Za-z0-9]{36}\b"),                                   4.5),
    ("GITHUB_PAT_FINEGRAINED",  re.compile(r"\bgithub_pat_[A-Za-z0-9_]{82}\b"),                           4.5),
    ("GITHUB_OAUTH",            re.compile(r"\bgho_[A-Za-z0-9]{36}\b"),                                   4.5),
    ("GITHUB_APP_USER",         re.compile(r"\bghu_[A-Za-z0-9]{36}\b"),                                   4.5),
    ("GITHUB_APP_SERVER",       re.compile(r"\bghs_[A-Za-z0-9]{36}\b"),                                   4.5),
    ("GITHUB_REFRESH",          re.compile(r"\bghr_[A-Za-z0-9]{36}\b"),                                   4.5),
    ("GITLAB_PAT",              re.compile(r"\bglpat-[A-Za-z0-9_-]{20}\b"),                               4.0),
    ("GITLAB_RUNNER",           re.compile(r"\bglrt-[A-Za-z0-9_-]{20}\b"),                                4.0),
    ("BITBUCKET_APP_PASSWORD",  re.compile(r"\bATBB[A-F0-9]{32}\b"),                                      3.5),
    ("NPM_TOKEN",               re.compile(r"\bnpm_[A-Za-z0-9]{36}\b"),                                   4.5),
    ("DOCKER_HUB_TOKEN",        re.compile(r"\bdckr_pat_[A-Za-z0-9_-]{27,}\b"),                           4.0),
    ("HUGGINGFACE_TOKEN",       re.compile(r"\bhf_[A-Za-z]{34}\b"),                                       4.0),
    ("OPENAI_API_KEY",          re.compile(r"\bsk-[A-Za-z0-9]{20,}\b"),                                   4.0),
    ("OPENAI_PROJECT_KEY",      re.compile(r"\bsk-proj-[A-Za-z0-9_-]{40,}\b"),                            4.5),
    ("ANTHROPIC_API_KEY",       re.compile(r"\bsk-ant-api03-[A-Za-z0-9_-]{93}-[A-Za-z0-9_-]{3}AA\b"),     4.5),
    ("MAILGUN_PRIVATE",         re.compile(r"\bkey-[a-f0-9]{32}\b"),                                      3.5),
    ("MAPBOX_SECRET",           re.compile(r"\bpk\.eyJ[A-Za-z0-9_-]+\.[A-Za-z0-9_-]+\b"),                 4.5),
    ("TELEGRAM_BOT_TOKEN",      re.compile(r"\b[0-9]{8,10}:[A-Za-z0-9_-]{35}\b"),                         4.5),
    ("DISCORD_BOT_TOKEN",       re.compile(r"\b[MN][A-Za-z0-9]{23}\.[\w-]{6}\.[\w-]{27}\b"),              4.5),
    ("DISCORD_WEBHOOK",         re.compile(r"https://discord(?:app)?\.com/api/webhooks/[0-9]+/[A-Za-z0-9_-]+"), 0.0),
    ("DIGITALOCEAN_PAT",        re.compile(r"\bdop_v1_[a-f0-9]{64}\b"),                                   4.5),
    ("DOPPLER",                 re.compile(r"\bdp\.pt\.[A-Za-z0-9]{43}\b"),                               4.5),
    ("VAULT_TOKEN",             re.compile(r"\bhvs\.[A-Za-z0-9_-]{90,}\b"),                               4.5),
    ("SENTRY_DSN",              re.compile(r"https://[a-f0-9]{32}@[a-z0-9.]+\.ingest\.sentry\.io/[0-9]+"), 0.0),
    ("NEWRELIC_USER_KEY",       re.compile(r"\bNRAK-[A-Z0-9]{27}\b"),                                     4.0),
    ("LINEAR_KEY",              re.compile(r"\blin_api_[A-Za-z0-9]{40}\b"),                               4.5),
    ("NOTION_SECRET",           re.compile(r"\bsecret_[A-Za-z0-9]{43}\b"),                                4.5),
    ("ATLASSIAN_API",           re.compile(r"\bATATT3xFfGF0[A-Za-z0-9_-]{180}=[A-Za-z0-9]{8}\b"),         4.5),
    ("SQUARE_ACCESS",           re.compile(r"\bEAAA[A-Za-z0-9_-]{60}\b"),                                 4.5),
    ("PAYPAL_BRAINTREE",        re.compile(r"access_token\$production\$[0-9a-z]{16}\$[0-9a-f]{32}"),      4.5),
    ("RSA_PRIVATE_KEY",         re.compile(r"-----BEGIN RSA PRIVATE KEY-----"),                           0.0),
    ("OPENSSH_PRIVATE_KEY",     re.compile(r"-----BEGIN OPENSSH PRIVATE KEY-----"),                       0.0),
    ("EC_PRIVATE_KEY",          re.compile(r"-----BEGIN EC PRIVATE KEY-----"),                            0.0),
    ("PGP_PRIVATE_KEY",         re.compile(r"-----BEGIN PGP PRIVATE KEY BLOCK-----"),                     0.0),
    ("JWT",                     re.compile(r"\beyJ[A-Za-z0-9_-]+\.eyJ[A-Za-z0-9_-]+\.[A-Za-z0-9_-]{10,}\b"), 0.0),
    ("POSTGRES_URL",            re.compile(r"postgres(?:ql)?://[^:\s]+:[^@\s]+@[^/\s]+/\w+"),             0.0),
    ("MYSQL_URL",               re.compile(r"mysql://[^:\s]+:[^@\s]+@[^/\s]+/\w+"),                       0.0),
    ("MONGODB_URL",             re.compile(r"mongodb(?:\+srv)?://[^:\s]+:[^@\s]+@[^/\s]+"),               0.0),
    ("REDIS_URL",               re.compile(r"redis://[^:\s]*:[^@\s]+@[^/\s]+"),                           0.0),
]

# Files/dirs to skip
SKIP_DIRS = {".git", "node_modules", "vendor", "__pycache__", ".venv", "venv", "dist", ".next"}
EXT_INCLUDE = {".js", ".jsx", ".ts", ".tsx", ".map", ".json", ".yaml", ".yml",
               ".env", ".conf", ".cfg", ".ini", ".toml", ".py", ".rb", ".php",
               ".java", ".go", ".rs", ".html", ".md", ".txt", ".sh", ".bash",
               ".tf", ".pem", ".crt", ".key"}

# Known dummy values to ignore (extend over time)
DUMMY_VALUES = {
    "AKIAIOSFODNN7EXAMPLE",
    "wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY",
    "sk_test_4eC39HqLyjWDarjtT1zdp7dc",
}


class Hit(NamedTuple):
    cls: str
    value: str
    file: str
    line: int
    entropy: float


def shannon_entropy(s: str) -> float:
    if not s:
        return 0.0
    counts = Counter(s)
    n = len(s)
    return -sum((c / n) * math.log2(c / n) for c in counts.values())


def scan_text(text: str, source: str) -> Iterable[Hit]:
    for line_no, line in enumerate(text.splitlines(), start=1):
        for cls, regex, thresh in PATTERNS:
            for m in regex.finditer(line):
                val = m.group(1) if m.groups() else m.group(0)
                if val in DUMMY_VALUES:
                    continue
                ent = shannon_entropy(val)
                if ent >= thresh:
                    yield Hit(cls, val, source, line_no, round(ent, 2))


def iter_files(root: Path) -> Iterable[Path]:
    if root.is_file():
        yield root
        return
    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = [d for d in dirnames if d not in SKIP_DIRS]
        for fname in filenames:
            p = Path(dirpath) / fname
            if p.suffix.lower() in EXT_INCLUDE or fname.startswith(".env"):
                yield p


def fetch_url(url: str) -> Path:
    suffix = ".js" if url.endswith(".js") else ".bin"
    fd, path = tempfile.mkstemp(suffix=suffix)
    os.close(fd)
    req = urllib.request.Request(url, headers={"User-Agent": "cbh-secret-scan/1.0"})
    with urllib.request.urlopen(req, timeout=30) as resp, open(path, "wb") as f:
        f.write(resp.read())
    return Path(path)


def mask(val: str) -> str:
    if len(val) <= 8:
        return val[:2] + "•" * (len(val) - 2)
    return val[:4] + "•" * (len(val) - 8) + val[-4:]


def main() -> int:
    parser = argparse.ArgumentParser(description="Scan for hardcoded secrets")
    parser.add_argument("--path", required=True, help="file, directory, or URL")
    parser.add_argument("--mask", action="store_true", default=True, help="mask values in output (default)")
    parser.add_argument("--no-mask", dest="mask", action="store_false")
    parser.add_argument("--json", action="store_true", help="emit JSON lines (default: human)")
    args = parser.parse_args()

    target = args.path
    cleanup: list[Path] = []
    try:
        if target.startswith(("http://", "https://")):
            local = fetch_url(target)
            cleanup.append(local)
            roots = [local]
            source_label = target
        else:
            p = Path(target).expanduser().resolve()
            if not p.exists():
                print(f"ERROR: {p} does not exist", file=sys.stderr)
                return 2
            roots = [p]
            source_label = str(p)

        n_files = 0
        n_hits = 0
        for root in roots:
            for fp in iter_files(root):
                n_files += 1
                try:
                    text = fp.read_text(encoding="utf-8", errors="replace")
                except (OSError, UnicodeDecodeError):
                    continue
                for hit in scan_text(text, source_label if fp in cleanup else str(fp)):
                    n_hits += 1
                    out_val = mask(hit.value) if args.mask else hit.value
                    if args.json:
                        print(json.dumps({
                            "class": hit.cls, "value": out_val,
                            "file": hit.file, "line": hit.line, "entropy": hit.entropy
                        }))
                    else:
                        print(f"[{hit.cls}] {hit.file}:{hit.line}  {out_val}  (entropy {hit.entropy})")
        if not args.json:
            print(f"\nScanned {n_files} file(s); {n_hits} hit(s).", file=sys.stderr)
        return 0
    finally:
        for c in cleanup:
            try:
                c.unlink()
            except OSError:
                pass


if __name__ == "__main__":
    sys.exit(main())
