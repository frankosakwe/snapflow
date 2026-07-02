# SnapFlow - Lightning-Fast Database Snapshot Manager

[![CI/CD](https://github.com/frankosakwe/snapflow/actions/workflows/ci.yml/badge.svg)](https://github.com/frankosakwe/snapflow/actions/workflows/ci.yml)
[![CodeQL](https://github.com/frankosakwe/snapflow/actions/workflows/codeql.yml/badge.svg)](https://github.com/frankosakwe/snapflow/actions/workflows/codeql.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python Version](https://img.shields.io/badge/python-3.8%2B-blue)](https://www.python.org/downloads/)
[![GitHub Stars](https://img.shields.io/github/stars/frankosakwe/snapflow?style=social)](https://github.com/frankosakwe/snapflow)
[![GitHub Issues](https://img.shields.io/github/issues/frankosakwe/snapflow)](https://github.com/frankosakwe/snapflow/issues)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![Imports: isort](https://img.shields.io/badge/%20imports-isort-%231674b1?style=flat&labelColor=ef8336)](https://pycqa.github.io/isort/)

SnapFlow is a high-performance database snapshot and restore tool designed for modern development workflows. Create instant database snapshots, switch between states effortlessly, and accelerate your development cycle.

![SnapFlow Banner](https://via.placeholder.com/800x200/4A90E2/FFFFFF?text=SnapFlow+-+Database+Time+Travel)

## 🚀 Features

- **Lightning Fast**: Restore databases up to 140x faster than traditional dump/restore methods
- **Multi-Database Support**: PostgreSQL and MySQL support out of the box
- **Smart Snapshots**: Automatic background copying for zero-downtime restores
- **Developer Friendly**: Simple CLI commands for everyday workflows
- **Project-Based**: Manage multiple projects with isolated snapshots
- **Safe & Reliable**: Built-in safeguards and error handling

## 🎯 Why SnapFlow?

SnapFlow revolutionizes database management during development:

- **Branch Switching**: Instantly switch database states when changing git branches
- **Migration Testing**: Test database migrations without fear
- **Data Experiments**: Try risky SQL queries with instant rollback capability
- **Clean State**: Return to a pristine database state in seconds

## ⚡ Quick Start

### Installation

```bash
pip install snapflow
```

### Initialize Your Project

```bash
cd your-project
snapflow init
```

Follow the interactive setup wizard to configure your database connection.

### Basic Workflow

```bash
# Create a snapshot
snapflow snapshot baseline

# Make changes to your database...
# Made a mistake? Restore instantly!

snapflow restore baseline

# List all snapshots
snapflow list

# Remove old snapshots
snapflow remove old-snapshot
```

## 📖 Documentation

### Commands

#### `snapflow init`
Initialize SnapFlow configuration for your project. Creates a `snapflow.yaml` file with your database settings.

#### `snapflow snapshot [NAME]`
Create a new snapshot of your database. If no name is provided, an auto-generated name is used.

```bash
snapflow snapshot before-migration
```

#### `snapflow restore [NAME]`
Restore your database from a snapshot. If no name is provided, restores from the most recent snapshot.

```bash
snapflow restore before-migration
```

#### `snapflow list`
Display all snapshots for the current project with creation timestamps.

```bash
snapflow list
```

#### `snapflow remove NAME`
Delete a specific snapshot.

```bash
snapflow remove old-snapshot
```

#### `snapflow rename OLD_NAME NEW_NAME`
Rename an existing snapshot.

```bash
snapflow rename snap1 baseline
```

#### `snapflow replace NAME`
Replace an existing snapshot with the current database state.

```bash
snapflow replace baseline
```

#### `snapflow gc`
Clean up orphaned snapshot databases (garbage collection).

```bash
snapflow gc
```

#### `snapflow version`
Display the current SnapFlow version.

```bash
snapflow version
```

## 🔧 Configuration

SnapFlow uses a `snapflow.yaml` file in your project directory:

```yaml
project_name: 'myproject'
tracked_databases: ['myproject_db']
url: 'postgresql://localhost:5432/template1'
stellar_url: 'postgresql://localhost:5432/snapflow_data'
logging: 20  # Optional: 10=DEBUG, 20=INFO, 30=WARNING
```

**Pro Tip**: Add `snapflow.yaml` to your `.gitignore` to keep database credentials private.

## 🏗️ How It Works

SnapFlow uses a clever approach to achieve blazing-fast restores:

1. **Snapshot Creation**: Creates a copy of your database using native RDBMS features
2. **Background Duplication**: Automatically creates a secondary copy in the background
3. **Instant Restore**: Restores by simply renaming the database (microseconds instead of minutes)
4. **Smart Recovery**: Regenerates the secondary copy after restore for the next operation

This approach trades storage space for speed, making it ideal for development environments.

## 🗄️ Storage Considerations

SnapFlow stores copies of your database, so plan accordingly:

- Each snapshot requires approximately 2x your database size (master + slave copies)
- Use `snapflow gc` regularly to clean up unused snapshots
- Consider disk space when creating multiple snapshots

## ⚠️ Important Notes

- **Development Only**: SnapFlow is designed for development environments, not production
- **Data Loss Risk**: While rare, data loss is possible. Don't use for critical data without backups
- **Storage Space**: Ensure adequate disk space for database copies
- **Permissions**: Requires database user with CREATE DATABASE permissions

## 🔒 Database Support

### PostgreSQL
- ✅ Fully supported
- ✅ Fast template-based copying
- ✅ Connection termination for clean operations

### MySQL
- ⚠️ Supported with limitations
- ⚠️ Slower copying (table-by-table)
- ✅ PyMySQL driver recommended

## 🛠️ Advanced Usage

### Multiple Databases

Track multiple databases in a single project:

```yaml
tracked_databases: 
  - 'main_db'
  - 'analytics_db'
  - 'cache_db'
```

### Custom Connection Strings

PostgreSQL:
```
postgresql://user:password@localhost:5432/
```

MySQL with PyMySQL:
```
mysql+pymysql://root:password@localhost/
```

## 🐛 Troubleshooting

### "Access denied" Error
Ensure your database user has CREATE DATABASE permissions:

```sql
-- PostgreSQL
ALTER USER myuser CREATEDB;

-- MySQL
GRANT ALL PRIVILEGES ON *.* TO 'myuser'@'localhost';
```

### "Database does not exist"
PostgreSQL users need a database matching their username:

```bash
createdb $USER
```

### Slow MySQL Performance
MySQL uses table-by-table copying. Consider:
- Using PostgreSQL for better performance
- Reducing database size during development
- Using SSD storage

## 🤝 Contributing

Contributions are welcome! Please feel free to submit issues and pull requests.

## 📄 License

SnapFlow is released under the MIT License. See LICENSE file for details.

## 🙏 Acknowledgments

SnapFlow builds upon database management concepts and is inspired by the need for faster development workflows.

## 📞 Support

- **Issues**: [GitHub Issues](https://github.com/frankosakwe/snapflow/issues)
- **Discussions**: [GitHub Discussions](https://github.com/frankosakwe/snapflow/discussions)
- **Email**: support@quantumdb.dev

---

**Made with ❤️ by the QuantumDB Team**

*SnapFlow - Because developers deserve better database tools.*
