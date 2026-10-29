from pydantic import BaseModel, Field


class LoginRequest(BaseModel):
    username: str = Field(min_length=1)
    password: str = Field(min_length=1)


class LoginResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


class UserResponse(BaseModel):
    payer_id: int
    username: str
    fullname: str
    phone: str | None = None
    email: str | None = None
    balance: float
    status: str
    mssv: str | None = None
