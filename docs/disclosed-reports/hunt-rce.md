# RCE — Disclosed Pattern Survey

64 disclosed reports + landmark CVE corpus.

## Entry-class frequency

| Entry | Frequency |
|---|---|
| SSTI (Jinja, Twig, Freemarker, Velocity, ERB) | 22% |
| Deserialization (Java, .NET, Python, Ruby, PHP) | 20% |
| Command injection (shell metachar) | 17% |
| File upload + handler enabling | 14% |
| Path traversal write + executable target | 8% |
| SQL injection → `xp_cmdshell` / `COPY FROM PROGRAM` | 6% |
| Prototype pollution → gadget | 5% |
| SSRF → Redis cron | 5% |
| Other | 3% |

## Landmark CVEs

| CVE | Year | Vector |
|---|---|---|
| CVE-2014-6271 (Shellshock) | 2014 | env var → bash |
| CVE-2017-5638 (Struts2) | 2017 | OGNL via Content-Type |
| CVE-2021-44228 (log4shell) | 2021 | JNDI lookup in log line |
| CVE-2022-22965 (Spring4Shell) | 2022 | Class.module → property binding |
| CVE-2024-23897 (Jenkins CLI) | 2024 | args expansion + file read |
| CVE-2024-27198 (TeamCity) | 2024 | Auth bypass + RCE |
| CVE-2025-31324 (SAP NetWeaver) | 2025 | Unrestricted file upload |
| CVE-2025-53770 / 53771 (SharePoint ToolShell) | 2025 | Deser + machineKey |

## See also

- `skills/hunt-rce/SKILL.md` parent
- `skills/hunt-ssti/SKILL.md`, `skills/hunt-deserialization/SKILL.md`,
  `skills/hunt-cmdi/SKILL.md`, `skills/hunt-file-upload/SKILL.md`,
  `skills/hunt-path-traversal/SKILL.md`, `skills/hunt-sqli/SKILL.md`
