# SnapFlow Demo Workflow

This guide walks you through a complete SnapFlow demo using a SQLite database.

## Prerequisites

```bash
# Ensure SnapFlow is installed
pip install -e .

# Verify installation
python scripts/verify_installation.py
```

## Demo Setup

### Step 1: Create Demo Database

```bash
cd demo
python demo_setup.py create
```

This creates a SQLite database with:
- **users** table (5 users)
- **posts** table (5 posts)
- **settings** table (3 settings)

### Step 2: Initialize SnapFlow

```bash
# Create configuration
cat > snapflow.yaml << EOF
project_name: 'demo_project'
tracked_databases: ['demo_database']
url: 'sqlite:///demo_database.db'
snapflow_url: 'sqlite:///snapflow_data.db'
logging: 20
EOF
```

Or use the interactive wizard:
```bash
snapflow init
```

## Demo Workflow

### Scenario: Testing Database Changes

#### 1. Create Initial Snapshot

```bash
# Create a baseline snapshot
snapflow snapshot baseline --description "Initial clean state"
```

Output:
```
📸 Snapshotting database: demo_database
✅ Snapshot 'baseline' created successfully
   Description: Initial clean state
   Databases: 1
```

#### 2. List Snapshots

```bash
snapflow list
```

Output:
```
📸 Snapshots for project 'demo_project':

  ✓ baseline
     Created: just now
     Description: Initial clean state
     Databases: 1
```

#### 3. Make Changes to Database

```bash
# Modify the database
python demo_setup.py modify
```

This will:
- Add a new user 'frank'
- Change theme from 'dark' to 'light'
- Delete post #3

```bash
# Verify changes
python demo_setup.py show
```

#### 4. Create Another Snapshot

```bash
snapflow snapshot after-changes --description "After adding frank and modifying settings"
```

#### 5. Make More Changes (Simulate a Mistake)

```bash
# Using SQLite CLI or Python
sqlite3 demo_database.db "DELETE FROM users WHERE username = 'alice'"
sqlite3 demo_database.db "UPDATE settings SET value = 'broken' WHERE key = 'theme'"
```

```bash
# Verify the "mistake"
python demo_setup.py show
```

#### 6. Restore from Snapshot

```bash
# Oops! Let's restore to our baseline
snapflow restore baseline
```

Output:
```
Using latest snapshot: baseline
🔄 Restoring from snapshot: baseline
   Restoring: demo_database
✅ Restore complete!
```

```bash
# Verify restoration
python demo_setup.py show
```

Everything is back to the original state!

#### 7. List All Snapshots

```bash
snapflow list
```

Output:
```
📸 Snapshots for project 'demo_project':

  ✓ after-changes
     Created: 2 minutes ago
     Description: After adding frank and modifying settings
     Databases: 1

  ✓ baseline
     Created: 5 minutes ago
     Description: Initial clean state
     Databases: 1
```

#### 8. Rename a Snapshot

```bash
snapflow rename after-changes modified-state
```

#### 9. Replace a Snapshot

```bash
# Make some changes
python demo_setup.py modify

# Replace the baseline with current state
snapflow replace baseline
```

#### 10. Clean Up

```bash
# Remove old snapshots
snapflow remove modified-state

# Clean up orphaned databases
snapflow gc
```

## Advanced Demo: Branch Switching Simulation

### Scenario: Working on Multiple Features

```bash
# 1. Create feature-A snapshot
python demo_setup.py modify
snapflow snapshot feature-a --description "Feature A changes"

# 2. Restore to baseline
snapflow restore baseline

# 3. Create feature-B snapshot (different changes)
sqlite3 demo_database.db "UPDATE settings SET value = 'blue' WHERE key = 'theme'"
snapflow snapshot feature-b --description "Feature B changes"

# 4. Switch between features
snapflow restore feature-a   # Work on feature A
snapflow restore feature-b   # Work on feature B
snapflow restore baseline    # Back to main
```

## Programmatic Demo

Create a file `demo_api.py`:

```python
from snapflow import SnapFlow

# Initialize SnapFlow
with SnapFlow() as app:
    # Create snapshot
    print("Creating snapshot...")
    snapshot = app.create_snapshot(
        'api-demo',
        description='Created via API'
    )
    print(f"✓ Created: {snapshot.snapshot_name}")
    
    # List snapshots
    print("\nAll snapshots:")
    for snap in app.get_all_snapshots():
        print(f"  - {snap.snapshot_name} ({snap.created_at})")
    
    # Restore snapshot
    print("\nRestoring snapshot...")
    app.restore_snapshot(snapshot)
    print("✓ Restored")
    
    # Clean up
    print("\nRemoving snapshot...")
    app.remove_snapshot(snapshot)
    print("✓ Removed")
```

Run it:
```bash
python demo_api.py
```

## Performance Demo

Test SnapFlow's speed:

```bash
# Create a larger database
python -c "
import sqlite3
conn = sqlite3.connect('large_demo.db')
cursor = conn.cursor()
cursor.execute('CREATE TABLE test (id INTEGER PRIMARY KEY, data TEXT)')
cursor.executemany('INSERT INTO test (data) VALUES (?)', 
                   [(f'data{i}',) for i in range(10000)])
conn.commit()
conn.close()
"

# Time traditional backup
time sqlite3 large_demo.db .dump > backup.sql
time sqlite3 restored.db < backup.sql

# Time SnapFlow
time snapflow snapshot speed-test
time snapflow restore speed-test
```

SnapFlow is significantly faster for restores!

## Demo Cleanup

```bash
# Remove all demo files
rm -f demo_database.db
rm -f snapflow_data.db
rm -f snapflow.yaml
rm -f large_demo.db
rm -f backup.sql
rm -f restored.db
```

## Key Takeaways

1. **Fast Snapshots**: Create snapshots in seconds
2. **Instant Restores**: Restore in microseconds (just renames the database)
3. **Safe Experiments**: Try anything without fear
4. **Branch Switching**: Easy context switching between features
5. **Simple API**: Both CLI and programmatic access

## Next Steps

1. Try SnapFlow with your real project database
2. Integrate into your development workflow
3. Add to CI/CD pipeline
4. Share with your team

---

**Demo created for SnapFlow v1.0.0**
