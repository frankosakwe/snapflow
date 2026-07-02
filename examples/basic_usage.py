"""
SnapFlow Basic Usage Examples

This script demonstrates how to use SnapFlow programmatically.
"""

from snapflow import SnapFlow, load_config
from snapflow.exceptions import SnapshotNotFoundError, SnapshotAlreadyExistsError


def example_basic_workflow():
    """
    Example: Basic snapshot creation and restoration workflow
    """
    print("=== Basic Workflow Example ===\n")
    
    # Initialize SnapFlow (loads config from snapflow.yaml)
    app = SnapFlow()
    
    # Create a snapshot
    print("Creating snapshot 'baseline'...")
    try:
        snapshot = app.create_snapshot('baseline', description='Initial database state')
        print(f"✓ Snapshot created: {snapshot.snapshot_name}")
        print(f"  Hash: {snapshot.hash}")
        print(f"  Tables: {len(snapshot.tables)}")
    except SnapshotAlreadyExistsError:
        print("✗ Snapshot already exists")
    
    # List all snapshots
    print("\nListing all snapshots...")
    snapshots = app.get_all_snapshots()
    for snap in snapshots:
        print(f"  - {snap.snapshot_name} ({snap.created_at})")
    
    # Restore from snapshot
    print("\nRestoring from 'baseline'...")
    snapshot = app.get_snapshot('baseline')
    if snapshot:
        app.restore_snapshot(snapshot)
        print("✓ Restore complete")
    else:
        print("✗ Snapshot not found")
    
    # Clean up
    app.close()


def example_context_manager():
    """
    Example: Using SnapFlow as a context manager
    """
    print("\n=== Context Manager Example ===\n")
    
    with SnapFlow() as app:
        # Get latest snapshot
        latest = app.get_latest_snapshot()
        if latest:
            print(f"Latest snapshot: {latest.snapshot_name}")
            print(f"Created: {latest.created_at}")
            print(f"Ready: {latest.is_ready}")
        else:
            print("No snapshots found")


def example_snapshot_management():
    """
    Example: Advanced snapshot management
    """
    print("\n=== Snapshot Management Example ===\n")
    
    with SnapFlow() as app:
        # Create multiple snapshots
        for i in range(3):
            snapshot_name = f"test_snap_{i}"
            try:
                app.create_snapshot(
                    snapshot_name,
                    description=f"Test snapshot #{i}"
                )
                print(f"✓ Created: {snapshot_name}")
            except SnapshotAlreadyExistsError:
                print(f"  Skipped {snapshot_name} (already exists)")
        
        # Rename a snapshot
        print("\nRenaming snapshot...")
        snapshot = app.get_snapshot('test_snap_0')
        if snapshot:
            app.rename_snapshot(snapshot, 'renamed_snapshot')
            print("✓ Snapshot renamed")
        
        # Remove a snapshot
        print("\nRemoving snapshot...")
        snapshot = app.get_snapshot('test_snap_1')
        if snapshot:
            app.remove_snapshot(snapshot)
            print("✓ Snapshot removed")
        
        # Clean up orphaned databases
        print("\nCleaning up orphaned databases...")
        count = app.cleanup_orphaned_databases()
        print(f"✓ Removed {count} orphaned databases")


def example_error_handling():
    """
    Example: Proper error handling
    """
    print("\n=== Error Handling Example ===\n")
    
    try:
        with SnapFlow() as app:
            # Try to restore non-existent snapshot
            try:
                snapshot = app.get_snapshot('nonexistent')
                if not snapshot:
                    raise SnapshotNotFoundError('nonexistent')
                app.restore_snapshot(snapshot)
            except SnapshotNotFoundError as e:
                print(f"✗ Error: {e}")
            
            # Try to create duplicate snapshot
            try:
                app.create_snapshot('baseline')
                app.create_snapshot('baseline')  # Will fail
            except SnapshotAlreadyExistsError as e:
                print(f"✗ Error: {e}")
    
    except Exception as e:
        print(f"✗ Unexpected error: {e}")


def example_custom_callbacks():
    """
    Example: Using callbacks for progress tracking
    """
    print("\n=== Custom Callbacks Example ===\n")
    
    def before_copy_callback(database_name):
        print(f"  📸 Snapshotting: {database_name}")
    
    def cleanup_callback(database_name):
        print(f"  🗑️  Removed: {database_name}")
    
    with SnapFlow() as app:
        # Create snapshot with callback
        print("Creating snapshot with progress tracking...")
        snapshot = app.create_snapshot(
            'callback_example',
            before_copy=before_copy_callback
        )
        
        # Cleanup with callback
        print("\nCleaning up...")
        app.cleanup_orphaned_databases(callback=cleanup_callback)


def example_snapshot_info():
    """
    Example: Getting detailed snapshot information
    """
    print("\n=== Snapshot Information Example ===\n")
    
    with SnapFlow() as app:
        snapshots = app.get_all_snapshots()
        
        for snapshot in snapshots:
            print(f"\nSnapshot: {snapshot.snapshot_name}")
            print(f"  Project: {snapshot.project_name}")
            print(f"  Created: {snapshot.created_at}")
            print(f"  Age: {snapshot.age:.1f} seconds")
            print(f"  Ready: {snapshot.is_ready}")
            print(f"  Description: {snapshot.description or 'N/A'}")
            print(f"  Databases:")
            
            for table in snapshot.tables:
                size_mb = table.size_bytes / (1024 * 1024) if table.size_bytes else 0
                print(f"    - {table.table_name} ({size_mb:.2f} MB)")
                print(f"      Master: {table.get_master_name()}")
                print(f"      Slave: {table.get_slave_name()}")


if __name__ == '__main__':
    print("SnapFlow Usage Examples")
    print("=" * 50)
    
    # Note: Make sure you have initialized SnapFlow first:
    # snapflow init
    
    try:
        example_basic_workflow()
        example_context_manager()
        example_snapshot_management()
        example_error_handling()
        example_custom_callbacks()
        example_snapshot_info()
        
        print("\n" + "=" * 50)
        print("All examples completed!")
    
    except Exception as e:
        print(f"\nError running examples: {e}")
        print("Make sure you have:")
        print("1. Initialized SnapFlow: snapflow init")
        print("2. Created at least one snapshot: snapflow snapshot baseline")
