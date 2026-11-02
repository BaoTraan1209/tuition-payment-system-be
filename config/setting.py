import os

from dotenv import load_dotenv
from zoneinfo import ZoneInfo

load_dotenv()

APP_NAME = os.getenv("APP_NAME", "iBanking")
APP_ENV = os.getenv("APP_ENV", "local")
APP_DEBUG = os.getenv("APP_DEBUG", "true").lower() == "true"
APP_HOST = os.getenv("APP_HOST", "127.0.0.1")
APP_PORT = int(os.getenv("APP_PORT", "8000"))

APP_TIMEZONE = ZoneInfo(
    os.getenv("APP_TIMEZONE", "Asia/Ho_Chi_Minh")
)