# Phase 2j — Cloud + LocalStack SSRF → IMDS → S3

## What this exercises

- `hunt-ssrf` — IMDSv1 metadata abuse
- `m365-entra-attack` / `enterprise-vpn-attack` (loosely)
- `payload-discipline` — read-only S3 demonstration

## Components

- A Flask app with a "url fetch" endpoint (the SSRF vector)
- LocalStack simulating AWS IAM, EC2 metadata, S3
- A pre-seeded "company secrets" S3 bucket

## docker-compose.yml

```yaml
version: "3.8"
services:
  app:
    build: ./app
    ports: ["127.0.0.1:5000:5000"]
    environment:
      - AWS_ACCESS_KEY_ID=test
      - AWS_SECRET_ACCESS_KEY=test
      - AWS_ENDPOINT_URL=http://localstack:4566
    depends_on: [localstack]
  localstack:
    image: localstack/localstack:3
    environment:
      - SERVICES=s3,iam,ec2
      - DEBUG=0
    ports: ["127.0.0.1:4566:4566"]
    volumes:
      - "./init:/etc/localstack/init/ready.d"
  metadata:
    # simple IMDS emulator
    build: ./metadata
    expose: ["169.254.169.254:80"]
    networks:
      lab:
        ipv4_address: 169.254.169.254
```

(Exact network setup varies by Docker version; full compose in the
lab folder.)

## Walk-through

1. Probe app's URL-fetch endpoint with a Burp Collaborator URL
2. Confirm server-side fetch
3. Fetch IMDSv1: `http://169.254.169.254/latest/meta-data/iam/security-credentials/<role>`
4. Use returned creds to `aws s3 ls`
5. Demonstrate **read** of a single object — no enumeration
6. Stop. PoC complete.

## Files

- `app/app.py` (Flask url-fetch app)
- `metadata/server.py` (IMDS emulator)
- `init/seed.sh` (creates the S3 bucket + object)
- `exploits/full-chain.sh`

## Discipline note

Even in lab, the walkthrough demonstrates **only the read** that
proves impact. Production engagements should do the same.

## See also

- `skills/hunt-ssrf/SKILL.md`
- `skills/offensive-osint/references/cloud-recon.md`
- `skills/payload-discipline/SKILL.md`
