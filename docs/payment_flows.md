# Payment Flow Documentation

## Overview

The system supports two payment providers: Stripe and bKash. Both follow a similar flow but with provider-specific implementations.

## Stripe Payment Flow

### 1. Order Creation
User creates an order with selected products.

### 2. Payment Initiation
```
POST /api/payments/create
{
  "order_id": 1,
  "provider": "stripe"
}
```

**Backend Process:**
1. PaymentService receives request
2. Selects StripePaymentStrategy
3. Creates Stripe PaymentIntent
4. Saves payment record with status="pending"
5. Returns client_secret to frontend

### 3. Frontend Payment
Frontend uses Stripe.js to confirm payment with the client_secret.

### 4. Webhook Processing
Stripe sends webhook to:
```
POST /api/webhooks/stripe
```

**Backend Process:**
1. Verifies webhook signature
2. Extracts transaction_id from webhook payload
3. Queries payment status from Stripe
4. Updates payment record
5. If successful, marks order as "paid" and reduces stock

### 5. Payment Confirmation
User can also manually confirm payment:
```
POST /api/payments/confirm
{
  "transaction_id": "pi_1234567890",
  "provider": "stripe"
}
```

## bKash Payment Flow

### 1. Order Creation
User creates an order with selected products.

### 2. Payment Initiation
```
POST /api/payments/create
{
  "order_id": 1,
  "provider": "bkash"
}
```

**Backend Process:**
1. PaymentService receives request
2. Selects BkashPaymentStrategy
3. Gets bKash access token
4. Creates bKash checkout payment
5. Saves payment record with status="pending"
6. Returns payment_id and payment_url to frontend

### 3. Frontend Payment
Frontend redirects user to bKash payment URL or uses bKash SDK.

### 4. Payment Execution
After user completes payment on bKash, frontend calls execute API or bKash sends webhook.

### 5. Webhook Processing
bKash sends webhook to:
```
POST /api/webhooks/bkash
```

**Backend Process:**
1. Extracts transaction_id from webhook payload
2. Queries payment status from bKash
3. Updates payment record
4. If successful, marks order as "paid" and reduces stock

### 6. Payment Query
User can query payment status:
```
POST /api/payments/confirm
{
  "transaction_id": "payment_id_123",
  "provider": "bkash"
}
```

## Payment States

- **pending**: Payment initiated but not confirmed
- **success**: Payment completed successfully
- **failed**: Payment failed or was canceled

## Order Status Updates

When payment is confirmed:
1. Payment status → "success"
2. Order status → "paid"
3. Product stock → reduced atomically

## Error Handling

- Invalid payment provider → 400 Bad Request
- Order not found → 404 Not Found
- Insufficient stock → 400 Bad Request
- Payment failed → Payment status set to "failed"

## Security

- **Webhook Signatures**: Stripe webhooks are verified using signature
- **JWT Authentication**: All payment endpoints require authentication
- **User Authorization**: Users can only access their own payments
- **Atomic Operations**: Stock reduction uses database transactions
