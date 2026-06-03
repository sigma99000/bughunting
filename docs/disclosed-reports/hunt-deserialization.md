# Deserialization — Disclosed Pattern Survey

26 disclosed reports + landmark CVE corpus.

## Format frequency

| Format | Frequency |
|---|---|
| Java `ObjectInputStream` (`aced 0005`) | 35% |
| .NET BinaryFormatter / ViewState | 18% |
| Python pickle | 15% |
| PHP serialize / phar | 14% |
| Ruby Marshal | 9% |
| Node.js (`serialize-javascript`) | 5% |
| YAML deserialization (PyYAML `yaml.load`) | 4% |

## Landmark CVEs

- CVE-2015-7501 (Commons Collections) — defining Java deser bug
- CVE-2017-9805 (Struts2 REST) — XML deser via XStream
- CVE-2017-12149 (JBoss HTTP Invoker) — readObject pre-auth
- CVE-2018-2628 (WebLogic T3) — T3 protocol deser
- CVE-2019-2725 (WebLogic) — XML deser via wls-wsat
- CVE-2021-44521 (Cassandra) — Java UDF via Nashorn deser
- CVE-2023-22518 (Confluence) — auth + deser chain
- CVE-2025-23006 (SonicWall SMA1000) — pre-auth deser → RCE

## See also

- `skills/hunt-deserialization/SKILL.md`
- `skills/sharepoint-attack/SKILL.md` (ViewState)
