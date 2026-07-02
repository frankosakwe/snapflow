"""
Tests for SnapFlow Database Operations

Tests low-level database operations.
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
import sqlalchemy as sa

from snapflow.operations import (
    get_database_url,
    get_postgresql_version,
    get_pid_column_name,
    SUPPORTED_DIALECTS,
)
from snapflow.exceptions import DatabaseNotSupportedError


class TestGetDatabaseUrl:
    """Tests for get_database_url function."""
    
    def test_url_ending_with_slash(self):
        """Should append database name to URL ending with /."""
        conn = Mock()
        conn.engine.url = 'postgresql://localhost:5432/'
        
        result = get_database_url(conn, 'mydb')
        assert result == 'postgresql://localhost:5432/mydb'
    
    def test_url_with_existing_database(self):
        """Should replace existing database in URL."""
        conn = Mock()
        conn.engine.url = 'postgresql://localhost:5432/olddb'
        
        result = get_database_url(conn, 'newdb')
        assert 'newdb' in result


class TestGetPostgresqlVersion:
    """Tests for get_postgresql_version function."""
    
    def test_parses_standard_version(self):
        """Should parse standard PostgreSQL version string."""
        conn = Mock()
        result_mock = Mock()
        result_mock.first.return_value = ['9.6.1']
        conn.execute.return_value = result_mock
        
        version = get_postgresql_version(conn)
        assert version == [9, 6]
    
    def test_parses_branded_version(self):
        """Should parse branded PostgreSQL version (Ubuntu, etc.)."""
        conn = Mock()
        result_mock = Mock()
        result_mock.first.return_value = ['10.3 (Ubuntu 10.3-1.pgdg16.04+1)']
        conn.execute.return_value = result_mock
        
        version = get_postgresql_version(conn)
        assert version == [10, 3]
    
    def test_handles_unparseable_version(self):
        """Should return safe default for unparseable versions."""
        conn = Mock()
        result_mock = Mock()
        result_mock.first.return_value = ['unknown version']
        conn.execute.return_value = result_mock
        
        version = get_postgresql_version(conn)
        assert version == [9, 2]  # Safe default


class TestGetPidColumnName:
    """Tests for get_pid_column_name function."""
    
    @pytest.mark.parametrize('version,expected', [
        ([9, 1], 'procpid'),
        ([9, 0], 'procpid'),
        ([8, 9], 'procpid'),
        ([9, 2], 'pid'),
        ([9, 3], 'pid'),
        ([10, 0], 'pid'),
        ([11, 5], 'pid'),
    ])
    def test_returns_correct_column_name(self, version, expected):
        """Should return correct PID column name based on version."""
        conn = Mock()
        
        with patch('snapflow.operations.get_postgresql_version', return_value=version):
            result = get_pid_column_name(conn)
            assert result == expected


class TestSupportedDialects:
    """Tests for supported database dialects."""
    
    def test_postgresql_supported(self):
        """PostgreSQL should be in supported dialects."""
        assert 'postgresql' in SUPPORTED_DIALECTS
    
    def test_mysql_supported(self):
        """MySQL should be in supported dialects."""
        assert 'mysql' in SUPPORTED_DIALECTS
