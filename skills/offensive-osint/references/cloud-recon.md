# Cloud Recon

## S3 (AWS)

Common bucket name patterns:

```
<target>
<target>-prod
<target>-staging
<target>-dev
<target>-backup
<target>-assets
<target>-static
<target>-cdn
<target>-uploads
<target>-logs
backup.<target>.com   (CNAME-routed)
files.<target>.com
```

Enumeration:

```bash
cloud_enum -k <target> -k <target>-prod
s3scanner scan -f buckets.txt
gobuster s3 -w bucketnames.txt
```

Permission check (without credentials):

```bash
aws s3 ls s3://<bucket> --no-sign-request
aws s3api get-bucket-acl --bucket <bucket> --no-sign-request
aws s3api get-bucket-policy --bucket <bucket> --no-sign-request
```

Findings:
- Public READ → list/read objects
- Public WRITE → upload object (massive impact)
- Public ACL → ACL listed (lesser)

## GCS (Google Cloud Storage)

```
gsutil ls gs://<bucket>     # if SDK installed
curl https://storage.googleapis.com/<bucket>/
```

Bucket naming: same patterns.

## Azure Blob

```
https://<account>.blob.core.windows.net/?comp=list
https://<account>.blob.core.windows.net/<container>?restype=container&comp=list
```

`account` names are global → enumeration sometimes finds tenants
indirectly.

## Cloud metadata (SSRF leverage)

Covered in `hunt-ssrf`. Repeated here for ease:

```
AWS:   http://169.254.169.254/latest/meta-data/
GCP:   http://metadata.google.internal/computeMetadata/v1/  (header: Metadata-Flavor: Google)
Azure: http://169.254.169.254/metadata/identity/oauth2/token  (header: Metadata: true)
DO:    http://169.254.169.254/metadata/v1/
```

## See also

- `dork-corpus.md` — cloud-specific search dorks
- `surface-mapping` — bucket findings flow into the asset ranking
