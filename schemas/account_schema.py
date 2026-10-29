from pydantic import BaseModel, ConfigDict


class AccountResponse(BaseModel):
    account_id: int
    payer_id: int
    balance: float
    status: str

    model_config = ConfigDict(from_attributes=True)


class AccountBalanceResponse(BaseModel):
    payer_id: int
    balance: float
    status: str
