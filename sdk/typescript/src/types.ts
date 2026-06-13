export enum DatabaseType {
  POSTGRESQL = "postgresql",
  MYSQL = "mysql",
  MONGODB = "mongodb",
  SQLITE = "sqlite",
  ORACLE = "oracle",
  SQLSERVER = "sqlserver",
  MARIADB = "mariadb",
  REDIS = "redis",
  ELASTICSEARCH = "elasticsearch",
  CASSANDRA = "cassandra",
  DYNAMODB = "dynamodb",
  FIREBASE = "firebase",
  COCKROACHDB = "cockroachdb",
  TIDB = "tidb",
  CLICKHOUSE = "clickhouse",
  NEON = "neon",
}

export enum MaskingStrategy {
  MASK = "mask",
  HASH = "hash",
  TOKENIZE = "tokenize",
  ENCRYPT = "encrypt",
  REDACT = "redact",
  SHUFFLE = "shuffle",
  NULLIFY = "nullify",
  SUBSTITUTE = "substitute",
  BLUR = "blur",
  GENERALIZE = "generalize",
  DATE_SHIFT = "date_shift",
  NUMERIC_NOISE = "numeric_noise",
  FAKE = "fake",
  PARTIAL_MASK = "partial_mask",
  REVERSIBLE = "reversible",
  FORMAT_PRESERVING = "format_preserving",
  TRUNCATE = "truncate",
  ENCODE = "encode",
  CUSTOM = "custom",
  CONDITIONAL = "conditional",
  CASCADING = "cascading",
  CONTEXT_AWARE = "context_aware",
  DETERMINISTIC = "deterministic",
}

export enum JobStatus {
  PENDING = "pending",
  RUNNING = "running",
  COMPLETED = "completed",
  FAILED = "failed",
  CANCELLED = "cancelled",
  PAUSED = "paused",
}

export enum ConnectionStatus {
  ACTIVE = "active",
  INACTIVE = "inactive",
  ERROR = "error",
  TESTING = "testing",
}

export interface AuthResponse {
  access_token: string;
  token_type: string;
  expires_in: number;
  user_id: string;
  email: string;
  role: string;
  permissions: string[];
}

export interface Connection {
  id: string;
  name: string;
  db_type: DatabaseType;
  host: string;
  port: number;
  database: string;
  username: string;
  status: ConnectionStatus;
  created_at: string;
  updated_at?: string;
  last_tested?: string;
  metadata: Record<string, unknown>;
}

export interface ColumnInfo {
  name: string;
  data_type: string;
  nullable: boolean;
  is_primary_key: boolean;
  is_foreign_key: boolean;
  pii_detected: boolean;
  pii_type?: string;
  confidence: number;
}

export interface TableInfo {
  name: string;
  schema: string;
  row_count: number;
  columns: ColumnInfo[];
}

export interface MaskingRule {
  id: string;
  name: string;
  strategy: MaskingStrategy;
  target_columns: string[];
  target_tables: string[];
  parameters: Record<string, unknown>;
  priority: number;
  enabled: boolean;
  created_at: string;
  updated_at?: string;
  created_by?: string;
}

export interface MaskingJob {
  id: string;
  name: string;
  connection_id: string;
  rule_ids: string[];
  status: JobStatus;
  progress: number;
  total_records: number;
  processed_records: number;
  error_message?: string;
  started_at?: string;
  completed_at?: string;
  created_at: string;
  created_by?: string;
  metadata: Record<string, unknown>;
}

export interface PIIDetection {
  column: string;
  table: string;
  pii_type: string;
  confidence: number;
  sample_values: string[];
  recommendation?: string;
}

export interface ScanResult {
  id: string;
  connection_id: string;
  status: string;
  tables_scanned: number;
  columns_scanned: number;
  pii_found: number;
  detections: PIIDetection[];
  started_at?: string;
  completed_at?: string;
}

export interface ComplianceReport {
  framework: string;
  total_checks: number;
  passed_checks: number;
  failed_checks: number;
  score: number;
  findings: Record<string, unknown>[];
  recommendations: string[];
  generated_at: string;
}

export interface SummaryReport {
  total_connections: number;
  total_rules: number;
  total_jobs: number;
  completed_jobs: number;
  failed_jobs: number;
  total_records_masked: number;
  pii_columns_detected: number;
  compliance_score: number;
  recent_activity: Record<string, unknown>[];
}
