"""
Tests for SnapFlow Configuration Management

Tests configuration loading, saving, and validation.
"""

import pytest
import yaml
from pathlib import Path

from snapflow.config import (
    find_config_file,
    load_config,
    save_config,
    create_default_config,
    get_database_url,
    get_snapflow_url,
)
from snapflow.exceptions import MissingConfigError, InvalidConfigError


class TestFindConfigFile:
    """Tests for find_config_file function."""
    
    def test_finds_config_in_current_directory(self, temp_config_dir):
        """Should find config in current directory."""
        config_path = temp_config_dir / 'snapflow.yaml'
        config_path.write_text('test: config')
        
        found = find_config_file(str(temp_config_dir))
        assert found == config_path
    
    def test_finds_config_in_parent_directory(self, temp_config_dir):
        """Should find config in parent directories."""
        config_path = temp_config_dir / 'snapflow.yaml'
        config_path.write_text('test: config')
        
        subdir = temp_config_dir / 'subdir'
        subdir.mkdir()
        
        found = find_config_file(str(subdir))
        assert found == config_path
    
    def test_returns_none_when_not_found(self, temp_config_dir):
        """Should return None when config not found."""
        found = find_config_file(str(temp_config_dir))
        assert found is None


class TestLoadConfig:
    """Tests for load_config function."""
    
    def test_loads_valid_config(self, config_file):
        """Should load a valid configuration file."""
        config = load_config(str(config_file))
        
        assert config['project_name'] == 'test_project'
        assert 'test_database' in config['tracked_databases']
        assert 'url' in config
        assert 'snapflow_url' in config
    
    def test_raises_error_for_missing_config(self, temp_config_dir):
        """Should raise MissingConfigError when file not found."""
        with pytest.raises(MissingConfigError):
            load_config(str(temp_config_dir / 'nonexistent.yaml'))
    
    def test_raises_error_for_invalid_yaml(self, temp_config_dir):
        """Should raise InvalidConfigError for invalid YAML."""
        bad_config = temp_config_dir / 'snapflow.yaml'
        bad_config.write_text('{ invalid yaml content [')
        
        with pytest.raises(InvalidConfigError, match="Invalid YAML"):
            load_config(str(bad_config))
    
    def test_raises_error_for_empty_config(self, temp_config_dir):
        """Should raise InvalidConfigError for empty config."""
        empty_config = temp_config_dir / 'snapflow.yaml'
        empty_config.write_text('')
        
        with pytest.raises(InvalidConfigError, match="empty"):
            load_config(str(empty_config))
    
    def test_applies_default_values(self, temp_config_dir):
        """Should apply default values for missing keys."""
        minimal_config = {
            'project_name': 'test',
            'tracked_databases': ['db1'],
            'url': 'postgresql://localhost/',
            'snapflow_url': 'postgresql://localhost/snapflow_data',
        }
        
        config_path = temp_config_dir / 'snapflow.yaml'
        with open(config_path, 'w') as f:
            yaml.dump(minimal_config, f)
        
        config = load_config(str(config_path))
        
        assert 'logging' in config
        assert 'config_version' in config
    
    def test_validates_required_fields(self, temp_config_dir):
        """Should raise error when required fields are missing."""
        incomplete_config = {
            'project_name': 'test',
            # missing tracked_databases, url, snapflow_url
        }
        
        config_path = temp_config_dir / 'snapflow.yaml'
        with open(config_path, 'w') as f:
            yaml.dump(incomplete_config, f)
        
        with pytest.raises(InvalidConfigError, match="validation failed"):
            load_config(str(config_path))


class TestSaveConfig:
    """Tests for save_config function."""
    
    def test_saves_config_to_file(self, temp_config_dir, test_config):
        """Should save configuration to file."""
        output_path = temp_config_dir / 'snapflow.yaml'
        
        save_config(test_config, str(output_path))
        
        assert output_path.exists()
        
        with open(output_path) as f:
            saved_config = yaml.safe_load(f)
        
        assert saved_config['project_name'] == test_config['project_name']
    
    def test_validates_before_saving(self, temp_config_dir):
        """Should validate config before saving."""
        invalid_config = {'invalid': 'config'}
        output_path = temp_config_dir / 'snapflow.yaml'
        
        with pytest.raises(InvalidConfigError):
            save_config(invalid_config, str(output_path))
    
    def test_overwrites_existing_file(self, config_file, test_config):
        """Should overwrite existing configuration file."""
        test_config['project_name'] = 'updated_project'
        
        save_config(test_config, str(config_file))
        
        with open(config_file) as f:
            saved_config = yaml.safe_load(f)
        
        assert saved_config['project_name'] == 'updated_project'


class TestCreateDefaultConfig:
    """Tests for create_default_config function."""
    
    def test_creates_valid_config(self):
        """Should create a valid configuration dictionary."""
        config = create_default_config(
            project_name='myproject',
            url='postgresql://localhost:5432/',
            database_name='mydb'
        )
        
        assert config['project_name'] == 'myproject'
        assert config['tracked_databases'] == ['mydb']
        assert 'postgresql://localhost:5432/' in config['url']
        assert 'snapflow_data' in config['snapflow_url']
    
    def test_ensures_url_ends_with_slash(self):
        """Should add trailing slash to URL if missing."""
        config = create_default_config(
            project_name='myproject',
            url='postgresql://localhost:5432',
            database_name='mydb'
        )
        
        assert config['url'].endswith('/')
    
    def test_saves_config_when_path_provided(self, temp_config_dir):
        """Should save config to file when output_path provided."""
        output_path = temp_config_dir / 'snapflow.yaml'
        
        config = create_default_config(
            project_name='myproject',
            url='postgresql://localhost:5432/',
            database_name='mydb',
            output_path=str(output_path)
        )
        
        assert output_path.exists()


class TestConfigHelpers:
    """Tests for configuration helper functions."""
    
    def test_get_database_url(self, test_config):
        """Should extract database URL from config."""
        url = get_database_url(test_config)
        assert url == test_config['url']
    
    def test_get_snapflow_url(self, test_config):
        """Should extract SnapFlow URL from config."""
        url = get_snapflow_url(test_config)
        assert url == test_config['snapflow_url']
