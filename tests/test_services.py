import pytest
from decimal import Decimal
from app.services.user_service import UserService
from app.services.product_service import ProductService
from app.services.order_service import OrderService
from app.schemas.user import UserCreate
from app.schemas.product import ProductCreate
from app.schemas.order import OrderCreate, OrderItemCreate


def test_user_service_create_user(db_session):
    """Test UserService create_user"""
    service = UserService(db_session)
    user_data = UserCreate(
        email="newuser@example.com",
        password="password123",
        name="New User"
    )
    user = service.create_user(user_data)
    assert user.id is not None
    assert user.email == "newuser@example.com"


def test_user_service_authenticate(db_session, test_user):
    """Test UserService authenticate_user"""
    service = UserService(db_session)
    user = service.authenticate_user("test@example.com", "testpassword")
    assert user is not None
    assert user.email == "test@example.com"


def test_product_service_create_product(db_session, test_category):
    """Test ProductService create_product"""
    service = ProductService(db_session)
    product_data = ProductCreate(
        name="New Product",
        sku="NEW001",
        price=Decimal("49.99"),
        stock=50,
        category_id=test_category.id
    )
    product = service.create_product(product_data)
    assert product.id is not None
    assert product.sku == "NEW001"


def test_order_service_create_order(db_session, test_user, test_product):
    """Test OrderService create_order"""
    service = OrderService(db_session)
    order_data = OrderCreate(
        items=[OrderItemCreate(product_id=test_product.id, quantity=2)]
    )
    order = service.create_order(test_user.id, order_data)
    assert order.id is not None
    assert order.total_amount > 0
    assert len(order.order_items) == 1


def test_order_service_calculate_total_deterministic(db_session, test_user, test_product):
    """Test that order total calculation is deterministic"""
    service = OrderService(db_session)
    order_data = OrderCreate(
        items=[
            OrderItemCreate(product_id=test_product.id, quantity=2),
            OrderItemCreate(product_id=test_product.id, quantity=1)
        ]
    )
    order1 = service.create_order(test_user.id, order_data)
    total1 = order1.total_amount
    
    # Create another identical order
    order2 = service.create_order(test_user.id, order_data)
    total2 = order2.total_amount
    
    # Totals should be the same (deterministic)
    assert total1 == total2
