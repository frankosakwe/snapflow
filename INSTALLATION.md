# SnapFlow Installation Guide

Complete installation instructions for all platforms and use cases.

## Table of Contents

- [System Requirements](#system-requirements)
- [Installation Methods](#installation-methods)
- [Database Drivers](#database-drivers)
- [Verification](#verification)
- [Troubleshooting](#troubleshooting)
- [Upgrade](#upgrade)
- [Uninstallation](#uninstallation)

## System Requirements

### Minimum Requirements

- **Python**: 3.8 or higher
- **Operating System**: Linux, macOS, or Windows
- **Memory**: 100 MB RAM (plus database size × 2)
- **Disk Space**: Sufficient for 2× your database size per snapshot

### Recommended

- **Python**: 3.10 or higher
- **SSD Storage**: For faster database copying
- **Database Permissions**: CREATE DATABASE privilege

## Installation Methods

### Method 1: From Source (Recommended for Development)

```bash
# Clone the repository
git clone https://github.com/quantumdb/snapflow.git
cd snapflow

# Create virtual environment (recommended)
python -m venv venv

# Activate virtual environment
# On Linux/macOS:
source venv/bin/activate
# On Windows:
venv\Scripts\activate

# Install in editable mode
pip install -e .
```

### Method 2: From PyPI (When Published)

```bash
# Install latest release
pip install snapflow

# Install specific version
pip install snapflow==1.0.0

# Install with extras
pip install snapflow[postgresql]  # PostgreSQL support
pip install snapflow[mysql]       # MySQL support
pip install snapflow[dev]         # Development tools
```

### Method 3: From GitHub Release

```bash
# Download release tarball
wget https://github.com/quantumdb/snapflow/archive/v1.0.0.tar.gz

# Extract
tar -xzf v1.0.0.tar.gz
cd snapflow-1.0.0

# Install
pip install .
```

### Method 4: Development Installation

For contributors and developers:

```bash
# Clone repository
git clone https://github.com/quantumdb/snapflow.git
cd snapflow

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install with all development dependencies
pip install -e ".[dev]"

# Or using make
make dev-install
```

## Database Drivers

SnapFlow requires database-specific drivers. Install based on your database:

### PostgreSQL

**Option 1: Binary Package (Recommended)**
```bash
pip install psycopg2-binary
```

**Option 2: From Source (Better Performance)**
```bash
# Install PostgreSQL development headers first
# Ubuntu/Debian:
sudo apt-get install libpq-dev python3-dev

# macOS:
brew install postgresql

# Windows:
# Download PostgreSQL from postgresql.org

# Then install psycopg2
pip install psycopg2
```

### MySQL

**PyMySQL (Recommended)**
```bash
pip install PyMySQL
```

**MySQL Connector**
```bash
pip install mysql-connector-python
```

**MySQLdb (Advanced)**
```bash
# Requires MySQL development headers
pip install mysqlclient
```

### SQLite

SQLite support is built into Python, no additional driver needed!

## Platform-Specific Installation

### Ubuntu/Debian

```bash
# Install system dependencies
sudo apt-get update
sudo apt-get install python3 python3-pip python3-venv

# For PostgreSQL
sudo apt-get install libpq-dev

# For MySQL
sudo apt-get install libmysqlclient-dev

# Install SnapFlow
pip3 install snapflow psycopg2-binary PyMySQL
```

### macOS

```bash
# Install Homebrew (if not installed)
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

# Install Python
brew install python

# For PostgreSQL
brew install postgresql

# For MySQL
brew install mysql

# Install SnapFlow
pip3 install snapflow psycopg2-binary PyMySQL
```

### Windows

```powershell
# Install Python from python.org (if not installed)
# Make sure to check "Add Python to PATH"

# Install SnapFlow
pip install snapflow psycopg2-binary PyMySQL
```

### Docker

Create a `Dockerfile`:

```dockerfile
FROM python:3.11-slim

# Install system dependencies
RUN apt-get update && apt-get install -y \
    libpq-dev \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Install SnapFlow
RUN pip install snapflow psycopg2-binary PyMySQL

# Set working directory
WORKDIR /app

# Entry point
ENTRYPOINT ["snapflow"]
CMD ["--help"]
```

Build and run:

```bash
docker build -t snapflow .
docker run -v $(pwd):/app snapflow init
```

## Verification

### Quick Verification

```bash
# Check installation
python -c "import snapflow; print('SnapFlow', snapflow.__version__)"

# Check CLI
snapflow --version

# Full verification
python scripts/verify_installation.py
```

### Expected Output

```
SnapFlow 1.0.0

============================================================
SnapFlow Installation Verification
============================================================
Checking Python version...
  ✓ Python 3.12.10

Checking module imports...
  ✓ SnapFlow core
  ✓ Application module
  ✓ CLI module
  ...

============================================================
✓ All checks passed! SnapFlow is installed correctly.
============================================================
```

## Troubleshooting

### Issue: "No module named 'snapflow'"

**Solution:**
```bash
# Reinstall SnapFlow
pip install --upgrade --force-reinstall snapflow

# Or if installed from source
cd snapflow
pip install -e .
```

### Issue: "Command 'snapflow' not found"

**Solution:**
```bash
# Ensure Python scripts directory is in PATH
# On Linux/macOS:
export PATH="$HOME/.local/bin:$PATH"

# On Windows, add to PATH:
# C:\Users\YourName\AppData\Local\Programs\Python\Python312\Scripts

# Or run as module
python -m snapflow --version
```

### Issue: Import errors for database drivers

**PostgreSQL: "No module named 'psycopg2'"**
```bash
pip install psycopg2-binary
```

**MySQL: "No module named 'pymysql'"**
```bash
pip install PyMySQL
```

### Issue: Permission errors on Unix

**Solution:**
```bash
# Install for user only
pip install --user snapflow

# Or use virtual environment
python -m venv venv
source venv/bin/activate
pip install snapflow
```

### Issue: SSL certificate errors

**Solution:**
```bash
# Upgrade pip and certifi
pip install --upgrade pip certifi

# Or disable SSL verification (not recommended)
pip install --trusted-host pypi.org --trusted-host files.pythonhosted.org snapflow
```

### Issue: "error: Microsoft Visual C++ 14.0 is required" (Windows)

**Solution:**
1. Install Microsoft C++ Build Tools
2. Or use pre-built wheels: `pip install psycopg2-binary`

### Issue: Build failures on macOS

**Solution:**
```bash
# Install Xcode Command Line Tools
xcode-select --install

# Update setuptools and pip
pip install --upgrade setuptools pip

# Reinstall
pip install snapflow
```

## Upgrade

### Upgrade to Latest Version

```bash
# From PyPI
pip install --upgrade snapflow

# From source
cd snapflow
git pull origin main
pip install --upgrade -e .
```

### Upgrade with Dependencies

```bash
pip install --upgrade snapflow[postgresql,mysql]
```

### Check for Updates

```bash
pip list --outdated | grep snapflow
```

## Uninstallation

### Remove SnapFlow

```bash
# Uninstall package
pip uninstall snapflow

# Remove configuration (optional)
rm -f snapflow.yaml
rm -f ~/.snapflow/config.yaml

# Remove virtual environment (if created)
rm -rf venv
```

### Clean Uninstall

```bash
# Remove all SnapFlow files
pip uninstall snapflow
rm -rf ~/.snapflow
rm -f snapflow.yaml
find . -name 'snapflow_*' -type d -exec rm -rf {} +
```

## Post-Installation

### First Steps

```bash
# 1. Verify installation
snapflow --version

# 2. Initialize your project
cd your-project
snapflow init

# 3. Create your first snapshot
snapflow snapshot baseline

# 4. Test restore
snapflow restore baseline
```

### Configuration

Create a `.snapflowrc` file in your home directory for global settings:

```yaml
# ~/.snapflowrc
default_description: true
auto_gc: false
logging: INFO
```

### Shell Completion (Optional)

**Bash:**
```bash
_SNAPFLOW_COMPLETE=bash_source snapflow > ~/.snapflow-complete.bash
echo ". ~/.snapflow-complete.bash" >> ~/.bashrc
```

**Zsh:**
```bash
_SNAPFLOW_COMPLETE=zsh_source snapflow > ~/.snapflow-complete.zsh
echo ". ~/.snapflow-complete.zsh" >> ~/.zshrc
```

**Fish:**
```bash
_SNAPFLOW_COMPLETE=fish_source snapflow > ~/.config/fish/completions/snapflow.fish
```

## Getting Help

- **Documentation**: See [README.md](README.md)
- **Quick Start**: See [QUICKSTART.md](QUICKSTART.md)
- **Issues**: https://github.com/quantumdb/snapflow/issues
- **Discussions**: https://github.com/quantumdb/snapflow/discussions

## Next Steps

1. ✅ Install SnapFlow
2. ✅ Verify installation
3. 📖 Read [QUICKSTART.md](QUICKSTART.md)
4. 🎓 Try the demo in `demo/`
5. 🚀 Use SnapFlow in your projects!

---

**Need help?** Open an issue on GitHub or check the troubleshooting section.
