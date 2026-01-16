from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.schemas.payment import PaymentCreate, PaymentResponse, PaymentConfirm
from app.services.payment_service import PaymentService
from app.api.deps import get_current_user
from app.models.user import User

router = APIRouter()


@router.post("/create", response_model=dict, status_code=status.HTTP_201_CREATED)
def initiate_payment(
    payment_data: PaymentCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Initiate payment with specified provider"""
    payment_service = PaymentService(db)
    try:
        result = payment_service.initiate_payment(payment_data.order_id, payment_data.provider)
        return result
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.post("/confirm", response_model=PaymentResponse)
def confirm_payment(
    payment_data: PaymentConfirm,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Confirm payment"""
    payment_service = PaymentService(db)
    payment = payment_service.confirm_payment(payment_data.transaction_id, payment_data.provider)
    if not payment:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Payment not found")
    return payment


@router.get("/{payment_id}", response_model=PaymentResponse)
def get_payment(
    payment_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get payment by ID"""
    payment_service = PaymentService(db)
    payment = payment_service.get_payment_by_id(payment_id)
    if not payment:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Payment not found")
    
    # Verify user owns the order
    if payment.order.user_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied")
    
    return payment
