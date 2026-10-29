from pydantic import BaseModel, ConfigDict, Field

class UserProfileResponse(BaseModel):
    id: str
    username: str
    fullname: str
    phone: str | None = None
    email: str | None = None

    model_config = ConfigDict(from_attributes=True)

class UserProfileUpdate(BaseModel):
    fullname: str | None = Field(default=None, min_length=1, max_length=100)
    phone: str | None = Field(default=None, max_length=20)
    email: str | None = Field(default=None, max_length=100)