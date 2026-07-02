"""
SnapFlow Configuration Management

Handles loading, validating, and saving configuration files.
"""

import os
import logging
from pathlib import Path
from typing import Dict, Any, Optional

import yaml
from schema import Schema, Use, Optional as SchemaOptional, SchemaError

from snapflow.exceptions import InvalidConfigError, MissingConfigError

logger = logging.getLogger(__name__)


# Default configuration values
DEFAULT_CONFIG = {
    "logging": logging.INFO,
    "migrate_from_old_version": False,
    "config_version": "1.0.0",
}


# Configuration schema validator
CONFIG_SCHEMA = Schema(
    {
        "snapflow_url": Use(str),
        "url": Use(str),
        "project_name": Use(str),
        "tracked_databases": [Use(str)],
        SchemaOptional("logging"): Use(int),
        SchemaOptional("migrate_from_old_version"): Use(bool),
        SchemaOptional("config_version"): Use(str),
    }
)


def find_config_file(start_path: Optional[str] = None) -> Optional[Path]:
    """
    Search for snapflow.yaml configuration file in current directory
    and parent directories.

    Args:
        start_path: Starting directory for search (defaults to cwd)

    Returns:
        Path to configuration file or None if not found
    """
    current_dir = Path(start_path or os.getcwd()).resolve()

    # Search up the directory tree
    for directory in [current_dir] + list(current_dir.parents):
        config_path = directory / "snapflow.yaml"
        if config_path.exists():
            logger.debug(f"Found config file: {config_path}")
            return config_path

        # Stop at filesystem root
        if directory == directory.parent:
            break

    return None


def load_config(config_path: Optional[str] = None) -> Dict[str, Any]:
    """
    Load and validate SnapFlow configuration.

    Args:
        config_path: Optional path to configuration file

    Returns:
        Validated configuration dictionary

    Raises:
        MissingConfigError: If configuration file not found
        InvalidConfigError: If configuration is invalid
    """
    if config_path:
        config_file = Path(config_path)
        if not config_file.exists():
            raise MissingConfigError(f"Configuration file not found: {config_path}")
    else:
        config_file = find_config_file()
        if not config_file:
            raise MissingConfigError()

    try:
        with open(config_file, "r", encoding="utf-8") as f:
            config = yaml.safe_load(f)
    except yaml.YAMLError as e:
        raise InvalidConfigError(f"Invalid YAML in configuration file: {e}")
    except Exception as e:
        raise InvalidConfigError(f"Error reading configuration file: {e}")

    if not config:
        raise InvalidConfigError("Configuration file is empty")

    # Apply defaults
    for key, value in DEFAULT_CONFIG.items():
        if key not in config:
            config[key] = value

    # Validate configuration
    try:
        validated_config = CONFIG_SCHEMA.validate(config)
    except SchemaError as e:
        raise InvalidConfigError(f"Configuration validation failed: {e}")

    logger.debug(f"Loaded configuration for project: {validated_config['project_name']}")
    return validated_config


def save_config(config: Dict[str, Any], config_path: Optional[str] = None) -> None:
    """
    Save configuration to file.

    Args:
        config: Configuration dictionary to save
        config_path: Optional path to save configuration (defaults to current dir)

    Raises:
        InvalidConfigError: If unable to save configuration
    """
    if config_path:
        output_path = Path(config_path)
    else:
        existing_config = find_config_file()
        if existing_config:
            output_path = existing_config
        else:
            output_path = Path.cwd() / "snapflow.yaml"

    try:
        # Validate before saving
        CONFIG_SCHEMA.validate(config)

        with open(output_path, "w", encoding="utf-8") as f:
            yaml.dump(config, f, default_flow_style=False, sort_keys=False)

        logger.info(f"Configuration saved to: {output_path}")
    except SchemaError as e:
        raise InvalidConfigError(f"Cannot save invalid configuration: {e}")
    except Exception as e:
        raise InvalidConfigError(f"Error saving configuration: {e}")


def create_default_config(
    project_name: str, url: str, database_name: str, output_path: Optional[str] = None
) -> Dict[str, Any]:
    """
    Create a default configuration dictionary.

    Args:
        project_name: Name of the project
        url: Database connection URL
        database_name: Name of the database to track
        output_path: Optional path to save configuration

    Returns:
        Configuration dictionary
    """
    # Ensure URL ends with /
    if not url.endswith("/"):
        url += "/"

    config = {
        "project_name": project_name,
        "tracked_databases": [database_name],
        "url": url,
        "snapflow_url": f"{url}snapflow_data",
        **DEFAULT_CONFIG,
    }

    if output_path:
        save_config(config, output_path)

    return config


def get_database_url(config: Dict[str, Any]) -> str:
    """
    Get the main database URL from configuration.

    Args:
        config: Configuration dictionary

    Returns:
        Database connection URL
    """
    return config["url"]


def get_snapflow_url(config: Dict[str, Any]) -> str:
    """
    Get the SnapFlow metadata database URL from configuration.

    Args:
        config: Configuration dictionary

    Returns:
        SnapFlow database connection URL
    """
    return config["snapflow_url"]
