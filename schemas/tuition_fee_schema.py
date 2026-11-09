from datetime import date
from pydantic import BaseModel, Field, ConfigDict
from datetime import date
from typing import List, Optional

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

class CreateTuitionFeesBulkRequest(BaseModel):
    user_ids: List[str] = Field(..., description="Danh sách các ID sinh viên được chọn")
    title: str
    amount: int
    due_date: date
    description: Optional[str] = None

class TuitionFeeResponse(BaseModel):
    id: int
    user_id: str
    title: str
    description: Optional[str]
    amount: int
    due_date: date
    status: str