# Secret Validators

For each secret class in `secret-patterns.md`, a one-liner that
confirms the key is live with the **smallest** possible side effect.

## Discipline

Validators are **read-only** wherever possible. Never use a found
key to enumerate, exfiltrate, or modify. The single validator call
proves liveness; that's enough for a bug-bounty submission.

## Stripe

```bash
curl -s -u "$KEY:" https://api.stripe.com/v1/account | jq -r '.id // .error.message'
# Live → returns acct_... ; revoked → "Invalid API Key provided"
```

## AWS

```bash
AWS_ACCESS_KEY_ID=$KEY AWS_SECRET_ACCESS_KEY=$SECRET \
  aws sts get-caller-identity --output json
# Live → returns {"UserId","Account","Arn"}
```

## GCP API key

```bash
curl -s "https://www.googleapis.com/youtube/v3/search?part=snippet&q=test&key=$KEY" | jq '.error.message // .kind'
# Live → returns search items; revoked → "API key not valid"
```

## GCP Service Account JSON

```bash
gcloud auth activate-service-account --key-file=/tmp/sa.json
gcloud projects list
```

## Azure Storage SAS

```bash
curl -s "https://$ACCOUNT.blob.core.windows.net/?$SAS" | head -c 200
# Live → XML container list; revoked → 403/AuthenticationFailed
```

## Twilio

```bash
curl -s -u "$SID:$TOKEN" "https://api.twilio.com/2010-04-01/Accounts/$SID.json" | jq -r '.friendly_name // .message'
```

## SendGrid

```bash
curl -s -H "Authorization: Bearer $KEY" https://api.sendgrid.com/v3/user/account | jq -r '.type // .errors[0].message'
```

## Slack

```bash
curl -s -X POST -H "Authorization: Bearer $TOKEN" https://slack.com/api/auth.test | jq -r '.ok, .user, .error'
```

## Slack Webhook

```bash
curl -s -X POST "$WEBHOOK_URL" -H 'Content-type: application/json' --data '{"text":"bug-bounty validation"}'
# Live → "ok" ; revoked → "invalid_token"
# WARNING: this posts a message. Coordinate with the program before sending.
```

## GitHub PAT

```bash
curl -s -H "Authorization: token $PAT" https://api.github.com/user | jq -r '.login // .message'
```

## GitLab PAT

```bash
curl -s -H "PRIVATE-TOKEN: $PAT" https://gitlab.com/api/v4/user | jq -r '.username // .message'
```

## NPM

```bash
curl -s -H "Authorization: Bearer $TOKEN" https://registry.npmjs.org/-/whoami | jq -r '.username // .error'
```

## OpenAI

```bash
curl -s -H "Authorization: Bearer $KEY" https://api.openai.com/v1/models | jq -r '.data[0].id // .error.message'
```

## Anthropic

```bash
curl -s -X POST https://api.anthropic.com/v1/messages \
  -H "x-api-key: $KEY" \
  -H "anthropic-version: 2023-06-01" \
  -H "content-type: application/json" \
  -d '{"model":"claude-haiku-4-5","max_tokens":1,"messages":[{"role":"user","content":"x"}]}' \
  | jq -r '.id // .error.message'
```

## Hugging Face

```bash
curl -s -H "Authorization: Bearer $HF_TOKEN" https://huggingface.co/api/whoami-v2 | jq -r '.name // .error'
```

## Mailgun

```bash
curl -s --user "api:$KEY" "https://api.mailgun.net/v3/domains" | jq -r '.items[0].name // .message'
```

## Mapbox

```bash
curl -s "https://api.mapbox.com/tokens/v2?access_token=$TOKEN" | jq -r '.[0].id // .message'
```

## Telegram Bot

```bash
curl -s "https://api.telegram.org/bot${BOT_TOKEN}/getMe" | jq -r '.result.username // .description'
```

## Discord Bot

```bash
curl -s -H "Authorization: Bot $TOKEN" https://discord.com/api/v10/users/@me | jq -r '.username // .message'
```

## Discord Webhook

```bash
curl -s "${WEBHOOK_URL}" | jq -r '.name // .message'
# This is a GET — no message posted.
```

## DigitalOcean PAT

```bash
curl -s -H "Authorization: Bearer $PAT" https://api.digitalocean.com/v2/account | jq -r '.account.email // .id'
```

## Cloudflare

```bash
curl -s -H "Authorization: Bearer $TOKEN" https://api.cloudflare.com/client/v4/user/tokens/verify | jq -r '.success'
```

## Notion

```bash
curl -s -H "Authorization: Bearer $TOKEN" -H "Notion-Version: 2022-06-28" https://api.notion.com/v1/users/me | jq -r '.name // .message'
```

## Linear

```bash
curl -s -X POST -H "Authorization: $KEY" -H "Content-Type: application/json" -d '{"query":"{viewer{id email}}"}' https://api.linear.app/graphql | jq -r '.data.viewer.email // .errors[0].message'
```

## Atlassian / Jira API

```bash
curl -s -u "$EMAIL:$TOKEN" "https://${TENANT}.atlassian.net/rest/api/3/myself" | jq -r '.emailAddress // .message'
```

## Sentry DSN

```bash
# Send a single empty event to verify
curl -s -X POST "$DSN_URL" -H "Content-Type: application/json" -d '{"message":"validation"}'
# This DOES log an event. Coordinate first.
```

## Square

```bash
curl -s -H "Authorization: Bearer $TOKEN" -H "Square-Version: 2024-01-18" https://connect.squareup.com/v2/locations | jq -r '.locations[0].name // .errors[0].detail'
```

## Default — generic

If the key class is unknown:

1. Decode if JWT-shaped (look at `iss`, `aud`)
2. Search the key prefix on `https://api.<provider>.com/...`
3. Try a documented "whoami"-style endpoint
4. **Don't** spray endpoints randomly

## Reporting note

In bug-bounty reports, include:

- Class of key (Stripe, AWS, etc.)
- Last 4 chars only
- Validator output (redact org/email if PII)
- Source file path + commit SHA

Example body in report:

> A live Stripe restricted key was discovered hardcoded in
> `dist/app.bundle.js` at line 12378 (SHA-256
> `abcd...`). Validation confirmed the key is active and bound to
> account `acct_***********xyz` (validator command in
> `evidence/secret-validation.txt`).

## See also

- `secret-patterns.md`
- `scripts/secret_scan.py`
- `evidence-hygiene` skill
