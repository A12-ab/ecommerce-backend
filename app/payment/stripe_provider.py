import stripe
from typing import Dict, Any
from app.payment.base import PaymentProvider
from app.config import settings


class StripePaymentStrategy(PaymentProvider):
    """Stripe payment provider implementation"""

    def __init__(self):
        stripe.api_key = settings.STRIPE_SECRET_KEY

    def create_payment_intent(self, order_id: int, amount: float) -> Dict[str, Any]:
        """Create Stripe payment intent"""
        try:
            # Convert amount to cents
            amount_cents = int(amount * 100)

            payment_intent = stripe.PaymentIntent.create(
                amount=amount_cents,
                currency="usd",
                metadata={"order_id": str(order_id)},
                automatic_payment_methods={
                    "enabled": True,
                },
            )

            return {
                "transaction_id": payment_intent.id,
                "client_secret": payment_intent.client_secret,
                "raw_response": payment_intent.to_dict()
            }
        except stripe.error.StripeError as e:
            raise ValueError(f"Stripe error: {str(e)}")

    def confirm_payment(self, transaction_id: str) -> Dict[str, Any]:
        """Confirm Stripe payment"""
        try:
            payment_intent = stripe.PaymentIntent.retrieve(transaction_id)
            
            status = "pending"
            if payment_intent.status == "succeeded":
                status = "success"
            elif payment_intent.status == "failed" or payment_intent.status == "canceled":
                status = "failed"

            return {
                "status": status,
                "raw_response": payment_intent.to_dict()
            }
        except stripe.error.StripeError as e:
            return {
                "status": "failed",
                "raw_response": {"error": str(e)}
            }

    def query_payment(self, transaction_id: str) -> Dict[str, Any]:
        """Query Stripe payment status"""
        return self.confirm_payment(transaction_id)

    def verify_webhook_signature(self, payload: bytes, signature: str) -> bool:
        """Verify Stripe webhook signature"""
        try:
            if not settings.STRIPE_WEBHOOK_SECRET:
                return True  # Skip verification if secret not configured
            stripe.Webhook.construct_event(
                payload, signature, settings.STRIPE_WEBHOOK_SECRET
            )
            return True
        except ValueError:
            return False
        except stripe.error.SignatureVerificationError:
            return False

    def extract_transaction_id_from_webhook(self, payload: Dict[str, Any]) -> str:
        """Extract transaction ID from Stripe webhook"""
        return payload.get("data", {}).get("object", {}).get("id", "")
