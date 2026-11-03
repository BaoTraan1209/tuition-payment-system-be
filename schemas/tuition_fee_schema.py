from datetime import date

from pydantic import BaseModel, Field, ConfigDict


class CreateTuitionFeeRequest(BaseModel):
    user_id: str
    title: str = Field(
        min_length=1,
        max_length=255
    )
    description: str | None = None
    amount: int = Field(
        gt=0,
        description="Tuition fee amount in VND"
    )
    due_date: date


class CreateTuitionFeeResponse(BaseModel):
    id: int
    user_id: str
    title: str
    description: str | None = None
    amount: int
    due_date: date
    status: str


class TuitionFeeResponse(BaseModel):
    id: int
    title: str
    description: str | None = None
    amount: int
    due_date: date
    status: str

    model_config = ConfigDict(from_attributes=True)