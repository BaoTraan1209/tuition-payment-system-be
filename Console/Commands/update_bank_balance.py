from config.db import SessionLocal
from Models.user import User
from Models.bank_account import BankAccount


def update_bank_balance():
    print("=== Update Bank Account Balance ===")

    username = input("Username: ").strip()

    if not username:
        print("Username is required.")
        return

    balance_input = input("New balance (VND): ").strip()

    if not balance_input.isdigit():
        print("Balance must be a non-negative integer.")
        return

    balance = int(balance_input)

    db = SessionLocal()

    try:
        user = (
            db.query(User)
            .filter(User.username == username)
            .first()
        )

        if not user:
            print(f"User '{username}' does not exist.")
            return

        bank_account = (
            db.query(BankAccount)
            .filter(BankAccount.user_id == user.id)
            .first()
        )

        if bank_account:
            old_balance = bank_account.balance
            bank_account.balance = balance

            print("Bank account balance updated!")

        else:
            bank_account = BankAccount(
                user_id=user.id,
                balance=balance
            )

            db.add(bank_account)
            old_balance = 0

            print("Bank account created successfully!")

        db.commit()

        print(f"Username: {user.username}")
        print(f"Old balance: {old_balance:,} VND")
        print(f"New balance: {bank_account.balance:,} VND")

    except Exception as e:
        db.rollback()
        print(f"Failed to update balance: {e}")

    finally:
        db.close()


if __name__ == "__main__":
    update_bank_balance()
