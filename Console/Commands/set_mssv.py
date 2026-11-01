"""
Gán / đổi MSSV cho một tài khoản đã có.

Chạy:
    python -m Console.Commands.set_mssv
"""
import re

from config.db import SessionLocal
from Models.user import User

MSSV_PATTERN = re.compile(r"[0-9A-Z]{8}")


def set_mssv():
    print("=== Set MSSV for user ===")

    username = input("Username: ").strip()
    mssv = input("MSSV: ").strip().upper()

    if not MSSV_PATTERN.fullmatch(mssv):
        print("MSSV must be 8 letters/digits, e.g. 522H0113.")
        return

    db = SessionLocal()

    try:
        user = db.query(User).filter(User.username == username).first()

        if user is None:
            print(f"Username '{username}' not found.")
            return

        owner = db.query(User).filter(User.mssv == mssv).first()

        if owner and owner.id != user.id:
            print(f"MSSV '{mssv}' is already linked to user '{owner.username}'.")
            return

        user.mssv = mssv
        db.commit()

        print(f"Updated: {user.username} -> MSSV {user.mssv}")

    except Exception as e:
        db.rollback()
        print(f"Failed to update MSSV: {e}")

    finally:
        db.close()


if __name__ == "__main__":
    set_mssv()
