
from getpass import getpass

from config.db import SessionLocal
from Models.user import User
from Security.password import hash_password


def init_user():
    print("=== Initialize User ===")

    username = input("Username: ").strip()
    password = getpass("Password: ")
    confirm_password = getpass("Confirm password: ")
    fullname = input("Full name: ").strip()
    phone = input("Phone (optional): ").strip() or None
    email = input("Email (optional): ").strip() or None

    if not username or not password or not fullname:
        print("Username, password and full name are required.")
        return

    if len(username) > 50:
        print("Username must not exceed 50 characters.")
        return

    if len(password) > 72:
        print("Password must not exceed 72 bytes for bcrypt.")
        return

    if password != confirm_password:
        print("Passwords do not match.")
        return

    if len(fullname) > 100:
        print("Full name must not exceed 100 characters.")
        return

    if phone and len(phone) > 20:
        print("Phone must not exceed 20 characters.")
        return

    if email and len(email) > 100:
        print("Email must not exceed 100 characters.")
        return

    db = SessionLocal()

    try:
        existing_user = (
            db.query(User)
            .filter(User.username == username)
            .first()
        )

        if existing_user:
            print(f"Username '{username}' already exists.")
            return

        user = User(
            username=username,
            password_hash=hash_password(password),
            fullname=fullname,
            phone=phone,
            email=email
        )

        db.add(user)
        db.commit()

        print("User created successfully!")
        print(f"User ID: {user.id}")
        print(f"Username: {user.username}")
        print(f"Full name: {user.fullname}")

    except Exception as e:
        db.rollback()
        print(f"Failed to create user: {e}")

    finally:
        db.close()


if __name__ == "__main__":
    init_user()
