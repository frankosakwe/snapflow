"""
SnapFlow Command Line Interface

User-friendly CLI for managing database snapshots.
"""

import sys
from datetime import datetime, timezone
from time import sleep

import click
import humanize
from sqlalchemy import create_engine
from sqlalchemy.exc import OperationalError

from snapflow.app import SnapFlow, __version__
from snapflow.config import create_default_config
from snapflow.exceptions import (
    InvalidConfigError,
    MissingConfigError,
    SnapshotAlreadyExistsError,
)
from snapflow.operations import SUPPORTED_DIALECTS, database_exists, list_databases


def get_app() -> SnapFlow:
    """
    Create and return a SnapFlow application instance.

    Returns:
        Initialized SnapFlow instance
    """
    try:
        return SnapFlow()
    except MissingConfigError:
        click.echo("❌ Configuration file not found.")
        click.echo("Initialize SnapFlow with: snapflow init")
        sys.exit(1)
    except InvalidConfigError as e:
        click.echo(f"❌ Invalid configuration: {e}")
        sys.exit(1)


@click.group()
@click.version_option(version=__version__, prog_name="SnapFlow")
def cli():
    """
    SnapFlow - Lightning-Fast Database Snapshot Manager

    Create instant database snapshots and restore them effortlessly.
    Perfect for development workflows, migration testing, and data experiments.
    """
    pass


@cli.command()
def version():
    """Display SnapFlow version information"""
    click.echo(f"SnapFlow v{__version__}")
    click.echo("Fast database snapshots for development")


@cli.command()
@click.argument("name", required=False)
@click.option("--description", "-d", help="Optional snapshot description")
def snapshot(name, description):
    """
    Create a new database snapshot

    NAME: Optional snapshot name (auto-generated if not provided)
    """
    app = get_app()

    # Use default name if not provided
    name = name or app.default_snapshot_name

    try:

        def before_copy(db_name):
            click.echo(f"📸 Snapshotting database: {db_name}")

        snapshot_obj = app.create_snapshot(name, description=description, before_copy=before_copy)

        click.echo(f"✅ Snapshot '{name}' created successfully")
        if description:
            click.echo(f"   Description: {description}")
        click.echo(f"   Databases: {len(snapshot_obj.tables)}")
    except SnapshotAlreadyExistsError:
        click.echo(f"❌ Snapshot '{name}' already exists")
        click.echo("   Use 'snapflow list' to see existing snapshots")
        sys.exit(1)
    finally:
        app.close()


@cli.command()
def list():
    """List all snapshots for the current project"""
    app = get_app()

    try:
        snapshots = app.get_all_snapshots()

        if not snapshots:
            click.echo("📭 No snapshots found for this project")
            click.echo("   Create one with: snapflow snapshot")
            return

        click.echo(f"\n📸 Snapshots for project '{app.config['project_name']}':\n")

        for snap in snapshots:
            # Handle both timezone-aware and naive datetimes
            created = snap.created_at
            if created.tzinfo is None:
                created = created.replace(tzinfo=timezone.utc)
            age = humanize.naturaltime(datetime.now(timezone.utc) - created)
            status = "✓" if snap.is_ready else "⏳"

            click.echo(f"  {status} {snap.snapshot_name}")
            click.echo(f"     Created: {age}")

            if snap.description:
                click.echo(f"     Description: {snap.description}")

            db_count = len(snap.tables)
            click.echo(f"     Databases: {db_count}")

            if not snap.is_ready:
                click.echo(f"     Status: Background copy in progress (PID: {snap.worker_pid})")

            click.echo()
    finally:
        app.close()


@cli.command()
@click.argument("name", required=False)
@click.option("--wait/--no-wait", default=True, help="Wait for background copy to complete")
def restore(name, wait):
    """
    Restore database from a snapshot

    NAME: Snapshot name (uses latest if not provided)
    """
    app = get_app()

    try:
        # Get snapshot
        if name:
            snapshot_obj = app.get_snapshot(name)
            if not snapshot_obj:
                click.echo(f"❌ Snapshot '{name}' not found")
                click.echo("   Use 'snapflow list' to see available snapshots")
                sys.exit(1)
        else:
            snapshot_obj = app.get_latest_snapshot()
            if not snapshot_obj:
                click.echo(f"❌ No snapshots found for project '{app.config['project_name']}'")
                click.echo("   Create one with: snapflow snapshot")
                sys.exit(1)
            click.echo(f"Using latest snapshot: {snapshot_obj.snapshot_name}")

        # Check if snapshot is ready
        if not snapshot_obj.is_ready:
            if not wait:
                click.echo("❌ Snapshot not ready (background copy in progress)")
                click.echo("   Run with --wait to wait for completion")
                sys.exit(1)

            if app.is_copy_process_running(snapshot_obj):
                click.echo(
                    f"⏳ Waiting for background copy to complete (PID: {snapshot_obj.worker_pid})"
                )

                with click.progressbar(
                    length=100, label="Copying slave databases", show_eta=False
                ) as bar:
                    while not snapshot_obj.is_ready:
                        sleep(0.5)
                        app.session.refresh(snapshot_obj)
                        bar.update(1)

                click.echo("✓ Background copy complete")
            else:
                click.echo("⚠️  Background process not running, performing inline copy")
                app.inline_slave_copy(snapshot_obj)

        # Perform restore
        click.echo(f"🔄 Restoring from snapshot: {snapshot_obj.snapshot_name}")

        for table in snapshot_obj.tables:
            click.echo(f"   Restoring: {table.table_name}")

        app.restore_snapshot(snapshot_obj)
        click.echo("✅ Restore complete!")
    finally:
        app.close()


@cli.command()
@click.argument("name")
@click.confirmation_option(prompt="Are you sure you want to remove this snapshot?")
def remove(name):
    """
    Remove a snapshot

    NAME: Snapshot name to remove
    """
    app = get_app()

    try:
        snapshot_obj = app.get_snapshot(name)
        if not snapshot_obj:
            click.echo(f"❌ Snapshot '{name}' not found")
            sys.exit(1)

        click.echo(f"🗑️  Removing snapshot: {name}")
        app.remove_snapshot(snapshot_obj)
        click.echo("✅ Snapshot removed")
    finally:
        app.close()


@cli.command()
@click.argument("old_name")
@click.argument("new_name")
def rename(old_name, new_name):
    """
    Rename a snapshot

    OLD_NAME: Current snapshot name
    NEW_NAME: New snapshot name
    """
    app = get_app()

    try:
        snapshot_obj = app.get_snapshot(old_name)
        if not snapshot_obj:
            click.echo(f"❌ Snapshot '{old_name}' not found")
            sys.exit(1)

        try:
            app.rename_snapshot(snapshot_obj, new_name)
            click.echo(f"✅ Renamed: {old_name} → {new_name}")
        except SnapshotAlreadyExistsError:
            click.echo(f"❌ Snapshot '{new_name}' already exists")
            sys.exit(1)
    finally:
        app.close()


@cli.command()
@click.argument("name")
@click.confirmation_option(prompt="Replace existing snapshot with current database state?")
def replace(name):
    """
    Replace an existing snapshot with current database state

    NAME: Snapshot name to replace
    """
    app = get_app()

    try:
        snapshot_obj = app.get_snapshot(name)
        if not snapshot_obj:
            click.echo(f"❌ Snapshot '{name}' not found")
            sys.exit(1)

        click.echo(f"🔄 Replacing snapshot: {name}")

        # Remove old snapshot
        app.remove_snapshot(snapshot_obj)

        # Create new snapshot with same name
        def before_copy(db_name):
            click.echo(f"📸 Snapshotting: {db_name}")

        app.create_snapshot(name, before_copy=before_copy)
        click.echo(f"✅ Snapshot '{name}' replaced")
    finally:
        app.close()


@cli.command()
def gc():
    """
    Garbage collect orphaned snapshot databases

    Removes SnapFlow databases that are no longer associated with any snapshot.
    """
    app = get_app()

    try:
        click.echo("🧹 Cleaning up orphaned databases...")

        def after_delete(db_name):
            click.echo(f"   Removed: {db_name}")

        count = app.cleanup_orphaned_databases(callback=after_delete)

        if count == 0:
            click.echo("✓ No orphaned databases found")
        else:
            click.echo(f"✅ Removed {count} orphaned database(s)")
    finally:
        app.close()


@cli.command()
def init():
    """Initialize SnapFlow configuration for your project"""
    click.echo("🚀 SnapFlow Initialization Wizard\n")

    # Get database URL
    while True:
        click.echo("Enter your database connection URL:")
        click.echo("  PostgreSQL: postgresql://user:pass@localhost:5432/")
        click.echo("  MySQL: mysql+pymysql://root:pass@localhost/")
        click.echo()

        url = click.prompt("Database URL")

        # Normalize URL
        if url.count("/") == 2 and not url.endswith("/"):
            url += "/"

        # Determine connection URL for testing
        if url.count("/") == 3 and url.endswith("/") and url.startswith("postgresql://"):
            connection_url = url + "template1"
        else:
            connection_url = url

        # Test connection
        click.echo("\n🔌 Testing connection...")
        try:
            engine = create_engine(connection_url, echo=False)
            conn = engine.connect()
            click.echo("✅ Connection successful!\n")
            break
        except OperationalError as e:
            click.echo(f"❌ Connection failed: {e}")
            click.echo()
            if not click.confirm("Try again?"):
                sys.exit(1)

    # Check dialect support
    dialect = engine.dialect.name
    if dialect not in SUPPORTED_DIALECTS:
        click.echo(f"⚠️  Warning: Dialect '{dialect}' may not be fully supported")
        click.echo(f"Supported dialects: {', '.join(SUPPORTED_DIALECTS)}")
        click.echo()

    # Get database name
    if url.count("/") == 3 and url.endswith("/"):
        click.echo("Available databases:")
        available_dbs = [
            db
            for db in list_databases(conn)
            if not db.startswith("snapflow_")
            and not db.startswith("template")
            and not db.startswith("postgres")
            and db not in ("mysql", "information_schema", "performance_schema", "sys")
        ]
        for db in available_dbs:
            click.echo(f"  • {db}")
        click.echo()

        while True:
            db_name = click.prompt("Enter database name to track")
            if database_exists(conn, db_name):
                break
            click.echo(f"❌ Database '{db_name}' not found")
    else:
        db_name = url.rsplit("/", 1)[-1]
        url = url.rsplit("/", 1)[0] + "/"

    # Get project name
    project_name = click.prompt("Enter project name", default=db_name)

    # Adjust URL for dialect
    if dialect == "postgresql":
        url = url + "template1" if not url.endswith("template1") else url

    # Create configuration
    create_default_config(
        project_name=project_name, url=url, database_name=db_name, output_path="snapflow.yaml"
    )

    click.echo("\n✅ Configuration saved to snapflow.yaml")
    click.echo()

    if dialect == "mysql":
        click.echo("⚠️  MySQL Support Note:")
        click.echo("   MySQL uses table-by-table copying (slower than PostgreSQL)")
        click.echo()

    click.echo("🎉 SnapFlow is ready!")
    click.echo()
    click.echo("Next steps:")
    click.echo("  1. Add snapflow.yaml to .gitignore")
    click.echo("  2. Create your first snapshot: snapflow snapshot baseline")
    click.echo("  3. Make changes and restore anytime: snapflow restore baseline")


def main():
    """Main entry point for CLI"""
    try:
        cli()
    except KeyboardInterrupt:
        click.echo("\n\n⚠️  Operation cancelled by user")
        sys.exit(130)
    except Exception as e:
        click.echo(f"\n❌ Unexpected error: {e}")
        import traceback

        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
