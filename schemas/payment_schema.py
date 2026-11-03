from pydantic import BaseModel, Field

class CreatePaymentRequest(BaseModel):
    tuition_fee_id: int = Field(gt=0)

class CreatePaymentResponse(BaseModel):
    order_id: str
    amount: int
    status: str
    payment_url: str