from datetime import datetime
from decimal import Decimal
from pydantic import BaseModel, ConfigDict


class TuitionResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    tuition_id: int
    student_id: int
    mssv: str
    fullname: str
    amount: Decimal
    status: str
    created_at: datetime | None = None
    updated_at: datetime | None = None


class TuitionStatusResponse(BaseModel):
    tuition_id: int
    student_id: int
    mssv: str
    amount: float
    status: str
    is_paid: bool
    is_payable: bool
    created_at: datetime | None = None
    updated_at: datetime | None = None
