# Changelog

All notable changes to SnapFlow will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.0.0] - 2026-07-02

### Added
- Initial release of SnapFlow
- Fast database snapshot and restore functionality
- PostgreSQL full support with template-based copying
- MySQL support with table-by-table copying
- Interactive CLI with intuitive commands
- Background worker process for slave database copying
- Snapshot management (create, restore, list, remove, rename, replace)
- Garbage collection for orphaned databases
- Comprehensive test suite with high coverage
- Full documentation and examples
- GitHub Actions CI/CD pipeline
- Type hints throughout codebase
- MIT License

### Features
- `snapflow init` - Interactive configuration wizard
- `snapflow snapshot` - Create database snapshots
- `snapflow restore` - Instant database restoration
- `snapflow list` - View all snapshots with timestamps
- `snapflow remove` - Delete snapshots
- `snapflow rename` - Rename snapshots
- `snapflow replace` - Replace snapshot with current state
- `snapflow gc` - Clean up orphaned databases
- `snapflow version` - Display version information

### Technical Highlights
- Zero-downtime restores using database renaming
- Automatic background slave copy generation
- Smart snapshot metadata management
- Comprehensive error handling and validation
- Cross-platform support (Linux, macOS, Windows)
- Python 3.8+ support
- SQLAlchemy-based database operations
- Click-based CLI with beautiful output

### Documentation
- Comprehensive README with usage examples
- API documentation with docstrings
- Contributing guidelines
- Code of conduct
- MIT License

### Development Tools
- pytest for testing
- Black for code formatting
- isort for import sorting
- flake8 for linting
- mypy for type checking
- GitHub Actions for CI/CD

## [Unreleased]

### Planned Features
- SQLite support
- Database diff visualization
- Snapshot tagging and search
- Automatic snapshot scheduling
- Snapshot compression
- Cloud backup integration
- Web-based dashboard
- Performance metrics and analytics

---

For more details, see the [GitHub releases page](https://github.com/quantumdb/snapflow/releases).
