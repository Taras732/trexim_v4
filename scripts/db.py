#!/usr/bin/env python3
"""
Database management script

Usage:
    python scripts/db.py init        # Initialize tables (dev only)
    python scripts/db.py migrate     # Run pending migrations
    python scripts/db.py revision    # Create new migration
    python scripts/db.py status      # Show migration status
    python scripts/db.py downgrade   # Rollback last migration
"""
import sys
import os
import subprocess
import argparse

# Add app directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from app.config import settings


def run_alembic(*args):
    """Run alembic command"""
    cmd = ["alembic"] + list(args)
    print(f"Running: {' '.join(cmd)}")
    subprocess.run(cmd, cwd=os.path.dirname(os.path.dirname(__file__)))


def init_db():
    """Initialize database tables (development only)"""
    if settings.APP_ENV == "production":
        print("Error: Use migrations in production!")
        print("Run: python scripts/db.py migrate")
        return

    print("Initializing database tables...")
    from app.database import init_db as _init_db
    _init_db()
    print("Done! Tables created.")


def migrate():
    """Run pending migrations"""
    print(f"Database: {settings.DATABASE_URL}")
    run_alembic("upgrade", "head")


def revision(message: str = None):
    """Create new migration"""
    if not message:
        message = input("Migration message: ").strip()
        if not message:
            print("Error: Message is required")
            return

    run_alembic("revision", "--autogenerate", "-m", message)


def status():
    """Show migration status"""
    print(f"Database: {settings.DATABASE_URL}")
    run_alembic("current")
    print("\nPending migrations:")
    run_alembic("history", "--verbose")


def downgrade(revision: str = "-1"):
    """Rollback migration"""
    print(f"Rolling back to: {revision}")
    run_alembic("downgrade", revision)


def main():
    parser = argparse.ArgumentParser(description="Trexim Database Management")
    parser.add_argument("command", choices=["init", "migrate", "revision", "status", "downgrade"],
                        help="Command to run")
    parser.add_argument("-m", "--message", help="Migration message (for revision)")
    parser.add_argument("-r", "--revision", default="-1", help="Revision to downgrade to")

    args = parser.parse_args()

    print(f"\n=== Trexim Database Management ===")
    print(f"Environment: {settings.APP_ENV}")
    print(f"Database: {settings.DATABASE_URL[:50]}...\n")

    if args.command == "init":
        init_db()
    elif args.command == "migrate":
        migrate()
    elif args.command == "revision":
        revision(args.message)
    elif args.command == "status":
        status()
    elif args.command == "downgrade":
        downgrade(args.revision)


if __name__ == "__main__":
    main()
