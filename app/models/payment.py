from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base


class Payment(Base):
    __tablename__ = "payments"

    id = Column(Integer, primary_key=True, index=True)
    order_id = Column(Integer, ForeignKey("orders.id"), nullable=False, index=True)
    provider = Column(String(50), nullable=False, index=True)  # stripe, bkash
    transaction_id = Column(String(255), unique=True, nullable=False, index=True)
    status = Column(String(20), default="pending", nullable=False, index=True)  # pending, success, failed
    raw_response = Column(JSON, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    # Relationships
    order = relationship("Order", back_populates="payments")
