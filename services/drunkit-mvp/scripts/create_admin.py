"""
Creates the first PLATFORM_ADMIN account. There is deliberately no
public API endpoint for this — the very first admin has to come from
somewhere with direct database access, not a self-service form.

Run once per environment, after `alembic upgrade head`:

    python -m scripts.create_admin --email admin@yourcompany.com

You'll be prompted for a password (not passed as a CLI arg, so it
doesn't end up in shell history or process listings).
"""
from __future__ import annotations

import argparse
import getpass
import sys

from app.db.models import StaffRole
from app.db.session import SessionLocal
from app.domain.staff_auth.service import StaffAuthError, create_staff_user


def main() -> None:
    parser = argparse.ArgumentParser(description="Create the first platform admin account.")
    parser.add_argument("--email", required=True, help="Admin login email.")
    args = parser.parse_args()

    password = getpass.getpass("Password: ")
    confirm = getpass.getpass("Confirm password: ")
    if password != confirm:
        print("Passwords did not match.", file=sys.stderr)
        sys.exit(1)
    if len(password) < 8:
        print("Password must be at least 8 characters.", file=sys.stderr)
        sys.exit(1)

    db = SessionLocal()
    try:
        staff = create_staff_user(db, email=args.email, password=password, role=StaffRole.PLATFORM_ADMIN)
    except StaffAuthError as e:
        print(f"Failed: {e.message}", file=sys.stderr)
        sys.exit(1)
    finally:
        db.close()

    print(f"Created platform admin {staff.email} (id={staff.id})")


if __name__ == "__main__":
    main()
