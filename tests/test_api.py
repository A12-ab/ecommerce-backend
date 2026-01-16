import pytest
from decimal import Decimal


def test_register_user(client):
    """Test user registration"""
    response = client.post(
        "/api/auth/register",
        json={
            "email": "newuser@example.com",
            "password": "password123",
            "name": "New User"
        }
    )
    assert response.status_code == 201
    assert response.json()["email"] == "newuser@example.com"


def test_login_user(client, test_user):
    """Test user login"""
    response = client.post(
        "/api/auth/login",
        json={
            "email": "test@example.com",
            "password": "testpassword"
        }
    )
    assert response.status_code == 200
    assert "access_token" in response.json()


def test_get_products(client, test_product):
    """Test get products endpoint"""
    response = client.get("/api/products")
    assert response.status_code == 200
    assert len(response.json()) > 0


def test_create_product_requires_admin(client, test_user):
    """Test that creating product requires admin"""
    # Login as regular user
    login_response = client.post(
        "/api/auth/login",
        json={
            "email": "test@example.com",
            "password": "testpassword"
        }
    )
    token = login_response.json()["access_token"]
    
    # Try to create product
    response = client.post(
        "/api/products",
        json={
            "name": "New Product",
            "sku": "NEW001",
            "price": 99.99,
            "stock": 100
        },
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 403  # Forbidden


def test_create_order_requires_auth(client, test_product):
    """Test that creating order requires authentication"""
    response = client.post(
        "/api/orders",
        json={
            "items": [{"product_id": test_product.id, "quantity": 1}]
        }
    )
    assert response.status_code == 401  # Unauthorized


def test_create_order_authenticated(client, test_user, test_product):
    """Test creating order when authenticated"""
    # Login
    login_response = client.post(
        "/api/auth/login",
        json={
            "email": "test@example.com",
            "password": "testpassword"
        }
    )
    token = login_response.json()["access_token"]
    
    # Create order
    response = client.post(
        "/api/orders",
        json={
            "items": [{"product_id": test_product.id, "quantity": 1}]
        },
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 201
    assert response.json()["status"] == "pending"
