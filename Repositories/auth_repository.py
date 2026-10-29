from sqlalchemy import text
from sqlalchemy.orm import Session
from Models.user import User

def get_user_by_username(db, username):
    return db.query(User).filter(
        User.username == username
    ).first()

def get_user_by_id(db, id):
    return db.query(User).filter(
        User.id == id
    ).first()