from __future__ import annotations

from typing import Any, Dict, Type, Union

from app.core.exceptions import EnmaskException
from app.core.logging import logger
from app.domain.entities.connection import ConnectionConfig
from app.domain.interfaces.connector import DatabaseConnector
from app.domain.value_objects.database_type import DatabaseType


class ConnectorFactoryError(EnmaskException):
    pass


_REGISTRY: Dict[DatabaseType, str] = {
    DatabaseType.POSTGRES: "app.infrastructure.connectors.postgres_connector.PostgresConnector",
    DatabaseType.MYSQL: "app.infrastructure.connectors.mysql_connector.MySQLConnector",
    DatabaseType.MARIADB: "app.infrastructure.connectors.mysql_connector.MySQLConnector",
    DatabaseType.MONGODB: "app.infrastructure.connectors.mongodb_connector.MongoDBConnector",
    DatabaseType.SQLSERVER: "app.infrastructure.connectors.sqlserver_connector.SQLServerConnector",
    DatabaseType.ORACLE: "app.infrastructure.connectors.oracle_connector.OracleConnector",
    DatabaseType.SQLITE: "app.infrastructure.connectors.sqlite_connector.SQLiteConnector",
    DatabaseType.CASSANDRA: "app.infrastructure.connectors.cassandra_connector.CassandraConnector",
    DatabaseType.REDIS: "app.infrastructure.connectors.redis_connector.RedisConnector",
    DatabaseType.ELASTICSEARCH: "app.infrastructure.connectors.elasticsearch_connector.ElasticsearchConnector",
    DatabaseType.DYNAMODB: "app.infrastructure.connectors.dynamodb_connector.DynamoDBConnector",
    DatabaseType.SNOWFLAKE: "app.infrastructure.connectors.snowflake_connector.SnowflakeConnector",
    DatabaseType.BIGQUERY: "app.infrastructure.connectors.bigquery_connector.BigQueryConnector",
    DatabaseType.REDSHIFT: "app.infrastructure.connectors.redshift_connector.RedshiftConnector",
    DatabaseType.COUCHDB: "app.infrastructure.connectors.couchdb_connector.CouchDBConnector",
    DatabaseType.AZURE_SYNAPSE: "app.infrastructure.connectors.azure_synapse_connector.AzureSynapseConnector",
}


def _import_class(dotted_path: str) -> Type[DatabaseConnector]:
    module_path, class_name = dotted_path.rsplit(".", 1)
    import importlib
    module = importlib.import_module(module_path)
    return getattr(module, class_name)


def register_connector(db_type: DatabaseType, class_path: str) -> None:
    _REGISTRY[db_type] = class_path


class ConnectorFactory:
    @staticmethod
    def create_connector(connection_config: Union[ConnectionConfig, Dict[str, Any]]) -> DatabaseConnector:
        if isinstance(connection_config, ConnectionConfig):
            config_dict = connection_config.model_dump()
        else:
            config_dict = connection_config
        db_type_raw = config_dict.get("type")
        if not db_type_raw:
            raise ConnectorFactoryError("Missing 'type' in connection config")
        try:
            db_type = DatabaseType(db_type_raw) if isinstance(db_type_raw, str) else db_type_raw
        except ValueError:
            raise ConnectorFactoryError(f"Unsupported database type: {db_type_raw}")
        class_path = _REGISTRY.get(db_type)
        if not class_path:
            raise ConnectorFactoryError(f"No connector registered for type: {db_type.value}")
        connector_cls = _import_class(class_path)
        kwargs = {
            "host": config_dict.get("host", ""),
            "port": config_dict.get("port", 0),
            "database": config_dict.get("database", ""),
            "username": config_dict.get("username", ""),
            "password": config_dict.get("password", ""),
            "ssl": config_dict.get("ssl", False),
        }
        for key, value in config_dict.items():
            if key not in (
                "type", "host", "port", "database", "username", "password",
                "ssl", "name", "id", "owner_id", "additional_options",
            ):
                kwargs[key] = value
        additional = config_dict.get("additional_options") or {}
        kwargs.update(additional)
        logger.info(f"Creating connector: {db_type.value} -> {connector_cls.__name__}")
        return connector_cls(**kwargs)
