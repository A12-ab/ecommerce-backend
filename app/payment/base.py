from abc import ABC, abstractmethod
from typing import Dict, Any, Optional


class PaymentProvider(ABC):
    """Abstract base class for payment providers"""

    @abstractmethod
    def create_payment_intent(self, order_id: int, amount: float) -> Dict[str, Any]:
        """
        Create a payment intent with the provider.
        Returns dict with transaction_id and provider-specific data.
        """
        pass

    @abstractmethod
    def confirm_payment(self, transaction_id: str) -> Dict[str, Any]:
        """
        Confirm a payment with the provider.
        Returns dict with status (success/failed/pending) and raw_response.
        """
        pass

    @abstractmethod
    def query_payment(self, transaction_id: str) -> Dict[str, Any]:
        """
        Query payment status from the provider.
        Returns dict with status and raw_response.
        """
        pass

    def verify_webhook_signature(self, payload: Dict[str, Any], signature: str) -> bool:
        """
        Verify webhook signature (optional, override if needed).
        Returns True if signature is valid.
        """
        return True

    def extract_transaction_id_from_webhook(self, payload: Dict[str, Any]) -> Optional[str]:
        """
        Extract transaction ID from webhook payload.
        Override in subclasses to handle provider-specific payloads.
        """
        return payload.get("transaction_id") or payload.get("id")
