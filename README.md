# E-commerce Backend System

A comprehensive FastAPI-based e-commerce backend system with user management, product management, order processing, and multi-provider payment integration (Stripe & bKash).

## Features

- **User Management**: Registration, authentication, and user profile management
- **Product Management**: CRUD operations for products with category support
- **Order Management**: Order creation, tracking, and status management
- **Payment Integration**: Support for Stripe and bKash payment providers using Strategy Pattern
- **Category System**: Hierarchical categories with DFS-based product recommendations
- **Caching**: Redis caching for category trees and recommendations
- **Webhooks**: Payment webhook handlers for both providers

## Tech Stack

- **Framework**: FastAPI
- **Database**: PostgreSQL
- **Cache**: Redis
- **ORM**: SQLAlchemy
- **Migrations**: Alembic
- **Authentication**: JWT
- **Testing**: Pytest

## Project Structure

```
backend/
├── app/              # Main application code
├── alembic/          # Database migrations
├── tests/            # Test suite
├── seeders/          # Database seeders
├── docker/           # Docker configuration
└── docs/             # Documentation
```

## Setup

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd practice
   ```

2. **Create virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables**
   
   Create a `.env` file in the root directory with the following variables:
   ```bash
   # Database Configuration
   DATABASE_URL=postgresql://user:password@localhost:5432/ecommerce_db
   
   # Redis Configuration
   REDIS_URL=redis://localhost:6379/0
   
   # JWT Configuration
   SECRET_KEY=your-secret-key-here-change-in-production
   ALGORITHM=HS256
   ACCESS_TOKEN_EXPIRE_MINUTES=30
   
   # Stripe Configuration (Get from https://dashboard.stripe.com/apikeys)
   STRIPE_SECRET_KEY=sk_test_your_stripe_secret_key
   STRIPE_PUBLISHABLE_KEY=pk_test_your_stripe_publishable_key
   STRIPE_WEBHOOK_SECRET=whsec_your_webhook_secret
   
   # bKash Configuration (Get from bKash merchant portal)
   BKASH_APP_KEY=your_bkash_app_key
   BKASH_APP_SECRET=your_bkash_app_secret
   BKASH_USERNAME=your_bkash_username
   BKASH_PASSWORD=your_bkash_password
   BKASH_BASE_URL=https://tokenized.sandbox.bka.sh/v1.2.0-beta
   BKASH_WEBHOOK_SECRET=your_bkash_webhook_secret
   
   # Environment Configuration
   ENVIRONMENT=development
   DEBUG=True
   ```
   
   **Note**: The `.env` file is gitignored for security. Make sure to create it manually with your actual credentials.

5. **Set up database**
   ```bash
   # Using Docker Compose
   docker-compose -f docker/docker-compose.yml up -d
   
   # Run migrations
   alembic upgrade head
   ```

6. **Seed database**
   ```bash
   python -m seeders.admin_seeder
   python -m seeders.product_seeder
   ```

7. **Run the application**
   ```bash
   uvicorn app.main:app --reload
   ```

## API Documentation

Once the server is running, visit:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## Testing

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=app --cov-report=html
```

## Docker Deployment

```bash
cd docker
docker-compose up -d
```

## Environment Variables

See `.env.example` for all required environment variables.

## License

MIT
