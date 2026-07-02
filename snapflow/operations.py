"""
SnapFlow Database Operations

Low-level database operations for creating, copying, and managing databases.
"""

import logging
import re
from typing import List

import sqlalchemy as sa
import sqlalchemy_utils
from sqlalchemy.engine import Connection

from snapflow.exceptions import DatabaseNotSupportedError

logger = logging.getLogger(__name__)


# Supported database dialects
SUPPORTED_DIALECTS = ("postgresql", "mysql")


def get_database_url(connection: Connection, database_name: str) -> str:
    """
    Construct full database URL for a given database name.

    Args:
        connection: SQLAlchemy connection
        database_name: Name of the database

    Returns:
        Complete database URL string
    """
    base_url = str(connection.engine.url)

    # Handle URLs that end with /
    if base_url.count("/") == 3 and base_url.endswith("/"):
        return f"{base_url}{database_name}"

    # Handle URLs with existing database
    if not base_url.endswith("/"):
        base_url += "/"

    parts = base_url.split("/")
    return "/".join(parts[:-2] + [database_name])


def get_postgresql_version(connection: Connection) -> List[int]:
    """
    Get PostgreSQL version as a list of integers.

    Args:
        connection: SQLAlchemy connection to PostgreSQL

    Returns:
        Version as [major, minor] list
    """
    result = connection.execute(sa.text("SHOW server_version;"))
    version_string = result.first()[0]

    # Extract version numbers (handle branded versions like Ubuntu packages)
    version_match = re.search(r"^(\d+\.\d+)", version_string)
    if not version_match:
        logger.warning(f"Could not parse PostgreSQL version: {version_string}")
        return [9, 2]  # Safe default

    version_parts = version_match.group(1).split(".")
    return [int(x) for x in version_parts]


def get_pid_column_name(connection: Connection) -> str:
    """
    Get the correct PID column name for PostgreSQL version.

    PostgreSQL 9.2+ uses 'pid', earlier versions use 'procpid'.

    Args:
        connection: SQLAlchemy connection to PostgreSQL

    Returns:
        Column name ('pid' or 'procpid')
    """
    version = get_postgresql_version(connection)
    return "pid" if version >= [9, 2] else "procpid"


def terminate_database_connections(connection: Connection, database_name: str) -> None:
    """
    Terminate all active connections to a database.

    This is necessary before operations like renaming or dropping databases.

    Args:
        connection: SQLAlchemy connection
        database_name: Name of the database
    """
    logger.debug(f"Terminating connections to: {database_name}")
    dialect = connection.engine.dialect.name

    if dialect == "postgresql":
        pid_column = get_pid_column_name(connection)

        query = sa.text(f"""
            SELECT pg_terminate_backend(pg_stat_activity.{pid_column})
            FROM pg_stat_activity
            WHERE
                pg_stat_activity.datname = :database_name AND
                {pid_column} <> pg_backend_pid()
        """)

        connection.execute(query, {"database_name": database_name})
    elif dialect == "mysql":
        # MySQL doesn't require explicit connection termination
        # for most operations
        pass
    else:
        logger.warning(f"Connection termination not implemented for: {dialect}")


def create_database(connection: Connection, database_name: str) -> None:
    """
    Create a new empty database.

    Args:
        connection: SQLAlchemy connection
        database_name: Name of the database to create
    """
    logger.debug(f"Creating database: {database_name}")
    url = get_database_url(connection, database_name)
    sqlalchemy_utils.functions.create_database(url)


def database_exists(connection: Connection, database_name: str) -> bool:
    """
    Check if a database exists.

    Args:
        connection: SQLAlchemy connection
        database_name: Name of the database

    Returns:
        True if database exists, False otherwise
    """
    url = get_database_url(connection, database_name)
    return sqlalchemy_utils.functions.database_exists(url)


def remove_database(connection: Connection, database_name: str) -> None:
    """
    Drop a database.

    Args:
        connection: SQLAlchemy connection
        database_name: Name of the database to remove
    """
    logger.debug(f"Removing database: {database_name}")
    terminate_database_connections(connection, database_name)
    url = get_database_url(connection, database_name)
    sqlalchemy_utils.functions.drop_database(url)


def copy_database(connection: Connection, source_database: str, target_database: str) -> None:
    """
    Create a copy of a database.

    PostgreSQL uses fast template-based copying.
    MySQL copies table-by-table (slower but reliable).

    Args:
        connection: SQLAlchemy connection
        source_database: Name of the source database
        target_database: Name of the target database
    """
    logger.debug(f"Copying database: {source_database} -> {target_database}")

    terminate_database_connections(connection, source_database)
    dialect = connection.engine.dialect.name

    if dialect == "postgresql":
        # Fast template-based copy
        target_url = get_database_url(connection, target_database)
        sqlalchemy_utils.functions.create_database(target_url, template=source_database)
    elif dialect == "mysql":
        # Table-by-table copy for MySQL
        _copy_mysql_database(connection, source_database, target_database)
    else:
        raise DatabaseNotSupportedError(dialect)


def _copy_mysql_database(
    connection: Connection, source_database: str, target_database: str
) -> None:
    """
    Copy MySQL database table by table.

    This is slower than PostgreSQL's template method but necessary
    for MySQL.

    Args:
        connection: SQLAlchemy connection
        source_database: Source database name
        target_database: Target database name
    """
    create_database(connection, target_database)

    # Get list of tables
    result = connection.execute(sa.text(f"SHOW TABLES IN `{source_database}`"))
    tables = [row[0] for row in result]

    logger.info(f"Copying {len(tables)} tables from {source_database}")

    for table_name in tables:
        logger.debug(f"Copying table: {table_name}")

        # Create table structure
        connection.execute(
            sa.text(
                f"CREATE TABLE `{target_database}`.`{table_name}` "
                f"LIKE `{source_database}`.`{table_name}`"
            )
        )

        # Disable keys for faster insertion
        connection.execute(sa.text(f"ALTER TABLE `{target_database}`.`{table_name}` DISABLE KEYS"))

        # Copy data
        connection.execute(
            sa.text(
                f"INSERT INTO `{target_database}`.`{table_name}` "
                f"SELECT * FROM `{source_database}`.`{table_name}`"
            )
        )

        # Re-enable keys
        connection.execute(sa.text(f"ALTER TABLE `{target_database}`.`{table_name}` ENABLE KEYS"))


def rename_database(connection: Connection, old_name: str, new_name: str) -> None:
    """
    Rename a database.

    This is the key operation that makes restores fast - we just
    rename the slave copy to replace the current database.

    Args:
        connection: SQLAlchemy connection
        old_name: Current database name
        new_name: New database name
    """
    logger.debug(f"Renaming database: {old_name} -> {new_name}")

    terminate_database_connections(connection, old_name)
    dialect = connection.engine.dialect.name

    if dialect == "postgresql":
        connection.execute(sa.text(f'ALTER DATABASE "{old_name}" RENAME TO "{new_name}"'))
    elif dialect == "mysql":
        # MySQL doesn't support direct database rename
        # We have to create new DB and rename all tables
        create_database(connection, new_name)

        result = connection.execute(sa.text(f"SHOW TABLES IN `{old_name}`"))
        tables = [row[0] for row in result]

        for table_name in tables:
            connection.execute(
                sa.text(
                    f"RENAME TABLE `{old_name}`.`{table_name}` " f"TO `{new_name}`.`{table_name}`"
                )
            )

        remove_database(connection, old_name)
    else:
        raise DatabaseNotSupportedError(dialect)


def list_databases(connection: Connection) -> List[str]:
    """
    Get list of all databases.

    Args:
        connection: SQLAlchemy connection

    Returns:
        List of database names
    """
    logger.debug("Listing all databases")
    dialect = connection.engine.dialect.name

    if dialect == "postgresql":
        result = connection.execute(sa.text("""
            SELECT datname FROM pg_database
            WHERE datistemplate = false
        """))
        return [row[0] for row in result]
    elif dialect == "mysql":
        result = connection.execute(sa.text("SHOW DATABASES"))
        return [row[0] for row in result]
    else:
        raise DatabaseNotSupportedError(dialect)


def get_database_size(connection: Connection, database_name: str) -> int:
    """
    Get estimated database size in bytes.

    Args:
        connection: SQLAlchemy connection
        database_name: Name of the database

    Returns:
        Size in bytes (approximate)
    """
    dialect = connection.engine.dialect.name

    try:
        if dialect == "postgresql":
            result = connection.execute(
                sa.text("SELECT pg_database_size(:db_name)"), {"db_name": database_name}
            )
            return result.first()[0]
        elif dialect == "mysql":
            result = connection.execute(
                sa.text("""
                SELECT SUM(data_length + index_length)
                FROM information_schema.tables
                WHERE table_schema = :db_name
            """),
                {"db_name": database_name},
            )
            size = result.first()[0]
            return size if size else 0
    except Exception as e:
        logger.warning(f"Could not get database size: {e}")
        return 0
