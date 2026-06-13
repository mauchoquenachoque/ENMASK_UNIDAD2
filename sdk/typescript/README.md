# Enmask TypeScript SDK

Official TypeScript client for the Enmask Data Masking Platform.

## Installation

```bash
npm install @enmask/sdk
```

## Quick Start

```typescript
import { EnmaskClient } from "@enmask/sdk";

const client = new EnmaskClient("https://api.enmask.io", "your-api-key");
const connections = await client.listConnections();
connections.forEach((c) => console.log(c.name, c.db_type));
```

## Authentication

### Email/Password

```typescript
const client = new EnmaskClient("https://api.enmask.io");
const auth = await client.login("user@example.com", "password");
console.log(auth.access_token);
```

### Google OAuth

```typescript
const auth = await client.loginGoogle("google-id-token");
```

### API Key

```typescript
const client = new EnmaskClient("https://api.enmask.io", "your-api-key");
```

### Bearer Token

```typescript
const client = new EnmaskClient("https://api.enmask.io", undefined, "your-jwt-token");
```

## Connections

```typescript
const conn = await client.createConnection({
  name: "Production DB",
  db_type: "postgresql",
  host: "db.example.com",
  port: 5432,
  database: "mydb",
  username: "user",
  password: "pass",
});

const success = await client.testConnection(conn.id);
const pii = await client.discoverPii(conn.id);

await client.deleteConnection(conn.id);
```

## Masking Rules

```typescript
const rule = await client.createRule({
  name: "Mask Emails",
  strategy: "partial_mask",
  target_tables: ["users"],
  target_columns: ["email"],
  parameters: { mask_char: "*", visible_chars: 3 },
});

const updated = await client.updateRule(rule.id, { priority: 10 });
await client.deleteRule(rule.id);
```

## Masking Jobs

```typescript
const job = await client.createJob({
  name: "Mask Production Data",
  connection_id: conn.id,
  rule_ids: [rule.id],
});

await client.runJob(job.id);
const status = await client.getJobStatus(job.id);
console.log(status.status, status.progress);

await client.shareJob(job.id, "colleague@example.com");
await client.unmaskJob(job.id);
```

## Reports

```typescript
const summary = await client.getSummary();
console.log(summary.total_records_masked);

const report = await client.getComplianceReport("GDPR");
console.log(report.score);
```

## PII Discovery

```typescript
const scan = await client.scanDatabase(conn.id);
const results = await client.getScanResults(scan.id);
results.detections.forEach((d) => {
  console.log(`${d.table}.${d.column}: ${d.pii_type}`);
});
```

## Error Handling

```typescript
import { EnmaskClient, AuthenticationError, NotFoundError } from "@enmask/sdk";

try {
  await client.login("bad@email.com", "wrong");
} catch (e) {
  if (e instanceof AuthenticationError) {
    console.log(`Auth failed: ${e.message}`);
  } else if (e instanceof NotFoundError) {
    console.log(`Not found: ${e.message}`);
  }
}
```

## Enums

```typescript
import { MaskingStrategy, DatabaseType, JobStatus } from "@enmask/sdk";

await client.createRule({
  name: "Hash SSN",
  strategy: MaskingStrategy.HASH,
  target_columns: ["ssn"],
});
```

## License

MIT
