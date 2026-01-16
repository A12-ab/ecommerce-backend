from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.routes import auth, products, orders, payments
from app.api.webhooks import stripe, bkash
from app.config import settings

app = FastAPI(
    title="E-commerce Backend API",
    description="Backend system for managing users, products, orders, and payments",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"] if settings.DEBUG else [],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth.router, prefix="/api/auth", tags=["Authentication"])
app.include_router(products.router, prefix="/api/products", tags=["Products"])
app.include_router(orders.router, prefix="/api/orders", tags=["Orders"])
app.include_router(payments.router, prefix="/api/payments", tags=["Payments"])
app.include_router(stripe.router, prefix="/api/webhooks", tags=["Webhooks"])
app.include_router(bkash.router, prefix="/api/webhooks", tags=["Webhooks"])


@app.get("/")
async def root():
    return {"message": "E-commerce Backend API", "version": "1.0.0"}


@app.get("/health")
async def health_check():
    return {"status": "healthy"}
