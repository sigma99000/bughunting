#!/usr/bin/env bash
# hunt.sh — bash wrapper for engagement scaffolding (mirrors /surface).
#
# Usage: hunt.sh <target> [program] [type]

set -euo pipefail

target="${1:-}"
program="${2:-}"
type="${3:-bugbounty}"

if [ -z "$target" ]; then
    cat <<USAGE
hunt.sh <target> [program] [type]

Examples:
  hunt.sh app.example.com h1-acme bugbounty
  hunt.sh corp.acme.com pentest-acme-2026q1 pentest
  hunt.sh corp.acme.com sow-2026-001 redteam
USAGE
    exit 2
fi

REPO="$(cd "$(dirname "$0")/.." && pwd)"
exec python3 "$REPO/scripts/cbh.py" surface \
    --target "$target" \
    --program "${program:-(fill in)}" \
    --type "$type"
