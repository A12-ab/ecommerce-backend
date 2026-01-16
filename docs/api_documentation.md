# API Documentation

## Base URL
```
http://localhost:8000
```

## Authentication

Most endpoints require JWT authentication. Include the token in the Authorization header:
```
Authorization: Bearer <access_token>
```

## Endpoints

### Authentication

#### Register User
```http
POST /api/auth/register
Content-Type: application/json

{
  "email": "user@example.com",
  "password": "password123",
  "name": "User Name"
}
```

**Response:**
```json
{
  "id": 1,
  "email": "user@example.com",
  "name": "User Name",
  "is_admin": false,
  "created_at": "2024-01-01T00:00:00"
}
```

#### Login
```http
POST /api/auth/login
Content-Type: application/json

{
  "email": "user@example.com",
  "password": "password123"
}
```

**Response:**
```json
{
  "access_token": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "token_type": "bearer"
}
```

#### Get Current User
```http
GET /api/auth/me
Authorization: Bearer <token>
```

### Products

#### List Products
```http
GET /api/products?skip=0&limit=100&status=active
```

#### Get Product
```http
GET /api/products/{product_id}
```

#### Create Product (Admin Only)
```http
POST /api/products
Authorization: Bearer <admin_token>
Content-Type: application/json

{
  "name": "Product Name",
  "sku": "SKU001",
  "description": "Product description",
  "price": 99.99,
  "stock": 100,
  "status": "active",
  "category_id": 1
}
```

#### Update Product (Admin Only)
```http
PUT /api/products/{product_id}
Authorization: Bearer <admin_token>
Content-Type: application/json

{
  "price": 89.99,
  "stock": 90
}
```

#### Delete Product (Admin Only)
```http
DELETE /api/products/{product_id}
Authorization: Bearer <admin_token>
```

#### Get Product Recommendations
```http
GET /api/products/recommendations/{product_id}?limit=10
```

### Orders

#### Create Order
```http
POST /api/orders
Authorization: Bearer <token>
Content-Type: application/json

{
  "items": [
    {
      "product_id": 1,
      "quantity": 2
    },
    {
      "product_id": 2,
      "quantity": 1
    }
  ]
}
```

#### Get User Orders
```http
GET /api/orders?skip=0&limit=100
Authorization: Bearer <token>
```

#### Get Order
```http
GET /api/orders/{order_id}
Authorization: Bearer <token>
```

#### Cancel Order
```http
PUT /api/orders/{order_id}/cancel
Authorization: Bearer <token>
```

### Payments

#### Initiate Payment
```http
POST /api/payments/create
Authorization: Bearer <token>
Content-Type: application/json

{
  "order_id": 1,
  "provider": "stripe"
}
```

**Response (Stripe):**
```json
{
  "payment_id": 1,
  "transaction_id": "pi_1234567890",
  "client_secret": "pi_1234567890_secret_...",
  "provider": "stripe"
}
```

**Response (bKash):**
```json
{
  "payment_id": 1,
  "transaction_id": "payment_id_123",
  "payment_url": "https://...",
  "provider": "bkash"
}
```

#### Confirm Payment
```http
POST /api/payments/confirm
Authorization: Bearer <token>
Content-Type: application/json

{
  "transaction_id": "pi_1234567890",
  "provider": "stripe"
}
```

#### Get Payment
```http
GET /api/payments/{payment_id}
Authorization: Bearer <token>
```

### Webhooks

#### Stripe Webhook
```http
POST /api/webhooks/stripe
X-Stripe-Signature: <signature>
Content-Type: application/json

{
  "type": "payment_intent.succeeded",
  "data": {
    "object": {
      "id": "pi_1234567890"
    }
  }
}
```

#### bKash Webhook
```http
POST /api/webhooks/bkash
Content-Type: application/json

{
  "paymentID": "payment_id_123",
  "status": "success"
}
```

## Error Responses

### 400 Bad Request
```json
{
  "detail": "Error message"
}
```

### 401 Unauthorized
```json
{
  "detail": "Could not validate credentials"
}
```

### 403 Forbidden
```json
{
  "detail": "Not enough permissions"
}
```

### 404 Not Found
```json
{
  "detail": "Resource not found"
}
```

## Interactive API Documentation

FastAPI automatically generates interactive API documentation:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
