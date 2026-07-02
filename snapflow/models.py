"""
SnapFlow Database Models

SQLAlchemy models for storing snapshot metadata.
"""

import hashlib
import uuid
from datetime import datetime, timezone

import sqlalchemy as sa
from sqlalchemy.orm import DeclarativeBase, relationship


class Base(DeclarativeBase):
    """Base class for all models."""

    pass


def generate_unique_hash() -> str:
    """
    Generate a unique hash for snapshot identification.

    Returns:
        32-character hexadecimal hash
    """
    return hashlib.md5(str(uuid.uuid4()).encode("utf-8")).hexdigest()


class Snapshot(Base):
    """
    Represents a database snapshot.

    A snapshot captures the state of one or more databases at a specific
    point in time.
    """

    __tablename__ = "snapshots"

    id = sa.Column(
        sa.Integer,
        sa.Sequence("snapshot_id_seq"),
        primary_key=True,
        doc="Unique snapshot identifier",
    )
    snapshot_name = sa.Column(
        sa.String(255), nullable=False, index=True, doc="User-friendly snapshot name"
    )
    project_name = sa.Column(
        sa.String(255), nullable=False, index=True, doc="Project this snapshot belongs to"
    )
    hash = sa.Column(
        sa.String(32),
        nullable=False,
        default=generate_unique_hash,
        unique=True,
        doc="Unique hash for internal identification",
    )
    created_at = sa.Column(
        sa.DateTime,
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
        doc="Timestamp when snapshot was created",
    )
    worker_pid = sa.Column(
        sa.Integer, nullable=True, doc="PID of background worker copying slave databases"
    )
    description = sa.Column(sa.Text, nullable=True, doc="Optional description of the snapshot")

    # Relationships
    tables = relationship(
        "DatabaseTable",
        back_populates="snapshot",
        cascade="all, delete-orphan",
        doc="Database tables included in this snapshot",
    )

    def __init__(self, **kwargs):
        """Initialize Snapshot with automatic hash generation."""
        if "hash" not in kwargs:
            kwargs["hash"] = generate_unique_hash()
        if "created_at" not in kwargs:
            kwargs["created_at"] = datetime.now(timezone.utc)
        super().__init__(**kwargs)

    @property
    def is_ready(self) -> bool:
        """
        Check if snapshot is ready for restoration.

        Returns:
            True if slave copies are complete, False otherwise
        """
        return self.worker_pid is None

    @property
    def age(self) -> float:
        """
        Get age of snapshot in seconds.

        Returns:
            Number of seconds since snapshot was created
        """
        now = datetime.now(timezone.utc)
        # Handle both timezone-aware and naive datetimes
        created = self.created_at
        if created.tzinfo is None:
            created = created.replace(tzinfo=timezone.utc)
        return (now - created).total_seconds()

    def __repr__(self) -> str:
        return (
            f"<Snapshot(id={self.id}, name='{self.snapshot_name}', "
            f"project='{self.project_name}', created={self.created_at})>"
        )

    def __str__(self) -> str:
        return f"{self.snapshot_name} ({self.project_name})"


class DatabaseTable(Base):
    """
    Represents a database table within a snapshot.

    Each snapshot can contain multiple database tables, and this model
    tracks the metadata for each.
    """

    __tablename__ = "database_tables"

    id = sa.Column(
        sa.Integer, sa.Sequence("table_id_seq"), primary_key=True, doc="Unique table identifier"
    )
    table_name = sa.Column(sa.String(255), nullable=False, doc="Original database name")
    snapshot_id = sa.Column(
        sa.Integer,
        sa.ForeignKey("snapshots.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
        doc="Foreign key to parent snapshot",
    )
    created_at = sa.Column(
        sa.DateTime,
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
        doc="Timestamp when table was added",
    )
    size_bytes = sa.Column(
        sa.BigInteger, nullable=True, doc="Estimated size of the database in bytes"
    )

    # Relationships
    snapshot = relationship("Snapshot", back_populates="tables", doc="Parent snapshot")

    def get_internal_name(self, copy_type: str) -> str:
        """
        Generate internal database name for this table.

        SnapFlow stores two copies of each database:
        - master: Primary copy used for cloning
        - slave: Secondary copy ready for instant restore

        Args:
            copy_type: Either 'master' or 'slave'

        Returns:
            Internal database name

        Raises:
            ValueError: If copy_type is invalid
        """
        if copy_type not in ("master", "slave"):
            raise ValueError(f"Invalid copy_type: {copy_type}. Must be 'master' or 'slave'")

        if not self.snapshot or not self.snapshot.hash:
            raise ValueError("Cannot generate name: snapshot or hash is missing")

        # Generate a short, unique identifier
        combined = f"{self.table_name}|{self.snapshot.hash}|{copy_type}"
        hash_digest = hashlib.md5(combined.encode("utf-8")).hexdigest()[:16]

        return f"snapflow_{hash_digest}"

    def get_master_name(self) -> str:
        """Get the master copy database name."""
        return self.get_internal_name("master")

    def get_slave_name(self) -> str:
        """Get the slave copy database name."""
        return self.get_internal_name("slave")

    def __repr__(self) -> str:
        return (
            f"<DatabaseTable(id={self.id}, name='{self.table_name}', "
            f"snapshot_id={self.snapshot_id})>"
        )

    def __str__(self) -> str:
        return self.table_name


# Create indexes for better query performance
sa.Index("idx_snapshot_project_name", Snapshot.project_name, Snapshot.snapshot_name)
sa.Index("idx_snapshot_created", Snapshot.created_at.desc())
