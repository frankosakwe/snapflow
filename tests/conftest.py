"""
Pytest Configuration and Fixtures

Shared test fixtures and configuration for the test suite.
"""

import pytest


@pytest.fixture
def temp_config_dir(tmp_path):
    """Create a temporary directory for configuration files."""
    return tmp_path


@pytest.fixture
def temp_database_url(tmp_path):
    """
    Create a temporary SQLite database URL for testing.

    Returns:
        SQLite connection URL string
    """
    db_file = tmp_path / "test.db"
    return f"sqlite:///{db_file}"


@pytest.fixture
def test_config(temp_config_dir, temp_database_url):
    """
    Create a test configuration dictionary.

    Returns:
        Test configuration dictionary
    """
    return {
        "project_name": "test_project",
        "tracked_databases": ["test_database"],
        "url": temp_database_url,
        "snapflow_url": temp_database_url,
        "logging": 30,  # WARNING level
        "migrate_from_old_version": False,
        "config_version": "1.0.0",
    }


@pytest.fixture
def config_file(temp_config_dir, test_config):
    """
    Create a temporary configuration file.

    Returns:
        Path to the configuration file
    """
    import yaml

    config_path = temp_config_dir / "snapflow.yaml"
    with open(config_path, "w") as f:
        yaml.dump(test_config, f)

    return config_path


@pytest.fixture
def mock_connection():
    """Create a mock database connection for testing."""
    from unittest.mock import MagicMock, Mock

    conn = Mock()
    conn.engine = Mock()
    conn.engine.dialect = Mock()
    conn.engine.dialect.name = "postgresql"
    conn.engine.url = "postgresql://localhost:5432/"
    conn.execute = MagicMock()

    return conn
