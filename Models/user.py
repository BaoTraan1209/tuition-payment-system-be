import uuid

from sqlalchemy import Column, String
from config.db import Base


class User(Base):
    __tablename__ = "users"

    id = Column(
        String(36),
        primary_key=True,
        default=lambda: str(uuid.uuid4())
    )

    username = Column(String(50), unique=True, nullable=False)
    password_hash = Column("password", String(255), nullable=False)
    fullname = Column(String(100), nullable=False)
    # Mã số sinh viên: 8 ký tự (VD: 522H0113), không trùng giữa các tài khoản
    mssv = Column(String(20), unique=True, nullable=True)
    phone = Column(String(20))
    email = Column(String(100))