# Enmask Python SDK

Official Python client for the Enmask Data Masking Platform.

## Installation

```bash
pip install enmask-sdk
```

## Quick Start

```python
from enmask import EnmaskClient

with EnmaskClient("https://api.enmask.io", api_key="your-key") as client:
    connections = client.list_connections()
    for conn in connections:
        print(conn.name, conn.db_type)
```

## Authentication

### Email/Password

```python
client = EnmaskClient("https://api.enmask.io")
auth = client.login("user@example.com", "password")
print(auth.access_token)
```

### Google OAuth

```python
auth = client.login_google("google-id-token")
```

### API Key

```python
client = EnmaskClient("https://api.enmask.io", api_key="your-api-key")
```

### Bearer Token

```python
client = EnmaskClient("https://api.enmask.io", token="your-jwt-token")
```

## Connections

```python
conn = client.create_connection({
    "name": "Production DB",
    "db_type": "postgresql",
    "host": "db.example.com",
    "port": 5432,
    "database": "mydb",
    "username": "user",
    "password": "pass"
})

success = client.test_connection(conn.id)
pii = client.discover_pii(conn.id)

client.delete_connection(conn.id)
```

## Masking Rules

```python
rule = client.create_rule({
    "name": "Mask Emails",
    "strategy": "partial_mask",
    "target_tables": ["users"],
    "target_columns": ["email"],
    "parameters": {"mask_char": "*", "visible_chars": 3}
})

updated = client.update_rule(rule.id, {"priority": 10})
client.delete_rule(rule.id)
```

## Masking Jobs

```python
job = client.create_job({
    "name": "Mask Production Data",
    "connection_id": conn.id,
    "rule_ids": [rule.id]
})

client.run_job(job.id)
status = client.get_job_status(job.id)
print(status.status, status.progress)

client.share_job(job.id, "colleague@example.com")
client.unmask_job(job.id)
```

## Reports

```python
summary = client.get_summary()
print(summary.total_records_masked)

report = client.get_compliance_report("GDPR")
print(report.score)
```

## PII Discovery

```python
scan = client.scan_database(conn.id)
results = client.get_scan_results(scan.id)
for detection in results.detections:
    print(f"{detection.table}.{detection.column}: {detection.pii_type}")
```

## Error Handling

```python
from enmask import EnmaskClient, AuthenticationError, NotFoundError

try:
    client.login("bad@email.com", "wrong")
except AuthenticationError as e:
    print(f"Auth failed: {e}")
except NotFoundError as e:
    print(f"Not found: {e}")
```

## Models

All responses are Pydantic models:

```python
from enmask.models import MaskingStrategy, DatabaseType, JobStatus

client.create_rule({
    "name": "Hash SSN",
    "strategy": MaskingStrategy.HASH,
    "target_columns": ["ssn"],
})
```

## License

MIT
