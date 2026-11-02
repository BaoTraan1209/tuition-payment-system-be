from pydantic import BaseModel, Field

class CreatePaymentRequest(BaseModel):
    amount: int = Field(
        gt=0,
        description="Payment amount in VND"
    )

class CreatePaymentResponse(BaseModel):
    order_id: str
    amount: int
    status: str
    payment_url: str