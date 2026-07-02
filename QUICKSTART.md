# SnapFlow Quick Start Guide

Get up and running with SnapFlow in 5 minutes!

## Installation

### Option 1: Install from PyPI (when published)
```bash
pip install snapflow
```

### Option 2: Install from Source
```bash
git clone https://github.com/quantumdb/snapflow.git
cd snapflow
pip install -e .
```

### Option 3: Install with Development Dependencies
```bash
git clone https://github.com/quantumdb/snapflow.git
cd snapflow
pip install -e ".[dev]"
```

## Database Drivers

Install the appropriate database driver for your database:

### PostgreSQL
```bash
pip install psycopg2-binary
```

### MySQL
```bash
pip install PyMySQL
```

## Verify Installation

```bash
# Check installation
python scripts/verify_installation.py

# Check version
snapflow version
```

## First-Time Setup

### 1. Initialize Configuration

```bash
cd your-project-directory
snapflow init
```

The wizard will ask for:
- **Database URL**: Connection string for your database
  - PostgreSQL: `postgresql://user:password@localhost:5432/`
  - MySQL: `mysql+pymysql://root:password@localhost/`
- **Database Name**: Name of the database to track
- **Project Name**: Identifier for your project

### 2. Add Configuration to .gitignore

```bash
echo "snapflow.yaml" >> .gitignore
```

### 3. Create Your First Snapshot

```bash
snapflow snapshot baseline
```

## Basic Usage

### Create a Snapshot
```bash
# Auto-named snapshot
snapflow snapshot

# Named snapshot
snapflow snapshot before-migration

# With description
snapflow snapshot --description "Before user table changes" pre-migration
```

### List Snapshots
```bash
snapflow list
```

### Restore from Snapshot
```bash
# Restore from specific snapshot
snapflow restore baseline

# Restore from latest snapshot
snapflow restore
```

### Remove a Snapshot
```bash
snapflow remove old-snapshot
```

### Rename a Snapshot
```bash
snapflow rename old-name new-name
```

### Replace a Snapshot
```bash
snapflow replace baseline
```

### Cleanup Orphaned Databases
```bash
snapflow gc
```

## Common Workflows

### Testing Database Migrations

```bash
# 1. Create snapshot before migration
snapflow snapshot before-migration

# 2. Run your migration
python manage.py migrate

# 3. Test the changes
# ... test your application ...

# 4. If something went wrong, restore
snapflow restore before-migration
```

### Branch Switching

```bash
# 1. Create snapshot for current branch
snapflow snapshot feature-branch-stable

# 2. Switch git branch
git checkout main

# 3. Restore database for main branch
snapflow restore main-baseline

# 4. Work on main...

# 5. Switch back to feature branch
git checkout feature-branch
snapflow restore feature-branch-stable
```

### Data Experiments

```bash
# 1. Take snapshot
snapflow snapshot clean-state

# 2. Run risky SQL or experiments
psql -c "UPDATE users SET ..."

# 3. Restore if needed
snapflow restore clean-state
```

## Programmatic Usage

```python
from snapflow import SnapFlow

# Use as context manager
with SnapFlow() as app:
    # Create snapshot
    snapshot = app.create_snapshot('my-snapshot')
    
    # List snapshots
    snapshots = app.get_all_snapshots()
    
    # Restore snapshot
    app.restore_snapshot(snapshot)
    
    # Remove snapshot
    app.remove_snapshot(snapshot)
```

See `examples/basic_usage.py` for more examples.

## Configuration File

SnapFlow uses a `snapflow.yaml` file:

```yaml
project_name: 'myproject'
tracked_databases:
  - 'myproject_db'
  - 'analytics_db'
url: 'postgresql://localhost:5432/template1'
snapflow_url: 'postgresql://localhost:5432/snapflow_data'
logging: 20  # INFO level
```

## Troubleshooting

### "Configuration file not found"
```bash
snapflow init
```

### "Access denied" or Permission Issues
Ensure your database user has CREATE DATABASE permissions:

**PostgreSQL:**
```sql
ALTER USER myuser CREATEDB;
```

**MySQL:**
```sql
GRANT ALL PRIVILEGES ON *.* TO 'myuser'@'localhost';
FLUSH PRIVILEGES;
```

### "Database does not exist" (PostgreSQL)
Create a database matching your username:
```bash
createdb $USER
```

### Slow Performance (MySQL)
MySQL copies tables one by one. For better performance:
- Use PostgreSQL if possible
- Reduce database size during development
- Use SSD storage

## Getting Help

- **Documentation**: See README.md for full documentation
- **Issues**: https://github.com/quantumdb/snapflow/issues
- **Examples**: See `examples/` directory
- **CLI Help**: `snapflow --help`

## Next Steps

1. ✅ Install SnapFlow
2. ✅ Initialize configuration
3. ✅ Create first snapshot
4. 📖 Read full documentation in README.md
5. 👨‍💻 Check out examples in `examples/`
6. 🤝 Contribute! See CONTRIBUTING.md

---

Happy snapshotting! 📸
