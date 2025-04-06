#!/usr/bin/env python3
"""
Database initialization script.
Creates default roles and admin user if they don't exist.
"""
import os

from dotenv import load_dotenv

from backend.app.auth import get_password_hash
from backend.app.db.database import get_db
from backend.app.db.models.auth import Role, User

# Load environment variables
load_dotenv()

# Default admin credentials
ADMIN_USERNAME = os.getenv("ADMIN_USERNAME", "admin")
ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD", "password")
ADMIN_EMAIL = os.getenv("ADMIN_EMAIL", "admin@example.com")


def init_db():
    """Initialize database with default roles and admin user"""
    # Get DB session
    db = next(get_db())

    # Create default roles if they don't exist
    roles = {
        "admin": "Full access to all resources",
        "league_manager": "Manage teams, players, games, and stats",
        "stat_keeper": "Enter and edit game statistics",
    }

    role_objs = {}
    for name, description in roles.items():
        role = db.query(Role).filter(Role.name == name).first()
        if not role:
            role = Role(name=name, description=description)
            db.add(role)
            print(f"Created role: {name}")
        role_objs[name] = role

    # Create admin user if it doesn't exist
    admin_user = db.query(User).filter(User.username == ADMIN_USERNAME).first()
    if not admin_user:
        admin_user = User(
            username=ADMIN_USERNAME,
            email=ADMIN_EMAIL,
            password_hash=get_password_hash(ADMIN_PASSWORD),
            is_active=True,
        )
        admin_user.roles = [role_objs["admin"]]
        db.add(admin_user)
        print(f"Created admin user: {ADMIN_USERNAME}")

    # Commit changes
    db.commit()
    print("Database initialization completed")


def main():
    """Main entry point"""
    init_db()


if __name__ == "__main__":
    main()
