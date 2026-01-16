from sqlalchemy.orm import Session
from typing import List, Optional
from app.models.order import Order, OrderItem
from app.models.product import Product
from app.schemas.order import OrderCreate, OrderItemCreate
from app.core.algorithms import calculate_subtotal, calculate_order_total
from app.services.product_service import ProductService


class OrderService:
    """Service class for order management operations"""

    def __init__(self, db: Session):
        self.db = db
        self.product_service = ProductService(db)

    def create_order(self, user_id: int, order_data: OrderCreate) -> Order:
        """Create a new order with deterministic total calculation"""
        # Validate all products and check stock
        order_items_data = []
        for item_data in order_data.items:
            product = self.product_service.get_product_by_id(item_data.product_id)
            if not product:
                raise ValueError(f"Product {item_data.product_id} not found")
            if product.status != "active":
                raise ValueError(f"Product {item_data.product_id} is not active")
            if not self.product_service.check_stock_availability(item_data.product_id, item_data.quantity):
                raise ValueError(f"Insufficient stock for product {item_data.product_id}")

            # Calculate subtotal deterministically
            subtotal = calculate_subtotal(item_data.quantity, product.price)
            order_items_data.append({
                "product": product,
                "quantity": item_data.quantity,
                "price": product.price,
                "subtotal": subtotal
            })

        # Create order
        new_order = Order(
            user_id=user_id,
            total_amount=0,  # Will be calculated
            status="pending"
        )
        self.db.add(new_order)
        self.db.flush()  # Get order ID

        # Create order items
        order_items = []
        for item_data in order_items_data:
            order_item = OrderItem(
                order_id=new_order.id,
                product_id=item_data["product"].id,
                quantity=item_data["quantity"],
                price=item_data["price"],
                subtotal=item_data["subtotal"]
            )
            order_items.append(order_item)
            self.db.add(order_item)

        # Calculate total deterministically
        new_order.total_amount = calculate_order_total(order_items)
        self.db.commit()
        self.db.refresh(new_order)
        return new_order

    def get_order_by_id(self, order_id: int, user_id: Optional[int] = None) -> Optional[Order]:
        """Get order by ID, optionally filtered by user"""
        query = self.db.query(Order).filter(Order.id == order_id)
        if user_id:
            query = query.filter(Order.user_id == user_id)
        return query.first()

    def get_user_orders(self, user_id: int, skip: int = 0, limit: int = 100) -> List[Order]:
        """Get all orders for a user"""
        return self.db.query(Order).filter(Order.user_id == user_id).offset(skip).limit(limit).all()

    def update_order_status(self, order_id: int, status: str) -> Optional[Order]:
        """Update order status"""
        order = self.get_order_by_id(order_id)
        if not order:
            return None

        order.status = status
        self.db.commit()
        self.db.refresh(order)
        return order

    def cancel_order(self, order_id: int, user_id: int) -> Optional[Order]:
        """Cancel an order"""
        order = self.get_order_by_id(order_id, user_id)
        if not order:
            return None
        if order.status not in ["pending", "paid"]:
            raise ValueError("Order cannot be canceled in current status")

        order.status = "canceled"
        self.db.commit()
        self.db.refresh(order)
        return order

    def mark_order_as_paid(self, order_id: int) -> Optional[Order]:
        """Mark order as paid and reduce stock"""
        order = self.get_order_by_id(order_id)
        if not order:
            return None

        # Reduce stock for each product in order items
        for order_item in order.order_items:
            try:
                self.product_service.reduce_stock(order_item.product_id, order_item.quantity)
            except ValueError as e:
                # If stock reduction fails, rollback
                self.db.rollback()
                raise e

        # Update order status
        order.status = "paid"
        self.db.commit()
        self.db.refresh(order)
        return order
