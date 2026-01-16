import pytest
from app.models.user import User
from app.models.product import Product
from app.models.order import Order, OrderItem
from app.models.category import Category
from app.models.payment import Payment
from app.core.security import get_password_hash


def test_user_model(db_session):
    """Test User model creation"""
    user = User(
        email="test@example.com",
        password_hash=get_password_hash("password"),
        name="Test User",
        is_admin=False
    )
    db_session.add(user)
    db_session.commit()
    
    assert user.id is not None
    assert user.email == "test@example.com"
    assert user.is_admin is False


def test_product_model(db_session, test_category):
    """Test Product model creation"""
    product = Product(
        name="Test Product",
        sku="TEST001",
        price=99.99,
        stock=100,
        status="active",
        category_id=test_category.id
    )
    db_session.add(product)
    db_session.commit()
    
    assert product.id is not None
    assert product.sku == "TEST001"
    assert product.price == 99.99


def test_order_model(db_session, test_user):
    """Test Order model creation"""
    order = Order(
        user_id=test_user.id,
        total_amount=199.98,
        status="pending"
    )
    db_session.add(order)
    db_session.commit()
    
    assert order.id is not None
    assert order.user_id == test_user.id
    assert order.status == "pending"


def test_order_item_model(db_session, test_user, test_product):
    """Test OrderItem model creation"""
    order = Order(
        user_id=test_user.id,
        total_amount=99.99,
        status="pending"
    )
    db_session.add(order)
    db_session.flush()
    
    order_item = OrderItem(
        order_id=order.id,
        product_id=test_product.id,
        quantity=1,
        price=99.99,
        subtotal=99.99
    )
    db_session.add(order_item)
    db_session.commit()
    
    assert order_item.id is not None
    assert order_item.subtotal == 99.99
