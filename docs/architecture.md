# System Architecture

## Overview

The E-commerce Backend System is built using FastAPI with a clean, layered architecture that separates concerns and follows SOLID principles.

## Architecture Layers

### 1. API Layer (`app/api/`)
- **Routes**: Handle HTTP requests and responses
- **Dependencies**: Authentication and authorization
- **Webhooks**: Payment provider webhook handlers

### 2. Service Layer (`app/services/`)
- **OOP Service Classes**: Business logic encapsulation
  - `UserService`: User management and authentication
  - `ProductService`: Product CRUD and stock management
  - `OrderService`: Order creation and status management
  - `PaymentService`: Payment orchestration
  - `CategoryService`: Category hierarchy and recommendations

### 3. Payment Strategy Layer (`app/payment/`)
- **Abstract Base Class**: `PaymentProvider` interface
- **Concrete Implementations**:
  - `StripePaymentStrategy`: Stripe integration
  - `BkashPaymentStrategy`: bKash integration

### 4. Data Layer
- **Models** (`app/models/`): SQLAlchemy ORM models
- **Database**: PostgreSQL for persistent storage
- **Cache**: Redis for category trees and recommendations

### 5. Core Utilities (`app/core/`)
- **Security**: JWT authentication, password hashing
- **Cache**: Redis client utilities
- **Algorithms**: Deterministic calculation functions

## Design Patterns

### Strategy Pattern
The payment system uses the Strategy Pattern to support multiple payment providers. New providers can be added by implementing the `PaymentProvider` interface without modifying existing code.

### Service Layer Pattern
Business logic is encapsulated in service classes, keeping controllers thin and making the codebase more maintainable and testable.

## Data Flow

1. **Request** → API Route
2. **Route** → Service Class
3. **Service** → Database/Cache/External APIs
4. **Response** ← Service ← Route ← **Client**

## Key Features

- **OOP Design**: All business logic in service classes
- **Deterministic Algorithms**: Consistent calculations for totals and stock
- **DFS + Caching**: Efficient category traversal with Redis caching
- **Strategy Pattern**: Extensible payment provider system
- **RESTful API**: Clean REST endpoints
- **JWT Authentication**: Secure token-based auth
- **Webhook Support**: Payment status updates via webhooks
