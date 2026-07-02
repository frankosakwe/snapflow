"""
Tests for SnapFlow Database Models

Tests the Snapshot and DatabaseTable models.
"""

import pytest
from datetime import datetime, timedelta

from snapflow.models import Snapshot, DatabaseTable, generate_unique_hash


class TestGenerateUniqueHash:
    """Tests for the unique hash generation function."""
    
    def test_generates_hash(self):
        """Hash generation should return a string."""
        hash_value = generate_unique_hash()
        assert hash_value is not None
        assert isinstance(hash_value, str)
    
    def test_hash_length(self):
        """Generated hash should be 32 characters (MD5 hex)."""
        hash_value = generate_unique_hash()
        assert len(hash_value) == 32
    
    def test_hash_uniqueness(self):
        """Each generated hash should be unique."""
        hash1 = generate_unique_hash()
        hash2 = generate_unique_hash()
        assert hash1 != hash2
    
    def test_hash_is_hexadecimal(self):
        """Generated hash should contain only hexadecimal characters."""
        hash_value = generate_unique_hash()
        assert all(c in '0123456789abcdef' for c in hash_value)


class TestSnapshot:
    """Tests for the Snapshot model."""
    
    def test_snapshot_creation(self):
        """Snapshot can be created with required fields."""
        snapshot = Snapshot(
            snapshot_name='test_snapshot',
            project_name='test_project'
        )
        
        assert snapshot.snapshot_name == 'test_snapshot'
        assert snapshot.project_name == 'test_project'
        assert snapshot.hash is not None
        assert len(snapshot.hash) == 32
    
    def test_snapshot_with_description(self):
        """Snapshot can include an optional description."""
        snapshot = Snapshot(
            snapshot_name='test_snapshot',
            project_name='test_project',
            description='Test snapshot description'
        )
        
        assert snapshot.description == 'Test snapshot description'
    
    def test_is_ready_when_no_worker(self):
        """Snapshot is ready when worker_pid is None."""
        snapshot = Snapshot(
            snapshot_name='test',
            project_name='test_project',
            worker_pid=None
        )
        
        assert snapshot.is_ready is True
    
    def test_is_not_ready_when_worker_active(self):
        """Snapshot is not ready when worker_pid is set."""
        snapshot = Snapshot(
            snapshot_name='test',
            project_name='test_project',
            worker_pid=12345
        )
        
        assert snapshot.is_ready is False
    
    def test_age_property(self):
        """Age property returns seconds since creation."""
        past_time = datetime.utcnow() - timedelta(seconds=100)
        snapshot = Snapshot(
            snapshot_name='test',
            project_name='test_project',
            created_at=past_time
        )
        
        age = snapshot.age
        assert age >= 100
        assert age < 110  # Allow some margin
    
    def test_snapshot_repr(self):
        """Snapshot has useful repr."""
        snapshot = Snapshot(
            id=1,
            snapshot_name='test_snapshot',
            project_name='test_project',
            created_at=datetime.utcnow()
        )
        
        repr_str = repr(snapshot)
        assert 'Snapshot' in repr_str
        assert 'test_snapshot' in repr_str
        assert 'test_project' in repr_str
    
    def test_snapshot_str(self):
        """Snapshot has useful string representation."""
        snapshot = Snapshot(
            snapshot_name='test_snapshot',
            project_name='test_project'
        )
        
        str_repr = str(snapshot)
        assert 'test_snapshot' in str_repr
        assert 'test_project' in str_repr


class TestDatabaseTable:
    """Tests for the DatabaseTable model."""
    
    def test_table_creation(self):
        """DatabaseTable can be created with required fields."""
        snapshot = Snapshot(
            snapshot_name='test_snapshot',
            project_name='test_project',
            hash='a1b2c3d4e5f6g7h8i9j0k1l2m3n4o5p6'
        )
        
        table = DatabaseTable(
            table_name='test_db',
            snapshot=snapshot
        )
        
        assert table.table_name == 'test_db'
        assert table.snapshot == snapshot
    
    def test_get_internal_name_master(self):
        """get_internal_name generates correct master name."""
        snapshot = Snapshot(
            snapshot_name='test',
            project_name='test_project',
            hash='abc123def456'
        )
        
        table = DatabaseTable(
            table_name='mydb',
            snapshot=snapshot
        )
        
        master_name = table.get_internal_name('master')
        assert master_name.startswith('snapflow_')
        assert len(master_name) == 25  # snapflow_ + 16 char hash
    
    def test_get_internal_name_slave(self):
        """get_internal_name generates correct slave name."""
        snapshot = Snapshot(
            snapshot_name='test',
            project_name='test_project',
            hash='abc123def456'
        )
        
        table = DatabaseTable(
            table_name='mydb',
            snapshot=snapshot
        )
        
        slave_name = table.get_internal_name('slave')
        assert slave_name.startswith('snapflow_')
        assert len(slave_name) == 25
    
    def test_master_and_slave_names_differ(self):
        """Master and slave names should be different."""
        snapshot = Snapshot(
            snapshot_name='test',
            project_name='test_project',
            hash='abc123def456'
        )
        
        table = DatabaseTable(
            table_name='mydb',
            snapshot=snapshot
        )
        
        master = table.get_internal_name('master')
        slave = table.get_internal_name('slave')
        
        assert master != slave
    
    def test_invalid_copy_type_raises_error(self):
        """get_internal_name raises ValueError for invalid copy type."""
        snapshot = Snapshot(
            snapshot_name='test',
            project_name='test_project',
            hash='abc123def456'
        )
        
        table = DatabaseTable(
            table_name='mydb',
            snapshot=snapshot
        )
        
        with pytest.raises(ValueError, match="Invalid copy_type"):
            table.get_internal_name('invalid')
    
    def test_get_master_name_convenience_method(self):
        """get_master_name is a convenience wrapper."""
        snapshot = Snapshot(
            snapshot_name='test',
            project_name='test_project',
            hash='abc123def456'
        )
        
        table = DatabaseTable(
            table_name='mydb',
            snapshot=snapshot
        )
        
        assert table.get_master_name() == table.get_internal_name('master')
    
    def test_get_slave_name_convenience_method(self):
        """get_slave_name is a convenience wrapper."""
        snapshot = Snapshot(
            snapshot_name='test',
            project_name='test_project',
            hash='abc123def456'
        )
        
        table = DatabaseTable(
            table_name='mydb',
            snapshot=snapshot
        )
        
        assert table.get_slave_name() == table.get_internal_name('slave')
    
    def test_table_repr(self):
        """DatabaseTable has useful repr."""
        snapshot = Snapshot(
            snapshot_name='test',
            project_name='test_project'
        )
        
        table = DatabaseTable(
            id=1,
            table_name='test_db',
            snapshot=snapshot
        )
        
        repr_str = repr(table)
        assert 'DatabaseTable' in repr_str
        assert 'test_db' in repr_str
    
    def test_table_str(self):
        """DatabaseTable has useful string representation."""
        snapshot = Snapshot(
            snapshot_name='test',
            project_name='test_project'
        )
        
        table = DatabaseTable(
            table_name='test_db',
            snapshot=snapshot
        )
        
        assert str(table) == 'test_db'
    
    def test_size_bytes_optional(self):
        """size_bytes field is optional."""
        snapshot = Snapshot(
            snapshot_name='test',
            project_name='test_project'
        )
        
        table = DatabaseTable(
            table_name='test_db',
            snapshot=snapshot,
            size_bytes=1024000
        )
        
        assert table.size_bytes == 1024000


class TestSnapshotTableRelationship:
    """Tests for the relationship between Snapshot and DatabaseTable."""
    
    def test_snapshot_has_tables_relationship(self):
        """Snapshot can have multiple tables."""
        snapshot = Snapshot(
            snapshot_name='test',
            project_name='test_project'
        )
        
        table1 = DatabaseTable(table_name='db1', snapshot=snapshot)
        table2 = DatabaseTable(table_name='db2', snapshot=snapshot)
        
        snapshot.tables = [table1, table2]
        
        assert len(snapshot.tables) == 2
        assert table1 in snapshot.tables
        assert table2 in snapshot.tables
    
    def test_table_has_snapshot_relationship(self):
        """Table has reference to parent snapshot."""
        snapshot = Snapshot(
            snapshot_name='test',
            project_name='test_project'
        )
        
        table = DatabaseTable(table_name='db1', snapshot=snapshot)
        
        assert table.snapshot == snapshot
