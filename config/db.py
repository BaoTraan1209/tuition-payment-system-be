
import os
from pathlib import Path

from dotenv import load_dotenv
from sqlalchemy import create_engine, URL, text
from sqlalchemy.orm import sessionmaker, declarative_base

load_dotenv(Path(__file__).resolve().parents[1] / ".env")

DB_USER = os.environ["DB_USER"]
DB_PASSWORD = os.getenv("DB_PASSWORD", "")
DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = int(os.getenv("DB_PORT", "3306"))
DB_NAME = os.environ["DB_NAME"]

# Kết nối MySQL server, chưa chọn database
server_url = URL.create(
    "mysql+pymysql",
    username=DB_USER,
    password=DB_PASSWORD,
    host=DB_HOST,
    port=DB_PORT,
)

server_engine = create_engine(server_url, pool_pre_ping=True)

# Tự tạo database nếu chưa tồn tại
with server_engine.connect() as connection:
    connection.execute(
        text(
            f"CREATE DATABASE IF NOT EXISTS `{DB_NAME}` "
            "CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci"
        )
    )

server_engine.dispose()

# Kết nối đến database của ứng dụng
db_url = URL.create(
    "mysql+pymysql",
    username=DB_USER,
    password=DB_PASSWORD,
    host=DB_HOST,
    port=DB_PORT,
    database=DB_NAME,
)

engine = create_engine(db_url, pool_pre_ping=True)

SessionLocal = sessionmaker(
    bind=engine,
    autoflush=False,
    autocommit=False,
)

Base = declarative_base()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()