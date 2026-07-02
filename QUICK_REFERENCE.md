# SnapFlow Quick Reference

## 🚀 Installation

```bash
cd "C:\Users\USER\OneDrive\Music\st 1\snapflow"
pip install -e .
python verify_snapflow.py
```

## ⚡ Quick Commands

| Command | Description |
|---------|-------------|
| `snapflow init` | Initialize configuration |
| `snapflow snapshot [name]` | Create snapshot |
| `snapflow list` | List all snapshots |
| `snapflow restore [name]` | Restore snapshot |
| `snapflow remove <name>` | Delete snapshot |
| `snapflow rename <old> <new>` | Rename snapshot |
| `snapflow replace <name>` | Replace snapshot |
| `snapflow gc` | Cleanup orphaned databases |
| `snapflow version` | Show version |

## 📝 Common Workflows

### First Time Setup

```bash
# 1. Go to your project
cd C:\path\to\your\project

# 2. Initialize SnapFlow
snapflow init

# 3. Create baseline
snapflow snapshot baseline
```

### Daily Development

```bash
# Before making changes
snapflow snapshot before-changes

# Make changes...

# If something breaks
snapflow restore before-changes
```

### Migration Testing

```bash
# 1. Snapshot before migration
snapflow snapshot before-migration

# 2. Run migration
python manage.py migrate

# 3. Test it...

# 4. Restore if needed
snapflow restore before-migration
```

## 🔧 Configuration

### Location

```
Current directory or parent: snapflow.yaml
```

### Example

```yaml
project_name: 'myproject'
tracked_databases: ['mydb']
url: 'postgresql://localhost:5432/template1'
snapflow_url: 'postgresql://localhost:5432/snapflow_data'
```

## 🐛 Troubleshooting

### Access Denied

```sql
-- PostgreSQL
ALTER USER myuser CREATEDB;

-- MySQL
GRANT ALL PRIVILEGES ON *.* TO 'myuser'@'localhost';
```

### Verify Installation

```bash
python verify_snapflow.py
```

### Run Tests

```bash
python run_tests.py
```

## 📚 Documentation

| File | Purpose |
|------|---------|
| `README.md` | Complete guide |
| `GETTING_STARTED.md` | Quick start |
| `PROJECT_SUMMARY.md` | Technical details |
| `COMPLETION_REPORT.md` | Implementation report |

## 💡 Pro Tips

1. **Add to .gitignore**: `echo snapflow.yaml >> .gitignore`
2. **Use descriptive names**: `snapflow snapshot user-migration-ready`
3. **Clean up old snapshots**: `snapflow gc` regularly
4. **Snapshot before risky operations**: Always!

## 🎯 One-Liners

```bash
# Quick snapshot & restore
snapflow snapshot temp && snapflow restore temp

# Create & list
snapflow snapshot test && snapflow list

# Replace existing
snapflow replace baseline

# Remove old snapshots
snapflow remove snap1 snap2 snap3
```

## ✅ Verification Checklist

- [ ] Installed: `pip install -e .`
- [ ] Verified: `python verify_snapflow.py`
- [ ] Initialized: `snapflow init`
- [ ] Created snapshot: `snapflow snapshot baseline`
- [ ] Listed snapshots: `snapflow list`
- [ ] Restored: `snapflow restore baseline`

## 🆘 Help

```bash
snapflow --help
snapflow snapshot --help
```

---

**SnapFlow v1.0.0** | QuantumDB | MIT License
