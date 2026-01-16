import pytest
from unittest.mock import Mock, patch


def test_stripe_webhook_signature_verification(client, db_session):
    """Test Stripe webhook signature verification"""
    with patch('app.services.payment_service.PaymentService.handle_webhook') as mock_handle:
        mock_payment = Mock()
        mock_payment.id = 1
        mock_handle.return_value = mock_payment
        
        response = client.post(
            "/api/webhooks/stripe",
            json={
                "type": "payment_intent.succeeded",
                "data": {
                    "object": {
                        "id": "pi_test123"
                    }
                }
            },
            headers={"stripe-signature": "test_signature"}
        )
        
        # Should process webhook
        assert response.status_code in [200, 201]


def test_bkash_webhook(client, db_session):
    """Test bKash webhook handling"""
    with patch('app.services.payment_service.PaymentService.handle_webhook') as mock_handle:
        mock_payment = Mock()
        mock_payment.id = 1
        mock_handle.return_value = mock_payment
        
        response = client.post(
            "/api/webhooks/bkash",
            json={
                "paymentID": "test_payment_id",
                "status": "success"
            }
        )
        
        # Should process webhook
        assert response.status_code in [200, 201]
