# Identity Fabric

Email → username → SaaS account enumeration across 30 platforms.

## Why

When recon yields `alice@example.com`, the identity fabric lets
you find every SaaS account Alice has — which expands the
credential-stuffing surface and the engineering risk surface.

## Discipline

- **Use only test accounts you control** for active enumeration.
- **Never** probe a real person's account without explicit
  engagement authorization. This is a fast path to harassment
  complaints and program bans.
- Most SaaS platforms now treat enumeration as ToS violation.
  Passive sources (mentions in public profiles) only by default.

## Email → username transform corpus

For an email `firstname.lastname@example.com`, common usernames are:

```
firstname.lastname
firstnamelastname
firstname_lastname
firstname-lastname
flastname
firstname.l
flast
firstname
lastname
{employee_id}            (numeric, harder to predict)
{firstinitial}{lastname}
{first3letters}{lastname}
{lastname}{first3}
```

## Platform → enum vector

| Platform | Vector (passive — public-only checks) |
|---|---|
| GitHub | `https://github.com/<username>` — 200 if exists |
| GitLab | `https://gitlab.com/<username>` |
| Bitbucket | `https://bitbucket.org/<username>` |
| LinkedIn | Search by company (no API) — visual inspection |
| Twitter / X | `https://twitter.com/<username>` |
| Slack (public dirs) | `<workspace>.slack.com/team/<userid>` |
| Notion (public pages) | search engine for `<name> site:notion.so` |
| Trello (public boards) | similar |
| Atlassian (Jira issue exports leaked) | search dorks |
| Salesforce (Trailhead public profile) | trailblazer.me/id/<username> |
| Medium | `https://medium.com/@<username>` |
| Dev.to | `https://dev.to/<username>` |
| Stack Overflow | `https://stackoverflow.com/users/?tab=Users&filter=all&search=<name>` |
| Goodreads | personal profile leakage |
| Strava | activity heatmaps (operational-security risk) |
| Steam | game profiles (less relevant) |
| Twitch | `https://twitch.tv/<username>` |
| YouTube | channel slug enumeration |
| Reddit | `https://reddit.com/user/<username>` |
| Keybase | `https://keybase.io/<username>` — gold for verified identities |
| HackerOne | `https://hackerone.com/<username>` |
| Bugcrowd | `https://bugcrowd.com/<username>` |
| Intigriti | `https://intigriti.com/<username>` |
| Twitter alt | bsky.app, mastodon, threads |
| Snapchat / Instagram | username matching (limited public surface) |
| TikTok | `https://tiktok.com/@<username>` |
| Behance | `https://behance.net/<username>` |
| Dribbble | `https://dribbble.com/<username>` |
| Pinterest | `https://pinterest.com/<username>` |
| Discord | invite-only servers; not directly enumerable |
| Spotify | profile URLs from playlists |

## Tools (passive only)

```bash
# Sherlock — username across 400+ sites
pip install sherlock-project
sherlock <username> --print-found --timeout 10

# Maigret — sherlock fork with more sites
pip install maigret
maigret <username> --no-color --print-not-found false

# WhatsMyName
git clone https://github.com/WebBreacher/WhatsMyName
python web_accounts_list_checker.py -u <username>
```

All three are passive (web-only GET requests). They still hit
those platforms — rate-limit yourself (`--timeout 10`).

## Email → breach correlation

See `breach-and-credentials.md`. Have I Been Pwned API gives
breach history per email. Combine with identity fabric to map:

```
alice@example.com → GitHub: alice99 → leaked in OneTask 2023 breach
                                    → password hash: bcrypt $2b$...
                                    → cracked: "Summer2023!"  (per HIBP-affiliated data)
                                    → reuse check: tested on M365 spray — locked out
```

(Don't actually try the credential against an org without
engagement authorization — and even with authorization, slow-spray.)

## Corporate identity surface

If the target has these public profiles, exposure exists:

- Corporate Slack Connect channels (`/team/U...`)
- Open-source contribution graph (employee names leaked via commit
  authorship)
- Conference speaker pages
- Job posting "team is led by..." sections
- LinkedIn "Worked at..." chains

## See also

- `dork-corpus.md` — search-engine entry points
- `breach-and-credentials.md` — HIBP integration
- `recon-stack.md` — tooling
- `redteam-mindset` — credential-reuse playbook
