from datetime import datetime
from pydantic import BaseModel, ConfigDict


class NotificationResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    notification_id: int
    payer_id: int
    title: str
    message: str
    type: str
    is_read: bool
    created_at: datetime | None = None
