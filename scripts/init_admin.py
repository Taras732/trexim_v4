#!/usr/bin/env python3
"""
Admin user initialization script

Usage:
    python scripts/init_admin.py                    # Interactive mode
    python scripts/init_admin.py -u admin -p pass   # Command line mode
    python scripts/init_admin.py --list             # List all users
    python scripts/init_admin.py --reset admin      # Reset password for user
"""
import sys
import os
import getpass
import argparse

# Add app directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from app.admin.users import (
    create_user,
    get_all_users,
    user_exists,
    update_password,
    get_user_by_username
)


def list_users():
    """List all admin users"""
    users = get_all_users()
    if not users:
        print("No users found.")
        return

    print("\nAdmin Users:")
    print("-" * 60)
    for user in users:
        status = "Active" if user["is_active"] else "Inactive"
        last_login = user["last_login"] or "Never"
        print(f"  {user['username']:15} | {user['role']:10} | {status:8} | Last: {last_login[:19]}")
    print("-" * 60)
    print(f"Total: {len(users)} users\n")


def create_admin_user(username: str = None, password: str = None, email: str = None):
    """Create a new admin user"""
    if not username:
        username = input("Username: ").strip()
        if not username:
            print("Error: Username is required")
            return False

    if get_user_by_username(username):
        print(f"Error: User '{username}' already exists")
        return False

    if not password:
        password = getpass.getpass("Password: ")
        password_confirm = getpass.getpass("Confirm password: ")
        if password != password_confirm:
            print("Error: Passwords don't match")
            return False

    if len(password) < 8:
        print("Error: Password must be at least 8 characters")
        return False

    if not email:
        email = input("Email (optional): ").strip() or None

    user_id = create_user(username, password, email=email, role="admin")
    if user_id:
        print(f"\nSuccess! Admin user '{username}' created (ID: {user_id})")
        return True
    else:
        print("Error: Failed to create user")
        return False


def reset_password(username: str):
    """Reset password for existing user"""
    if not get_user_by_username(username):
        print(f"Error: User '{username}' not found")
        return False

    password = getpass.getpass("New password: ")
    password_confirm = getpass.getpass("Confirm new password: ")

    if password != password_confirm:
        print("Error: Passwords don't match")
        return False

    if len(password) < 8:
        print("Error: Password must be at least 8 characters")
        return False

    if update_password(username, password):
        print(f"\nSuccess! Password for '{username}' has been updated")
        return True
    else:
        print("Error: Failed to update password")
        return False


def main():
    parser = argparse.ArgumentParser(description="Trexim Admin User Management")
    parser.add_argument("-u", "--username", help="Username for new admin")
    parser.add_argument("-p", "--password", help="Password for new admin")
    parser.add_argument("-e", "--email", help="Email for new admin")
    parser.add_argument("--list", action="store_true", help="List all users")
    parser.add_argument("--reset", metavar="USERNAME", help="Reset password for user")

    args = parser.parse_args()

    print("\n=== Trexim Admin User Management ===\n")

    if args.list:
        list_users()
        return

    if args.reset:
        reset_password(args.reset)
        return

    # Create new user
    if args.username and args.password:
        create_admin_user(args.username, args.password, args.email)
    else:
        # Interactive mode
        if not user_exists():
            print("No admin users found. Let's create the first one.\n")
        else:
            print("Creating new admin user.\n")
            list_users()

        create_admin_user(args.username, args.password, args.email)


if __name__ == "__main__":
    main()
