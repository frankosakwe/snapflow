"""
SnapFlow Demo Setup

This script creates a demo SQLite database to demonstrate SnapFlow functionality.
Run this before running the demo.
"""

import sqlite3
import random
from pathlib import Path


def create_demo_database(db_path='demo_database.db'):
    """
    Create a demo SQLite database with sample data.
    
    Args:
        db_path: Path to the database file
    """
    # Remove existing database
    if Path(db_path).exists():
        Path(db_path).unlink()
    
    print(f"Creating demo database: {db_path}")
    
    # Connect to database
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Create users table
    print("  Creating users table...")
    cursor.execute('''
        CREATE TABLE users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL UNIQUE,
            email TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Insert sample users
    print("  Inserting sample users...")
    users = [
        ('alice', 'alice@example.com'),
        ('bob', 'bob@example.com'),
        ('charlie', 'charlie@example.com'),
        ('diana', 'diana@example.com'),
        ('eve', 'eve@example.com'),
    ]
    
    cursor.executemany(
        'INSERT INTO users (username, email) VALUES (?, ?)',
        users
    )
    
    # Create posts table
    print("  Creating posts table...")
    cursor.execute('''
        CREATE TABLE posts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            title TEXT NOT NULL,
            content TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id)
        )
    ''')
    
    # Insert sample posts
    print("  Inserting sample posts...")
    titles = [
        "Getting Started with SnapFlow",
        "Database Snapshots Made Easy",
        "Why I Love Fast Restores",
        "Testing Migrations with SnapFlow",
        "Developer Workflow Tips",
    ]
    
    for i, title in enumerate(titles, 1):
        cursor.execute(
            'INSERT INTO posts (user_id, title, content) VALUES (?, ?, ?)',
            (random.randint(1, 5), title, f"Content for post {i}")
        )
    
    # Create settings table
    print("  Creating settings table...")
    cursor.execute('''
        CREATE TABLE settings (
            key TEXT PRIMARY KEY,
            value TEXT NOT NULL
        )
    ''')
    
    cursor.executemany(
        'INSERT INTO settings (key, value) VALUES (?, ?)',
        [
            ('app_name', 'SnapFlow Demo'),
            ('version', '1.0.0'),
            ('theme', 'dark'),
        ]
    )
    
    # Commit and close
    conn.commit()
    conn.close()
    
    print(f"✅ Demo database created successfully!")
    print(f"   Database: {db_path}")
    print(f"   Tables: users (5 rows), posts (5 rows), settings (3 rows)")


def show_database_contents(db_path='demo_database.db'):
    """Display contents of the demo database."""
    
    if not Path(db_path).exists():
        print(f"❌ Database not found: {db_path}")
        return
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    print(f"\n📊 Database Contents: {db_path}\n")
    
    # Show users
    print("Users Table:")
    cursor.execute('SELECT id, username, email FROM users')
    for row in cursor.fetchall():
        print(f"  {row[0]}: {row[1]} <{row[2]}>")
    
    # Show posts
    print("\nPosts Table:")
    cursor.execute('SELECT id, user_id, title FROM posts')
    for row in cursor.fetchall():
        print(f"  {row[0]}: {row[2]} (by user {row[1]})")
    
    # Show settings
    print("\nSettings Table:")
    cursor.execute('SELECT key, value FROM settings')
    for row in cursor.fetchall():
        print(f"  {row[0]}: {row[1]}")
    
    conn.close()
    print()


def modify_database(db_path='demo_database.db'):
    """Make some modifications to the database for demo purposes."""
    
    if not Path(db_path).exists():
        print(f"❌ Database not found: {db_path}")
        return
    
    print(f"\n🔧 Making modifications to database...\n")
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Add a new user
    print("  Adding new user 'frank'...")
    cursor.execute(
        'INSERT INTO users (username, email) VALUES (?, ?)',
        ('frank', 'frank@example.com')
    )
    
    # Update a setting
    print("  Changing theme to 'light'...")
    cursor.execute(
        'UPDATE settings SET value = ? WHERE key = ?',
        ('light', 'theme')
    )
    
    # Delete a post
    print("  Deleting post #3...")
    cursor.execute('DELETE FROM posts WHERE id = 3')
    
    conn.commit()
    conn.close()
    
    print("\n✅ Modifications complete!")


if __name__ == '__main__':
    import sys
    
    print("=" * 60)
    print("SnapFlow Demo Setup")
    print("=" * 60)
    
    if len(sys.argv) > 1:
        command = sys.argv[1]
        
        if command == 'create':
            create_demo_database()
            show_database_contents()
        elif command == 'show':
            show_database_contents()
        elif command == 'modify':
            modify_database()
            show_database_contents()
        else:
            print(f"Unknown command: {command}")
            print("Usage: python demo_setup.py [create|show|modify]")
    else:
        print("\nCommands:")
        print("  python demo_setup.py create  - Create demo database")
        print("  python demo_setup.py show    - Show database contents")
        print("  python demo_setup.py modify  - Modify database")
        print("\nDefault action: create")
        print()
        
        create_demo_database()
        show_database_contents()
