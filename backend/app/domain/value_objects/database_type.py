from enum import Enum


class DatabaseType(str, Enum):
    POSTGRES = "postgres"
    MYSQL = "mysql"
    MARIADB = "mariadb"
    SQLSERVER = "sqlserver"
    ORACLE = "oracle"
    SQLITE = "sqlite"
    MONGODB = "mongodb"
    CASSANDRA = "cassandra"
    REDIS = "redis"
    COUCHDB = "couchdb"
    DYNAMODB = "dynamodb"
    ELASTICSEARCH = "elasticsearch"
    SNOWFLAKE = "snowflake"
    BIGQUERY = "bigquery"
    REDSHIFT = "redshift"
    AZURE_SYNAPSE = "azure_synapse"
