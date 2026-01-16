from pydantic import BaseModel
from datetime import datetime
from typing import List
from decimal import Decimal


class OrderItemCreate(BaseModel):
    product_id: int
    quantity: int


class OrderCreate(BaseModel):
    items: List[OrderItemCreate]


class OrderItemResponse(BaseModel):
    id: int
    order_id: int
    product_id: int
    quantity: int
    price: Decimal
    subtotal: Decimal
    created_at: datetime

    class Config:
        from_attributes = True


class OrderResponse(BaseModel):
    id: int
    user_id: int
    total_amount: Decimal
    status: str
    created_at: datetime
    updated_at: datetime
    order_items: List[OrderItemResponse] = []

    class Config:
        from_attributes = True
