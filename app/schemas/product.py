from pydantic import BaseModel
from datetime import datetime
from typing import Optional
from decimal import Decimal


class ProductCreate(BaseModel):
    name: str
    sku: str
    description: Optional[str] = None
    price: Decimal
    stock: int = 0
    status: str = "active"
    category_id: Optional[int] = None


class ProductUpdate(BaseModel):
    name: Optional[str] = None
    sku: Optional[str] = None
    description: Optional[str] = None
    price: Optional[Decimal] = None
    stock: Optional[int] = None
    status: Optional[str] = None
    category_id: Optional[int] = None


class ProductResponse(BaseModel):
    id: int
    name: str
    sku: str
    description: Optional[str]
    price: Decimal
    stock: int
    status: str
    category_id: Optional[int]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
