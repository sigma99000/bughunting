# Credits & Sources

Claude Bug Hunter distills knowledge from publicly available
sources. This file lists them so users can verify any claim made
in a skill.

## Disclosed-report corpora

| Source | Use |
|---|---|
| HackerOne Hacktivity (public reports) | Pattern source for all `hunt-*` skills; 681 reports surveyed for the 2024-Q4 corpus build |
| Bugcrowd Disclosed Reports | Cross-validation of severity / VRT mapping |
| Intigriti public disclosures | ITG-VR mapping |
| Immunefi public reports | Web3 pattern source for `web3-audit` |
| ZDI publications | Vendor-coordinated disclosures, especially network appliances |

## Standards & taxonomies

| Source | Use |
|---|---|
| OWASP WSTG (Web Security Testing Guide) | Phase structure for `hunt-*` skills |
| OWASP Top 10 (2021 + 2026 update) | Severity calibration |
| Bugcrowd VRT 1.13 | `bugcrowd-reporting` mapping |
| FIRST CVSS 3.1 | Severity scoring across all skills |
| MITRE ATT&CK Enterprise | `redteam-mindset` + `redteam-report-template` TID mapping |
| MITRE CWE | `h1-reporting` CWE selection table |
| NIST 800-53 | Remediation references in `report-writing` |

## Research blogs & talks

| Source | Use |
|---|---|
| PortSwigger Web Security Academy | Smuggling, cache poisoning, race-condition patterns |
| Doyensec | Prototype pollution, GraphQL research |
| Snyk research | Library-class CVE coverage |
| Simon Willison's blog | Indirect prompt-injection corpus for `llm-attack` |
| Zenity research (Michael Bargury et al.) | Copilot ATO patterns for `llm-ato` |
| Cure53 advisories | DOMPurify / XSS / mXSS variants |
| Project Zero | Various CVE walkthroughs |
| Black Hat / DEF CON archives | Smuggling, SSRF research |
| Lupin (Frans Rosén) research | OAuth + open redirect chains |
| Marcin Wielgoszewski / Brett Buerhaus posts | OAuth, SAML |

## CVE & advisory feeds

- NVD (National Vulnerability Database) — primary CVE source
- MSRC (Microsoft Security Response Center) — Exchange / SharePoint advisories
- VMware Security Advisories (VMSA) — vCenter / ESXi
- Fortinet PSIRT — FortiOS / FortiGate advisories
- Citrix Security Bulletins (CTX...) — NetScaler / Gateway / ADC
- Palo Alto Networks Security Advisories
- Pulse / Ivanti Trust Portal
- Cisco PSIRT advisories
- SonicWall PSIRT advisories
- F5 Security Advisories

## Tool authors (recon-stack)

Special thanks to:

- ProjectDiscovery (subfinder, httpx, nuclei, katana, dnsx, chaos)
- TomNomNom (assetfinder, waybackurls, etc.)
- OWASP Amass team
- The SecLists maintainers (wordlist corpus)
- PortSwigger (Burp + Turbo Intruder + smuggler)
- Trail of Bits (slither, echidna)
- Foundry team (Web3 testing)

## Disclaimer

CBH includes **patterns** and **methodology** distilled from these
sources. No copyrighted text is reproduced verbatim. Any
disclosed-report reference is by H1 report ID, CVE ID, or named
research title — readers should consult the original source for
full detail.

If you author a research piece referenced here and would like the
citation adjusted (or removed), email the maintainers per
`SECURITY.md`.

## License of the bundle itself

The CBH skill bodies are released under MIT for the markdown
content and BSD-3-Clause for the Python scripts, unless individual
files state otherwise.

## Author note

CBH is an opinionated artifact. The "right" payload, the "right"
chain, and the "right" reporting voice are all judgment calls. The
maintainers' opinions are anchored in the corpus above; your
opinions may differ. The `CONTRIBUTING.md` process is the right
place to push back with evidence.
