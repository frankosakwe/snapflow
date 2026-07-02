"""
SnapFlow Core Application

Main application class that coordinates snapshot and restore operations.
"""

import logging
import os
import sys
from functools import partial
from typing import Callable, List, Optional

from psutil import pid_exists
from sqlalchemy import create_engine
from sqlalchemy.exc import ProgrammingError
from sqlalchemy.orm import sessionmaker

from snapflow.config import load_config
from snapflow.exceptions import (
    SnapshotAlreadyExistsError,
    SnapshotRestoreError,
)
from snapflow.models import Base, DatabaseTable, Snapshot
from snapflow.operations import (
    copy_database,
    create_database,
    database_exists,
    get_database_size,
    list_databases,
    remove_database,
    rename_database,
    terminate_database_connections,
)

__version__ = "1.0.0"
logger = logging.getLogger(__name__)


class DatabaseOperations:
    """
    Wrapper for database operations with connection binding.
    """

    def __init__(self, connection, config):
        self.connection = connection
        self.config = config

        # Bind operations to this connection
        self.terminate_connections = partial(terminate_database_connections, connection)
        self.create_database = partial(create_database, connection)
        self.copy_database = partial(copy_database, connection)
        self.database_exists = partial(database_exists, connection)
        self.rename_database = partial(rename_database, connection)
        self.remove_database = partial(remove_database, connection)
        self.list_databases = partial(list_databases, connection)
        self.get_database_size = partial(get_database_size, connection)


class SnapFlow:
    """
    Main SnapFlow application class.

    Coordinates all snapshot and restore operations, manages database
    connections, and handles background worker processes.
    """

    def __init__(self, config_path: Optional[str] = None):
        """
        Initialize SnapFlow application.

        Args:
            config_path: Optional path to configuration file
        """
        logger.debug("Initializing SnapFlow")
        self.config_path = config_path
        self.load_configuration()
        self.initialize_database()

    def load_configuration(self) -> None:
        """Load and apply configuration."""
        self.config = load_config(self.config_path)

        # Configure logging
        logging.basicConfig(
            level=self.config.get("logging", logging.INFO),
            format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        )

    def initialize_database(self) -> None:
        """Initialize database connections and create metadata tables."""
        # Create engine for main database operations
        self.engine = create_engine(self.config["url"], echo=False)
        self.connection = self.engine.connect()
        self.operations = DatabaseOperations(self.connection, self.config)

        # Set isolation level for PostgreSQL
        try:
            self.connection.connection.set_isolation_level(0)
        except AttributeError:
            logger.debug("Could not set isolation level (normal for MySQL)")

        # Create engine for metadata database
        self.metadata_engine = create_engine(self.config["snapflow_url"], echo=False)

        # Create sessions
        SessionClass = sessionmaker(bind=self.metadata_engine)
        self.session = SessionClass()

        # Ensure metadata database exists
        self.ensure_metadata_database()

        # Create tables if needed
        self.create_metadata_tables()

    def ensure_metadata_database(self) -> bool:
        """
        Ensure SnapFlow metadata database exists.

        Returns:
            True if database was created, False if it already existed
        """
        if not self.operations.database_exists("snapflow_data"):
            logger.info("Creating SnapFlow metadata database")
            self.operations.create_database("snapflow_data")
            return True
        return False

    def create_metadata_tables(self) -> None:
        """Create metadata tables in the SnapFlow database."""
        Base.metadata.create_all(self.metadata_engine)
        self.session.commit()
        logger.debug("Metadata tables ready")

    def get_snapshot(self, snapshot_name: str) -> Optional[Snapshot]:
        """
        Get a snapshot by name for the current project.

        Args:
            snapshot_name: Name of the snapshot

        Returns:
            Snapshot object or None if not found
        """
        return (
            self.session.query(Snapshot)
            .filter(
                Snapshot.snapshot_name == snapshot_name,
                Snapshot.project_name == self.config["project_name"],
            )
            .first()
        )

    def get_all_snapshots(self) -> List[Snapshot]:
        """
        Get all snapshots for the current project.

        Returns:
            List of Snapshot objects, sorted by creation time (newest first)
        """
        return (
            self.session.query(Snapshot)
            .filter(Snapshot.project_name == self.config["project_name"])
            .order_by(Snapshot.created_at.desc())
            .all()
        )

    def get_latest_snapshot(self) -> Optional[Snapshot]:
        """
        Get the most recent snapshot for the current project.

        Returns:
            Latest Snapshot object or None if no snapshots exist
        """
        return (
            self.session.query(Snapshot)
            .filter(Snapshot.project_name == self.config["project_name"])
            .order_by(Snapshot.created_at.desc())
            .first()
        )

    def create_snapshot(
        self,
        snapshot_name: str,
        description: Optional[str] = None,
        before_copy: Optional[Callable[[str], None]] = None,
    ) -> Snapshot:
        """
        Create a new snapshot of tracked databases.

        Args:
            snapshot_name: Name for the snapshot
            description: Optional description
            before_copy: Optional callback called before each database copy

        Returns:
            Created Snapshot object

        Raises:
            SnapshotAlreadyExistsError: If snapshot name already exists
        """
        # Check if snapshot already exists
        if self.get_snapshot(snapshot_name):
            raise SnapshotAlreadyExistsError(snapshot_name)

        # Create snapshot record
        snapshot = Snapshot(
            snapshot_name=snapshot_name,
            project_name=self.config["project_name"],
            description=description,
        )
        self.session.add(snapshot)
        self.session.flush()

        logger.info(f"Creating snapshot: {snapshot_name}")

        # Copy each tracked database
        for db_name in self.config["tracked_databases"]:
            if before_copy:
                before_copy(db_name)

            table = DatabaseTable(table_name=db_name, snapshot=snapshot)

            master_name = table.get_master_name()
            logger.debug(f"Copying {db_name} to {master_name}")

            # Perform the copy
            self.operations.copy_database(db_name, master_name)

            # Store size information
            try:
                table.size_bytes = self.operations.get_database_size(db_name)
            except Exception as e:
                logger.warning(f"Could not get size for {db_name}: {e}")

            self.session.add(table)

        self.session.commit()
        logger.info(f"Snapshot '{snapshot_name}' created successfully")

        # Start background process to create slave copies
        self.start_background_copy(snapshot)

        return snapshot

    def remove_snapshot(self, snapshot: Snapshot) -> None:
        """
        Remove a snapshot and its associated databases.

        Args:
            snapshot: Snapshot object to remove
        """
        logger.info(f"Removing snapshot: {snapshot.snapshot_name}")

        for table in snapshot.tables:
            # Remove master copy
            try:
                self.operations.remove_database(table.get_master_name())
                logger.debug(f"Removed master: {table.get_master_name()}")
            except ProgrammingError as e:
                logger.warning(f"Could not remove master database: {e}")

            # Remove slave copy
            try:
                self.operations.remove_database(table.get_slave_name())
                logger.debug(f"Removed slave: {table.get_slave_name()}")
            except ProgrammingError as e:
                logger.warning(f"Could not remove slave database: {e}")

            self.session.delete(table)

        self.session.delete(snapshot)
        self.session.commit()
        logger.info(f"Snapshot '{snapshot.snapshot_name}' removed")

    def rename_snapshot(self, snapshot: Snapshot, new_name: str) -> None:
        """
        Rename a snapshot.

        Args:
            snapshot: Snapshot to rename
            new_name: New name for the snapshot

        Raises:
            SnapshotAlreadyExistsError: If new name already exists
        """
        if self.get_snapshot(new_name):
            raise SnapshotAlreadyExistsError(new_name)

        old_name = snapshot.snapshot_name
        snapshot.snapshot_name = new_name
        self.session.commit()
        logger.info(f"Renamed snapshot: {old_name} -> {new_name}")

    def restore_snapshot(self, snapshot: Snapshot) -> None:
        """
        Restore databases from a snapshot.

        This is the fast operation that makes SnapFlow powerful - we simply
        rename the slave copies to replace the current databases.

        Args:
            snapshot: Snapshot to restore from

        Raises:
            SnapshotRestoreError: If restore operation fails
        """
        logger.info(f"Restoring snapshot: {snapshot.snapshot_name}")

        for table in snapshot.tables:
            slave_name = table.get_slave_name()

            # Verify slave copy exists
            if not self.operations.database_exists(slave_name):
                raise SnapshotRestoreError(
                    snapshot.snapshot_name, f"Slave database {slave_name} does not exist"
                )

            logger.debug(f"Restoring database: {table.table_name}")

            # Remove current database if it exists
            try:
                self.operations.remove_database(table.table_name)
            except ProgrammingError:
                logger.debug(f"Database {table.table_name} does not exist")

            # Rename slave to become the active database
            self.operations.rename_database(slave_name, table.table_name)

        # Mark snapshot as needing slave regeneration
        snapshot.worker_pid = 1
        self.session.commit()

        logger.info(f"Restore complete: {snapshot.snapshot_name}")

        # Regenerate slave copies in background
        self.start_background_copy(snapshot)

    def start_background_copy(self, snapshot: Snapshot) -> None:
        """
        Start background process to copy slave databases.

        Slave copies allow instant restores without waiting for copying.

        Args:
            snapshot: Snapshot to create slaves for
        """
        logger.debug("Starting background slave copy process")
        snapshot_id = snapshot.id

        # Close connections before forking
        self.connection.close()
        self.session.close()

        # Fork process (Unix-like systems only)
        if not hasattr(os, "fork"):
            logger.warning("Fork not available, performing inline copy")
            self.inline_slave_copy(snapshot)
            return

        pid = os.fork()

        if pid:
            # Parent process
            logger.debug(f"Background process started: PID {pid}")
            return

        # Child process
        try:
            self.initialize_database()
            snapshot = self.session.query(Snapshot).get(snapshot_id)
            snapshot.worker_pid = os.getpid()
            self.session.commit()

            self.inline_slave_copy(snapshot)
        except Exception as e:
            logger.error(f"Background copy failed: {e}")
        finally:
            sys.exit(0)

    def inline_slave_copy(self, snapshot: Snapshot) -> None:
        """
        Perform slave database copies in current process.

        Args:
            snapshot: Snapshot to create slaves for
        """
        logger.info("Copying slave databases")

        for table in snapshot.tables:
            master_name = table.get_master_name()
            slave_name = table.get_slave_name()

            logger.debug(f"Copying {master_name} -> {slave_name}")

            # Remove old slave if exists
            try:
                self.operations.remove_database(slave_name)
            except ProgrammingError:
                pass

            # Create new slave copy
            self.operations.copy_database(master_name, slave_name)

        # Mark as complete
        snapshot.worker_pid = None
        self.session.commit()
        logger.info("Slave copies complete")

    def is_copy_process_running(self, snapshot: Snapshot) -> bool:
        """
        Check if background copy process is still running.

        Args:
            snapshot: Snapshot to check

        Returns:
            True if process is running, False otherwise
        """
        if snapshot.worker_pid is None:
            return False
        return pid_exists(snapshot.worker_pid)

    def cleanup_orphaned_databases(self, callback: Optional[Callable[[str], None]] = None) -> int:
        """
        Remove orphaned SnapFlow databases not associated with any snapshot.

        Args:
            callback: Optional function called for each deleted database

        Returns:
            Number of databases removed
        """
        logger.info("Cleaning up orphaned databases")

        # Get all SnapFlow databases from snapshots
        tracked_dbs = set()
        for snapshot in self.session.query(Snapshot).all():
            for table in snapshot.tables:
                tracked_dbs.add(table.get_master_name())
                tracked_dbs.add(table.get_slave_name())

        # Get all databases from RDBMS
        all_dbs = set(self.operations.list_databases())

        # Find orphaned SnapFlow databases
        removed_count = 0
        for db_name in all_dbs:
            if (
                db_name.startswith("snapflow_")
                and db_name != "snapflow_data"
                and db_name not in tracked_dbs
            ):

                logger.debug(f"Removing orphaned database: {db_name}")
                self.operations.remove_database(db_name)
                removed_count += 1

                if callback:
                    callback(db_name)

        logger.info(f"Removed {removed_count} orphaned databases")
        return removed_count

    @property
    def default_snapshot_name(self) -> str:
        """
        Generate a default snapshot name (snap1, snap2, etc.).

        Returns:
            Available snapshot name
        """
        n = 1
        while (
            self.session.query(Snapshot)
            .filter(
                Snapshot.snapshot_name == f"snap{n}",
                Snapshot.project_name == self.config["project_name"],
            )
            .count()
        ):
            n += 1
        return f"snap{n}"

    def close(self) -> None:
        """Clean up database connections."""
        if hasattr(self, "connection"):
            self.connection.close()
        if hasattr(self, "session"):
            self.session.close()
        logger.debug("SnapFlow connections closed")

    def __enter__(self):
        """Context manager entry."""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.close()
