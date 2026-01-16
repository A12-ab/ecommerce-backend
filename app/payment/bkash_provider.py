import requests
import json
from typing import Dict, Any, Optional
from app.payment.base import PaymentProvider
from app.config import settings


class BkashPaymentStrategy(PaymentProvider):
    """bKash payment provider implementation"""

    def __init__(self):
        self.base_url = settings.BKASH_BASE_URL
        self.app_key = settings.BKASH_APP_KEY
        self.app_secret = settings.BKASH_APP_SECRET
        self.username = settings.BKASH_USERNAME
        self.password = settings.BKASH_PASSWORD
        self._token: Optional[str] = None
        self._token_expires_at: Optional[float] = None

    def _get_token(self) -> str:
        """Get or refresh bKash access token"""
        import time
        
        # Return cached token if still valid
        if self._token and self._token_expires_at and time.time() < self._token_expires_at:
            return self._token

        url = f"{self.base_url}/tokenized/checkout/token/grant"
        headers = {
            "Content-Type": "application/json",
            "Accept": "application/json",
            "username": self.username,
            "password": self.password,
        }
        data = {
            "app_key": self.app_key,
            "app_secret": self.app_secret,
        }

        try:
            response = requests.post(url, json=data, headers=headers)
            response.raise_for_status()
            result = response.json()
            
            self._token = result.get("id_token")
            # Token expires in 3600 seconds, refresh a bit earlier
            self._token_expires_at = time.time() + 3500
            
            return self._token
        except requests.RequestException as e:
            raise ValueError(f"Failed to get bKash token: {str(e)}")

    def create_payment_intent(self, order_id: int, amount: float) -> Dict[str, Any]:
        """Create bKash payment intent (checkout)"""
        token = self._get_token()
        
        url = f"{self.base_url}/tokenized/checkout/payment/create"
        headers = {
            "Content-Type": "application/json",
            "Accept": "application/json",
            "Authorization": token,
            "X-APP-Key": self.app_key,
        }
        
        # Convert amount to string with 2 decimal places
        amount_str = f"{amount:.2f}"
        
        data = {
            "mode": "0011",  # Checkout mode
            "payerReference": f"order_{order_id}",
            "callbackURL": "https://your-domain.com/api/webhooks/bkash",
            "amount": amount_str,
            "currency": "BDT",
            "intent": "sale",
            "merchantInvoiceNumber": str(order_id),
        }

        try:
            response = requests.post(url, json=data, headers=headers)
            response.raise_for_status()
            result = response.json()
            
            if result.get("statusCode") != "0000":
                raise ValueError(f"bKash error: {result.get('statusMessage', 'Unknown error')}")

            payment_id = result.get("paymentID")
            if not payment_id:
                raise ValueError("No payment ID returned from bKash")

            return {
                "transaction_id": payment_id,
                "payment_url": result.get("bkashURL"),
                "raw_response": result
            }
        except requests.RequestException as e:
            raise ValueError(f"bKash payment creation failed: {str(e)}")

    def confirm_payment(self, transaction_id: str) -> Dict[str, Any]:
        """Execute bKash payment"""
        token = self._get_token()
        
        url = f"{self.base_url}/tokenized/checkout/payment/execute"
        headers = {
            "Content-Type": "application/json",
            "Accept": "application/json",
            "Authorization": token,
            "X-APP-Key": self.app_key,
        }
        
        data = {
            "paymentID": transaction_id,
        }

        try:
            response = requests.post(url, json=data, headers=headers)
            response.raise_for_status()
            result = response.json()
            
            status = "pending"
            if result.get("statusCode") == "0000":
                status = "success"
            elif result.get("statusCode") in ["2001", "2002", "2003"]:
                status = "failed"

            return {
                "status": status,
                "raw_response": result
            }
        except requests.RequestException as e:
            return {
                "status": "failed",
                "raw_response": {"error": str(e)}
            }

    def query_payment(self, transaction_id: str) -> Dict[str, Any]:
        """Query bKash payment status"""
        token = self._get_token()
        
        url = f"{self.base_url}/tokenized/checkout/payment/query"
        headers = {
            "Content-Type": "application/json",
            "Accept": "application/json",
            "Authorization": token,
            "X-APP-Key": self.app_key,
        }
        
        data = {
            "paymentID": transaction_id,
        }

        try:
            response = requests.post(url, json=data, headers=headers)
            response.raise_for_status()
            result = response.json()
            
            status = "pending"
            if result.get("statusCode") == "0000":
                # Check transaction status
                transaction_status = result.get("transactionStatus", "").upper()
                if transaction_status == "COMPLETED":
                    status = "success"
                elif transaction_status in ["FAILED", "CANCELLED"]:
                    status = "failed"
            else:
                status = "failed"

            return {
                "status": status,
                "raw_response": result
            }
        except requests.RequestException as e:
            return {
                "status": "failed",
                "raw_response": {"error": str(e)}
            }

    def extract_transaction_id_from_webhook(self, payload: Dict[str, Any]) -> Optional[str]:
        """Extract transaction ID from bKash webhook"""
        return payload.get("paymentID") or payload.get("payment_id")
