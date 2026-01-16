from fastapi import APIRouter, Request, HTTPException, status, Header, Depends
from sqlalchemy.orm import Session
from app.database import get_db
from app.services.payment_service import PaymentService
from typing import Optional
import json

router = APIRouter()


@router.post("/stripe")
async def stripe_webhook(
    request: Request,
    db: Session = Depends(get_db),
    stripe_signature: Optional[str] = Header(None, alias="stripe-signature")
):
    """Handle Stripe webhook"""
    try:
        payload_bytes = await request.body()
        payload_dict = json.loads(payload_bytes)
        payment_service = PaymentService(db)
        
        # Verify signature and process webhook
        payment = payment_service.handle_webhook("stripe", payload_dict, stripe_signature)
        
        if payment:
            return {"status": "success", "payment_id": payment.id}
        else:
            return {"status": "ignored"}
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))
