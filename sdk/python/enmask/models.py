from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


class DatabaseType(str, Enum):
    POSTGRESQL = "postgresql"
    MYSQL = "mysql"
    MONGODB = "mongodb"
    SQLITE = "sqlite"
    ORACLE = "oracle"
    SQLSERVER = "sqlserver"
    MARIADB = "mariadb"
    REDIS = "redis"
    ELASTICSEARCH = "elasticsearch"
    CASSANDRA = "cassandra"
    DYNAMODB = "dynamodb"
    FIREBASE = "firebase"
    COCKROACHDB = "cockroachdb"
    TIDB = "tidb"
    CLICKHOUSE = "clickhouse"
    NEON = "neon"


class MaskingStrategy(str, Enum):
    MASK = "mask"
    HASH = "hash"
    TOKENIZE = "tokenize"
    ENCRYPT = "encrypt"
    REDACT = "redact"
    SHUFFLE = "shuffle"
    NULLIFY = "nullify"
    SUBSTITUTE = "substitute"
    BLUR = "blur"
    GENERALIZE = "generalize"
    DATE_SHIFT = "date_shift"
    NUMERIC_NOISE = "numeric_noise"
    FAKE = "fake"
    PARTIAL_MASK = "partial_mask"
    REVERSIBLE = "reversible"
    FORMAT_PRESERVING = "format_preserving"
    TRUNCATE = "truncate"
    ENCODE = "encode"
    CUSTOM = "custom"
    CONDITIONAL = "conditional"
    CASCADING = "cascading"
    CONTEXT_AWARE = "context_aware"
    DETERMINISTIC = "deterministic"


class JobStatus(str, Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"
    PAUSED = "paused"


class ConnectionStatus(str, Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"
    ERROR = "error"
    TESTING = "testing"


class AuthResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    expires_in: int
    user_id: str
    email: str
    role: str
    permissions: List[str] = Field(default_factory=list)


class Connection(BaseModel):
    id: str
    name: str
    db_type: DatabaseType
    host: str
    port: int
    database: str
    username: str
    status: ConnectionStatus = ConnectionStatus.ACTIVE
    created_at: datetime
    updated_at: Optional[datetime] = None
    last_tested: Optional[datetime] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)


class ColumnInfo(BaseModel):
    name: str
    data_type: str
    nullable: bool = False
    is_primary_key: bool = False
    is_foreign_key: bool = False
    pii_detected: bool = False
    pii_type: Optional[str] = None
    confidence: float = 0.0


class TableInfo(BaseModel):
    name: str
    schema: str = "public"
    row_count: int = 0
    columns: List[ColumnInfo] = Field(default_factory=list)


class MaskingRule(BaseModel):
    id: str
    name: str
    strategy: MaskingStrategy
    target_columns: List[str] = Field(default_factory=list)
    target_tables: List[str] = Field(default_factory=list)
    parameters: Dict[str, Any] = Field(default_factory=dict)
    priority: int = 0
    enabled: bool = True
    created_at: datetime
    updated_at: Optional[datetime] = None
    created_by: Optional[str] = None


class MaskingJob(BaseModel):
    id: str
    name: str
    connection_id: str
    rule_ids: List[str] = Field(default_factory=list)
    status: JobStatus = JobStatus.PENDING
    progress: float = 0.0
    total_records: int = 0
    processed_records: int = 0
    error_message: Optional[str] = None
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    created_at: datetime
    created_by: Optional[str] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)


class PIIDetection(BaseModel):
    column: str
    table: str
    pii_type: str
    confidence: float
    sample_values: List[str] = Field(default_factory=list)
    recommendation: Optional[str] = None


class ScanResult(BaseModel):
    id: str
    connection_id: str
    status: str
    tables_scanned: int = 0
    columns_scanned: int = 0
    pii_found: int = 0
    detections: List[PIIDetection] = Field(default_factory=list)
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None


class ComplianceReport(BaseModel):
    framework: str
    total_checks: int = 0
    passed_checks: int = 0
    failed_checks: int = 0
    score: float = 0.0
    findings: List[Dict[str, Any]] = Field(default_factory=list)
    recommendations: List[str] = Field(default_factory=list)
    generated_at: datetime


class SummaryReport(BaseModel):
    total_connections: int = 0
    total_rules: int = 0
    total_jobs: int = 0
    completed_jobs: int = 0
    failed_jobs: int = 0
    total_records_masked: int = 0
    pii_columns_detected: int = 0
    compliance_score: float = 0.0
    recent_activity: List[Dict[str, Any]] = Field(default_factory=list)
