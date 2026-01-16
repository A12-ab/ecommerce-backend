from fastapi import APIRouter, Request, HTTPException, status, Header, Depends
from sqlalchemy.orm import Session
from app.database import get_db
from app.services.payment_service import PaymentService
from typing import Optional
import json

router = APIRouter()


@router.post("/bkash")
async def bkash_webhook(
    request: Request,
    db: Session = Depends(get_db),
    x_app_key: Optional[str] = Header(None, alias="X-APP-Key")
):
    """Handle bKash webhook"""
    try:
        payload_dict = await request.json()
        payment_service = PaymentService(db)
        
        # Process webhook (bKash may not always send signature)
        payment = payment_service.handle_webhook("bkash", payload_dict, None)
        
        if payment:
            return {"status": "success", "payment_id": payment.id}
        else:
            return {"status": "ignored"}
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))
