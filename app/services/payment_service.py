from sqlalchemy.orm import Session
from typing import Optional, Dict, Any
from app.models.payment import Payment
from app.models.order import Order
from app.services.order_service import OrderService
from app.payment.base import PaymentProvider
from app.payment.stripe_provider import StripePaymentStrategy
from app.payment.bkash_provider import BkashPaymentStrategy
from app.config import settings


class PaymentService:
    """Service class for payment management operations"""

    def __init__(self, db: Session):
        self.db = db
        self.order_service = OrderService(db)
        self._providers: Dict[str, PaymentProvider] = {
            "stripe": StripePaymentStrategy(),
            "bkash": BkashPaymentStrategy()
        }

    def _get_provider(self, provider_name: str) -> PaymentProvider:
        """Get payment provider by name"""
        provider = self._providers.get(provider_name.lower())
        if not provider:
            raise ValueError(f"Payment provider '{provider_name}' not supported")
        return provider

    def initiate_payment(self, order_id: int, provider: str) -> Dict[str, Any]:
        """Initiate payment with specified provider"""
        order = self.order_service.get_order_by_id(order_id)
        if not order:
            raise ValueError("Order not found")
        if order.status != "pending":
            raise ValueError("Order is not in pending status")

        payment_provider = self._get_provider(provider)

        # Create payment intent with provider
        result = payment_provider.create_payment_intent(order_id, float(order.total_amount))

        # Save payment record
        payment = Payment(
            order_id=order_id,
            provider=provider.lower(),
            transaction_id=result["transaction_id"],
            status="pending",
            raw_response=result.get("raw_response")
        )
        self.db.add(payment)
        self.db.commit()
        self.db.refresh(payment)

        return {
            "payment_id": payment.id,
            "transaction_id": result["transaction_id"],
            "client_secret": result.get("client_secret"),
            "payment_url": result.get("payment_url"),
            "provider": provider
        }

    def confirm_payment(self, transaction_id: str, provider: str) -> Optional[Payment]:
        """Confirm payment with provider"""
        payment = self.db.query(Payment).filter(
            Payment.transaction_id == transaction_id,
            Payment.provider == provider.lower()
        ).first()

        if not payment:
            return None

        payment_provider = self._get_provider(provider)
        result = payment_provider.confirm_payment(transaction_id)

        # Update payment status
        payment.status = result["status"]
        payment.raw_response = result.get("raw_response")
        self.db.commit()
        self.db.refresh(payment)

        # Update order status if payment successful
        if result["status"] == "success":
            self.order_service.mark_order_as_paid(payment.order_id)

        return payment

    def query_payment(self, transaction_id: str, provider: str) -> Optional[Payment]:
        """Query payment status from provider"""
        payment = self.db.query(Payment).filter(
            Payment.transaction_id == transaction_id,
            Payment.provider == provider.lower()
        ).first()

        if not payment:
            return None

        payment_provider = self._get_provider(provider)
        result = payment_provider.query_payment(transaction_id)

        # Update payment status
        payment.status = result["status"]
        payment.raw_response = result.get("raw_response")
        self.db.commit()
        self.db.refresh(payment)

        return payment

    def get_payment_by_id(self, payment_id: int) -> Optional[Payment]:
        """Get payment by ID"""
        return self.db.query(Payment).filter(Payment.id == payment_id).first()

    def handle_webhook(self, provider: str, payload: Dict[str, Any], signature: Optional[str] = None) -> Optional[Payment]:
        """Handle webhook from payment provider"""
        payment_provider = self._get_provider(provider)
        
        # Verify webhook signature if provided
        if signature and hasattr(payment_provider, 'verify_webhook_signature'):
            # For Stripe, payload needs to be bytes for signature verification
            if provider == "stripe" and isinstance(payload, dict):
                import json
                payload_bytes = json.dumps(payload).encode()
                if not payment_provider.verify_webhook_signature(payload_bytes, signature):
                    raise ValueError("Invalid webhook signature")
            elif not payment_provider.verify_webhook_signature(payload, signature):
                raise ValueError("Invalid webhook signature")

        # Process webhook
        transaction_id = payment_provider.extract_transaction_id_from_webhook(payload)
        if not transaction_id:
            return None

        # Query payment status
        return self.query_payment(transaction_id, provider)
