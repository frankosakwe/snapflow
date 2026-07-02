# Getting Started with SnapFlow

Welcome to **SnapFlow** - the lightning-fast database snapshot manager for modern development workflows!

## 🎯 What is SnapFlow?

SnapFlow is a tool that lets you:
- Create instant snapshots of your databases
- Restore databases in seconds (up to 140x faster than traditional methods)
- Switch between database states effortlessly
- Test migrations safely
- Experiment with data without fear

## 🚀 Quick Setup (5 Minutes)

### Step 1: Install SnapFlow

```bash
# Clone the repository
cd "C:\Users\USER\OneDrive\Music\st 1\snapflow"

# Install SnapFlow
pip install -e .

# Verify installation
python verify_snapflow.py
```

### Step 2: Set Up Your Database

Make sure you have PostgreSQL or MySQL installed and running.

**PostgreSQL Example:**
```bash
# Make sure PostgreSQL is running
# Default: localhost:5432
```

**MySQL Example:**
```bash
# Make sure MySQL is running
# Default: localhost:3306
```

### Step 3: Initialize SnapFlow

```bash
# Navigate to your project directory
cd C:\path\to\your\project

# Initialize SnapFlow (interactive wizard)
snapflow init
```

The wizard will ask for:
1. **Database URL** (e.g., `postgresql://localhost:5432/` or `mysql+pymysql://root@localhost/`)
2. **Database name** to track (e.g., `myproject_db`)
3. **Project name** (defaults to database name)

### Step 4: Create Your First Snapshot

```bash
# Create a snapshot called "baseline"
snapflow snapshot baseline
```

### Step 5: Make Changes and Restore

```bash
# Make some changes to your database...
# (Add data, run migrations, etc.)

# Oops! Want to go back?
snapflow restore baseline

# Done! Your database is back to the baseline state
```

## 📚 Common Commands

### Creating Snapshots

```bash
# Create with auto-generated name (snap1, snap2, etc.)
snapflow snapshot

# Create with custom name
snapflow snapshot before-migration

# Create with description
snapflow snapshot test-data --description "Test dataset for feature X"
```

### Listing Snapshots

```bash
# Show all snapshots for current project
snapflow list
```

Output example:
```
📸 Snapshots for project 'myproject':

  ✓ baseline
     Created: 2 hours ago
     Databases: 1

  ✓ before-migration
     Created: 30 minutes ago
     Description: Before adding user table
     Databases: 1
```

### Restoring Snapshots

```bash
# Restore latest snapshot
snapflow restore

# Restore specific snapshot
snapflow restore baseline

# Restore and wait for background copy
snapflow restore baseline --wait
```

### Managing Snapshots

```bash
# Rename a snapshot
snapflow rename old-name new-name

# Replace a snapshot with current state
snapflow replace baseline

# Remove a snapshot
snapflow remove old-snapshot

# Clean up orphaned databases
snapflow gc
```

## 🎓 Example Workflows

### Workflow 1: Safe Migration Testing

```bash
# 1. Create snapshot before migration
snapflow snapshot before-users-table

# 2. Run your migration
python manage.py migrate  # Django example
# or
alembic upgrade head      # SQLAlchemy example

# 3. Test the migration
# ... run tests, check data ...

# 4a. If migration is good, keep it
snapflow snapshot after-users-table

# 4b. If migration failed, restore
snapflow restore before-users-table
```

### Workflow 2: Branch Switching

```bash
# On feature-branch-1
snapflow snapshot feature-1-data

# Switch to different branch
git checkout feature-branch-2
snapflow restore feature-2-data

# Back to feature-branch-1
git checkout feature-branch-1
snapflow restore feature-1-data
```

### Workflow 3: Data Experiments

```bash
# Save current state
snapflow snapshot clean-state

# Run risky SQL experiments
# ... experiment with queries ...

# Restore if something went wrong
snapflow restore clean-state
```

## ⚙️ Configuration

### Configuration File Location

SnapFlow looks for `snapflow.yaml` in:
1. Current directory
2. Parent directories (up to filesystem root)

### Example Configuration

```yaml
project_name: 'myproject'
tracked_databases: ['myproject_db', 'myproject_cache']
url: 'postgresql://localhost:5432/template1'
snapflow_url: 'postgresql://localhost:5432/snapflow_data'
logging: 20  # 10=DEBUG, 20=INFO, 30=WARNING, 40=ERROR
```

### Multiple Databases

You can track multiple databases:

```yaml
tracked_databases:
  - 'main_db'
  - 'analytics_db'
  - 'cache_db'
```

## 🔍 Verification & Testing

### Verify Installation

```bash
# Run comprehensive verification
python verify_snapflow.py
```

This checks:
- ✅ Python version
- ✅ Module imports
- ✅ Dependencies
- ✅ Version detection
- ✅ CLI availability
- ✅ Model functionality
- ✅ Database operations
- ✅ Exception handling

### Run Tests

```bash
# Run test suite
python run_tests.py

# Or use pytest directly
pytest -v

# With coverage report
pytest --cov=snapflow --cov-report=html
open htmlcov/index.html
```

## 🗄️ Database Support

### PostgreSQL ✅ (Fully Supported)

**Pros:**
- ⚡ Lightning-fast template-based copying
- ✅ Native database rename support
- ✅ All features work perfectly

**Requirements:**
```bash
pip install psycopg2-binary
```

**Connection String:**
```
postgresql://user:password@localhost:5432/
```

### MySQL ⚠️ (Supported with Limitations)

**Pros:**
- ✅ All core features work
- ✅ Reliable table-by-table copying

**Cons:**
- ⚠️ Slower than PostgreSQL (table-by-table copy)
- ⚠️ No native database rename (simulated)

**Requirements:**
```bash
pip install PyMySQL
```

**Connection String:**
```
mysql+pymysql://root:password@localhost/
```

## ⚠️ Important Notes

### Development Use Only

SnapFlow is designed for **development environments**, not production:
- Uses significant disk space (2x database size per snapshot)
- Assumes you have database creation permissions
- Not designed for critical data without backups

### Storage Requirements

Each snapshot requires:
- **Master copy**: ~1x database size
- **Slave copy**: ~1x database size
- **Total**: ~2x database size per snapshot

**Example:** 1GB database with 3 snapshots = ~6GB storage

### Permissions Required

Your database user needs:
- CREATE DATABASE permission
- DROP DATABASE permission
- For PostgreSQL: CREATEDB role

## 🐛 Troubleshooting

### "Access denied" Error

**Problem:** User lacks database creation permissions

**Solution (PostgreSQL):**
```sql
ALTER USER myuser CREATEDB;
```

**Solution (MySQL):**
```sql
GRANT ALL PRIVILEGES ON *.* TO 'myuser'@'localhost';
FLUSH PRIVILEGES;
```

### "Database does not exist"

**Problem:** PostgreSQL users need a database matching their username

**Solution:**
```bash
createdb $USER
```

### Slow Performance on MySQL

**Problem:** MySQL uses slower table-by-table copying

**Solutions:**
- Use PostgreSQL for better performance
- Use SSD storage
- Reduce database size during development
- Keep fewer snapshots

### Background Copy Not Completing

**Problem:** Background process failed or killed

**Solution:**
```bash
# Force inline copy
snapflow restore baseline --wait
```

## 📖 Advanced Usage

### Programmatic API

```python
from snapflow import SnapFlow

# Use as context manager
with SnapFlow() as app:
    # Create snapshot
    snapshot = app.create_snapshot('test', description='Test snapshot')
    
    # List all snapshots
    snapshots = app.get_all_snapshots()
    
    # Get specific snapshot
    snapshot = app.get_snapshot('test')
    
    # Restore
    app.restore_snapshot(snapshot)
    
    # Remove
    app.remove_snapshot(snapshot)
```

### Custom Callbacks

```python
from snapflow import SnapFlow

def before_copy(database_name):
    print(f"Copying {database_name}...")

app = SnapFlow()
app.create_snapshot('test', before_copy=before_copy)
app.close()
```

## 📞 Getting Help

### Documentation

- **README**: Full project documentation
- **PROJECT_SUMMARY**: Technical details
- **COMPLETION_REPORT**: Implementation details
- **Examples**: See `examples/` directory

### Support Channels

- **GitHub Issues**: Report bugs or request features
- **GitHub Discussions**: Ask questions, share tips
- **Email**: support@quantumdb.dev

### Useful Commands

```bash
# Show version
snapflow version

# Show help
snapflow --help

# Show command help
snapflow snapshot --help
```

## 🎉 You're Ready!

You now know how to:
- ✅ Install and verify SnapFlow
- ✅ Initialize configuration
- ✅ Create and restore snapshots
- ✅ Manage multiple snapshots
- ✅ Use SnapFlow in your workflow
- ✅ Troubleshoot common issues

**Start snapshotting!** 📸

```bash
snapflow snapshot baseline
```

---

**Questions?** Check the [README](README.md) or open an issue on GitHub.

**Happy snapshotting!** 🚀

---

*SnapFlow v1.0.0 - Built with ❤️ by the QuantumDB Team*
