# Installation

## Prerequisites

- Claude Code (Desktop or VS Code extension) ≥ April 2025 build
- Python 3.10+ (for `cbh.py`, `refresh-cve-index.py`, `secret_scan.py`)
- Optional: `subfinder`, `httpx`, `nuclei`, `gau`, `katana`, `waybackurls`
  for recon. CBH will degrade gracefully if these aren't installed.

## 1. Clone

```bash
git clone https://github.com/your-org/claude-bughunter ~/code/claude-bughunter
cd ~/code/claude-bughunter
```

## 2. Symlink into Claude's skill directory

Claude Code auto-loads skills from `~/.claude/skills/` (Mac/Linux) or
`%USERPROFILE%\.claude\skills\` (Windows). Run:

```bash
bash scripts/install.sh
```

This script:

1. Creates `~/.claude/skills/` if missing.
2. Symlinks each `skills/<name>` into `~/.claude/skills/<name>`.
3. Symlinks each `commands/<name>.md` into `~/.claude/commands/<name>.md`.
4. Adds `cbh.py` to your `PATH` via a `~/.local/bin/cbh` shim.

### Manual install (Windows / no symlink permissions)

Copy the `skills/` and `commands/` contents directly:

```powershell
robocopy skills  "$env:USERPROFILE\.claude\skills"   /E
robocopy commands "$env:USERPROFILE\.claude\commands" /E
```

## 3. Verify

Restart Claude Code, then run:

```
/hunt --help
```

You should see the engagement-scaffold prompt.

## 4. (Optional) Refresh CVE index

`enterprise-vpn-attack`, `m365-entra-attack`, and `vcenter-attack` ship
with a curated CVE table. To pull the latest from NVD:

```bash
python scripts/refresh-cve-index.py --vendor cisco,fortinet,citrix,paloalto,pulse,sonicwall,f5
```

The script writes to `skills/enterprise-vpn-attack/cve-index.json` and
re-renders the markdown table embedded in `SKILL.md`.

## 5. Editor integration

### VS Code

CBH skills are auto-discovered by the Claude Code extension. To get
hover-help for slash commands, add to your `settings.json`:

```json
{
  "claudeCode.skills.autoLoad": true,
  "claudeCode.commands.searchPaths": ["~/.claude/commands"]
}
```

### Claude Desktop

Symlinks alone are sufficient. Restart Claude Desktop after install.

## Troubleshooting

| Symptom | Fix |
|---------|-----|
| `/hunt` not recognized | Verify `~/.claude/commands/hunt.md` exists |
| Skills not loading on keyword | Restart Claude; check that `~/.claude/skills/<name>/SKILL.md` is readable |
| `cbh.py: command not found` | Add `~/.local/bin` to `PATH` |
| `refresh-cve-index.py` fails | NVD rate-limits unauthenticated requests to 5/30s — pass `--api-key` |
