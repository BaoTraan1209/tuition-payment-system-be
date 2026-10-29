# from pydantic_settings import BaseSettings, SettingsConfigDict

# class Settings(BaseSettings):
#     # Application
#     APP_NAME: str = "iBanking"
#     BRAND_NAME: str = "iBanking"
#     APP_ENV: str = "local"
#     APP_DEBUG: bool = True
#     APP_HOST: str = "127.0.0.1"
#     APP_PORT: int = 8000
#     APP_TIMEZONE: str = "Asia/Ho_Chi_Minh"
#     APP_URL: str = "http://127.0.0.1:8000"

#     # MySQL
#     DB_CONNECTION: str = "mysql"
#     DB_HOST: str = "127.0.0.1"
#     DB_PORT: int = 3306
#     DB_DATABASE: str
#     DB_USERNAME: str
#     DB_PASSWORD: str = ""

#     # JWT
#     SECRET_KEY: str
#     ALGORITHM: str = "HS256"
#     TOKEN_EXP: int = 5

#     # Password
#     BCRYPT_ROUNDS: int = 12

#     # Email
#     MAIL_HOST: str = "smtp.gmail.com"
#     MAIL_PORT: int = 587
#     MAIL_USERNAME: str
#     MAIL_PASSWORD: str
#     MAIL_FROM_ADDRESS: str
#     MAIL_FROM_NAME: str = "iBanking"
#     MAIL_TLS: bool = True

#     # OTP
#     OTP_EXPIRE_MINUTES: int = 5
#     OTP_MAX_ATTEMPTS: int = 5

#     model_config = SettingsConfigDict(
#         env_file=".env",
#         env_file_encoding="utf-8",
#         extra="ignore"
#     )


# settings = Settings()