from pydantic import BaseModel
from datetime import datetime
from typing import Optional, Dict, Any


class PaymentCreate(BaseModel):
    order_id: int
    provider: str  # stripe or bkash


class PaymentInitiate(BaseModel):
    order_id: int
    provider: str


class PaymentResponse(BaseModel):
    id: int
    order_id: int
    provider: str
    transaction_id: str
    status: str
    raw_response: Optional[Dict[str, Any]] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class PaymentConfirm(BaseModel):
    transaction_id: str
    provider: str
