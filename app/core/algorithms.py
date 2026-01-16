from decimal import Decimal
from typing import List
from app.models.order import OrderItem


def calculate_subtotal(quantity: int, price: Decimal) -> Decimal:
    """
    Deterministic algorithm to calculate subtotal.
    Always returns the same result for the same inputs.
    """
    return Decimal(str(quantity)) * Decimal(str(price))


def calculate_order_total(order_items: List[OrderItem]) -> Decimal:
    """
    Deterministic algorithm to calculate order total.
    Sums all subtotals in a consistent order.
    """
    total = Decimal('0.00')
    # Sort by item id if available, otherwise maintain order
    sorted_items = sorted(order_items, key=lambda x: x.id if x.id else 0)
    for item in sorted_items:
        total += Decimal(str(item.subtotal))
    return total


def reduce_stock_quantity(current_stock: int, quantity_to_reduce: int) -> int:
    """
    Deterministic algorithm to reduce stock.
    Returns new stock quantity after reduction.
    """
    if current_stock < quantity_to_reduce:
        raise ValueError(f"Insufficient stock. Available: {current_stock}, Requested: {quantity_to_reduce}")
    return current_stock - quantity_to_reduce
