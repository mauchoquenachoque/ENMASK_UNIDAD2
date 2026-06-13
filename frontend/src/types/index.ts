export type DatabaseType =
  | 'postgres'
  | 'mysql'
  | 'mongodb'
  | 'mariadb'
  | 'sqlite'
  | 'oracle'
  | 'sqlserver'
  | 'db2'
  | 'cassandra'
  | 'redis'
  | 'elasticsearch'
  | 'dynamodb'
  | 'cockroachdb'
  | 'clickhouse'
  | 'snowflake'
  | 'bigquery';

export type MaskingAlgorithm =
  | 'substitution'
  | 'hashing'
  | 'redaction'
  | 'nullification'
  | 'fpe'
  | 'perturbation'
  | 'shuffling'
  | 'truncation'
  | 'encoding'
  | 'tokenization'
  | 'generalization'
  | 'blurring';

export type DataType =
  | 'name'
  | 'email'
  | 'phone'
  | 'ssn'
  | 'credit_card'
  | 'address'
  | 'date_of_birth'
  | 'ip_address'
  | 'passport'
  | 'license_plate'
  | 'bank_account'
  | 'medical_record'
  | 'salary'
  | 'age'
  | 'custom';

export type ComplianceFramework =
  | 'gdpr'
  | 'hipaa'
  | 'pci_dss'
  | 'sox'
  | 'ccpa'
  | 'ferpa'
  | 'lgpd'
  | 'pipeda';

export type UserRole = 'admin' | 'analyst' | 'viewer' | 'operator';

export type JobStatus = 'pending' | 'running' | 'completed' | 'failed' | 'unmasked' | 'cancelled' | 'scheduled';

export type ConnectionStatus = 'connected' | 'disconnected' | 'error' | 'testing';

export type ScheduleFrequency = 'once' | 'hourly' | 'daily' | 'weekly' | 'monthly' | 'custom';

export type DiscoveryConfidence = 'high' | 'medium' | 'low';

export type ExportFormat = 'pdf' | 'excel' | 'csv' | 'json';

export interface User {
  id: string;
  email: string;
  name: string;
  picture?: string;
  role: UserRole;
  mfa_enabled: boolean;
  last_login: string | null;
  created_at: string;
}

export interface AuthResponse {
  access_token: string;
  refresh_token: string;
  token_type: string;
  expires_in: number;
  user: User;
}

export interface Connection {
  id: string;
  name: string;
  type: DatabaseType;
  host: string;
  port: number;
  database: string;
  username: string;
  status: ConnectionStatus;
  ssl_enabled: boolean;
  pool_size: number;
  last_tested: string | null;
  created_at: string;
  updated_at: string;
  created_by: string;
  metadata: Record<string, unknown>;
}

export interface ConnectionCreate {
  name: string;
  type: DatabaseType;
  host: string;
  port: number;
  database: string;
  username: string;
  password: string;
  ssl_enabled?: boolean;
  pool_size?: number;
  ssl_cert?: string;
  ssl_key?: string;
  ssl_ca?: string;
  connection_timeout?: number;
}

export interface ConnectionTestResult {
  success: boolean;
  message: string;
  latency_ms: number;
  server_version: string;
}

export interface MaskingRule {
  id: string;
  name: string;
  description: string;
  connection_id: string;
  target_table: string;
  target_column: string;
  data_type: DataType;
  algorithm: MaskingAlgorithm;
  algorithm_options: Record<string, unknown>;
  compliance_frameworks: ComplianceFramework[];
  priority: number;
  enabled: boolean;
  created_at: string;
  updated_at: string;
  created_by: string;
}

export interface RuleCreate {
  name: string;
  description?: string;
  connection_id: string;
  target_table: string;
  target_column: string;
  data_type?: DataType;
  algorithm: MaskingAlgorithm;
  algorithm_options?: Record<string, unknown>;
  compliance_frameworks?: ComplianceFramework[];
  priority?: number;
}

export interface MaskingJob {
  id: string;
  name: string;
  connection_id: string;
  rule_ids: string[];
  status: JobStatus;
  progress: number;
  started_at: string | null;
  completed_at: string | null;
  error_message: string | null;
  records_processed: number;
  records_total: number;
  duration_ms: number | null;
  owner_id: string;
  shared_with: string[];
  schedule_id: string | null;
  metadata: Record<string, unknown>;
  created_at: string;
}

export interface JobCreate {
  name?: string;
  connection_id: string;
  rule_ids: string[];
  schedule_id?: string;
}

export interface Summary {
  total_connections: number;
  total_rules: number;
  total_jobs: number;
  total_records_processed: number;
  active_jobs: number;
  failed_jobs: number;
  risk_score: number;
  compliance_coverage: Record<ComplianceFramework, number>;
  database_distribution: Record<DatabaseType, number>;
  recent_activity: ActivityEntry[];
}

export interface ActivityEntry {
  id: string;
  type: 'job_started' | 'job_completed' | 'job_failed' | 'connection_added' | 'rule_created' | 'user_login';
  message: string;
  timestamp: string;
  user_email: string;
  metadata: Record<string, unknown>;
}

export interface DynamicQueryResponse {
  data: Record<string, unknown>[];
  total_records: number;
  is_masked: boolean;
  columns: string[];
  query_time_ms: number;
}

export interface ShareJobRequest {
  email: string;
  permission: 'read' | 'write';
}

export interface AuditLogEntry {
  id: string;
  job_id: string;
  user_id: string;
  user_email: string;
  user_role: UserRole;
  action: string;
  is_masked: boolean;
  ip_address: string;
  user_agent: string;
  timestamp: string;
  details: Record<string, unknown>;
}

export interface PaginatedResponse<T> {
  items: T[];
  total: number;
  page: number;
  page_size: number;
  total_pages: number;
}

export interface PaginationParams {
  page?: number;
  page_size?: number;
  sort_by?: string;
  sort_order?: 'asc' | 'desc';
  search?: string;
}

export interface DiscoveryScan {
  id: string;
  connection_id: string;
  status: 'pending' | 'scanning' | 'completed' | 'failed';
  progress: number;
  columns_scanned: number;
  pii_found: number;
  started_at: string | null;
  completed_at: string | null;
  created_by: string;
}

export interface DiscoveryResult {
  id: string;
  scan_id: string;
  table_name: string;
  column_name: string;
  data_type: string;
  pii_type: DataType;
  confidence: DiscoveryConfidence;
  sample_values: string[];
  suggested_algorithm: MaskingAlgorithm;
  compliance_frameworks: ComplianceFramework[];
  rule_created: boolean;
}

export interface ScanConfig {
  connection_id: string;
  tables?: string[];
  exclude_tables?: string[];
  confidence_threshold?: number;
  sample_size?: number;
}

export interface Schedule {
  id: string;
  name: string;
  description: string;
  job_config: JobCreate;
  frequency: ScheduleFrequency;
  cron_expression: string | null;
  next_run: string | null;
  last_run: string | null;
  enabled: boolean;
  created_by: string;
  created_at: string;
  updated_at: string;
}

export interface ScheduleCreate {
  name: string;
  description?: string;
  job_config: JobCreate;
  frequency: ScheduleFrequency;
  cron_expression?: string;
  enabled?: boolean;
}

export interface ScheduleHistory {
  id: string;
  schedule_id: string;
  job_id: string;
  status: JobStatus;
  started_at: string;
  completed_at: string | null;
  error_message: string | null;
}

export interface Plugin {
  id: string;
  name: string;
  version: string;
  description: string;
  type: 'algorithm' | 'connector' | 'export' | 'notification';
  enabled: boolean;
  config: Record<string, unknown>;
  installed_at: string;
}

export interface ApiKey {
  id: string;
  name: string;
  key_prefix: string;
  scopes: string[];
  expires_at: string | null;
  last_used: string | null;
  created_at: string;
}

export interface NotificationPreference {
  email_on_job_complete: boolean;
  email_on_job_fail: boolean;
  email_on_scan_complete: boolean;
  slack_webhook: string | null;
  teams_webhook: string | null;
}

export interface ComplianceReport {
  id: string;
  framework: ComplianceFramework;
  generated_at: string;
  total_tables: number;
  covered_tables: number;
  coverage_percentage: number;
  risk_items: RiskItem[];
  recommendations: string[];
}

export interface RiskItem {
  table: string;
  column: string;
  pii_type: DataType;
  risk_level: 'critical' | 'high' | 'medium' | 'low';
  status: 'masked' | 'unmasked' | 'partial';
  recommendation: string;
}

export interface ApiError {
  status: number;
  message: string;
  detail: string | Record<string, unknown>[];
  timestamp: string;
}

export const DATABASE_TYPES: { value: DatabaseType; label: string; defaultPort: number }[] = [
  { value: 'postgres', label: 'PostgreSQL', defaultPort: 5432 },
  { value: 'mysql', label: 'MySQL', defaultPort: 3306 },
  { value: 'mariadb', label: 'MariaDB', defaultPort: 3306 },
  { value: 'mongodb', label: 'MongoDB', defaultPort: 27017 },
  { value: 'sqlite', label: 'SQLite', defaultPort: 0 },
  { value: 'oracle', label: 'Oracle', defaultPort: 1521 },
  { value: 'sqlserver', label: 'SQL Server', defaultPort: 1433 },
  { value: 'db2', label: 'IBM DB2', defaultPort: 50000 },
  { value: 'cassandra', label: 'Apache Cassandra', defaultPort: 9042 },
  { value: 'redis', label: 'Redis', defaultPort: 6379 },
  { value: 'elasticsearch', label: 'Elasticsearch', defaultPort: 9200 },
  { value: 'dynamodb', label: 'Amazon DynamoDB', defaultPort: 8000 },
  { value: 'cockroachdb', label: 'CockroachDB', defaultPort: 26257 },
  { value: 'clickhouse', label: 'ClickHouse', defaultPort: 8123 },
  { value: 'snowflake', label: 'Snowflake', defaultPort: 443 },
  { value: 'bigquery', label: 'Google BigQuery', defaultPort: 443 },
];

export const MASKING_ALGORITHMS: { value: MaskingAlgorithm; label: string; description: string }[] = [
  { value: 'substitution', label: 'Substitution', description: 'Replace with realistic fake data' },
  { value: 'hashing', label: 'Hashing (SHA-256)', description: 'One-way hash with optional salt' },
  { value: 'redaction', label: 'Redaction', description: 'Replace with fixed characters (e.g. ***)' },
  { value: 'nullification', label: 'Nullification', description: 'Replace with NULL' },
  { value: 'fpe', label: 'Format-Preserving Encryption', description: 'Encrypt while preserving format' },
  { value: 'perturbation', label: 'Data Perturbation', description: 'Add variance to numeric/date values' },
  { value: 'shuffling', label: 'Shuffling', description: 'Randomly reorder values within column' },
  { value: 'truncation', label: 'Truncation', description: 'Truncate to partial value' },
  { value: 'encoding', label: 'Encoding', description: 'Base64 or hex encoding' },
  { value: 'tokenization', label: 'Tokenization', description: 'Replace with reversible token' },
  { value: 'generalization', label: 'Generalization', description: 'Replace with broader category' },
  { value: 'blurring', label: 'Blurring', description: 'Reduce precision of values' },
];

export const DATA_TYPES: { value: DataType; label: string }[] = [
  { value: 'name', label: 'Full Name' },
  { value: 'email', label: 'Email Address' },
  { value: 'phone', label: 'Phone Number' },
  { value: 'ssn', label: 'Social Security Number' },
  { value: 'credit_card', label: 'Credit Card Number' },
  { value: 'address', label: 'Street Address' },
  { value: 'date_of_birth', label: 'Date of Birth' },
  { value: 'ip_address', label: 'IP Address' },
  { value: 'passport', label: 'Passport Number' },
  { value: 'license_plate', label: 'License Plate' },
  { value: 'bank_account', label: 'Bank Account' },
  { value: 'medical_record', label: 'Medical Record' },
  { value: 'salary', label: 'Salary' },
  { value: 'age', label: 'Age' },
  { value: 'custom', label: 'Custom' },
];

export const COMPLIANCE_FRAMEWORKS: { value: ComplianceFramework; label: string; description: string }[] = [
  { value: 'gdpr', label: 'GDPR', description: 'EU General Data Protection Regulation' },
  { value: 'hipaa', label: 'HIPAA', description: 'US Health Insurance Portability and Accountability Act' },
  { value: 'pci_dss', label: 'PCI DSS', description: 'Payment Card Industry Data Security Standard' },
  { value: 'sox', label: 'SOX', description: 'Sarbanes-Oxley Act' },
  { value: 'ccpa', label: 'CCPA', description: 'California Consumer Privacy Act' },
  { value: 'ferpa', label: 'FERPA', description: 'Family Educational Rights and Privacy Act' },
  { value: 'lgpd', label: 'LGPD', description: 'Brazilian General Data Protection Law' },
  { value: 'pipeda', label: 'PIPEDA', description: 'Canadian Personal Information Protection Act' },
];

export const USER_ROLES: { value: UserRole; label: string; description: string }[] = [
  { value: 'admin', label: 'Administrator', description: 'Full system access' },
  { value: 'analyst', label: 'Analyst', description: 'Create and manage masking jobs' },
  { value: 'operator', label: 'Operator', description: 'Run and monitor jobs' },
  { value: 'viewer', label: 'Viewer', description: 'Read-only access' },
];

export const PERMISSIONS: Record<UserRole, string[]> = {
  admin: ['*'],
  analyst: [
    'connections:read', 'connections:create', 'connections:update',
    'rules:read', 'rules:create', 'rules:update', 'rules:delete',
    'jobs:read', 'jobs:create', 'jobs:run', 'jobs:share',
    'discovery:read', 'discovery:run',
    'reports:read', 'reports:export',
    'schedules:read', 'schedules:create', 'schedules:update',
  ],
  operator: [
    'connections:read',
    'rules:read',
    'jobs:read', 'jobs:run',
    'discovery:read',
    'reports:read',
  ],
  viewer: [
    'connections:read',
    'rules:read',
    'jobs:read',
    'reports:read',
  ],
};
