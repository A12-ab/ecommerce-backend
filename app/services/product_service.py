from sqlalchemy.orm import Session
from typing import List, Optional
from app.models.product import Product
from app.schemas.product import ProductCreate, ProductUpdate
from app.core.algorithms import reduce_stock_quantity


class ProductService:
    """Service class for product management operations"""

    def __init__(self, db: Session):
        self.db = db

    def create_product(self, product_data: ProductCreate) -> Product:
        """Create a new product"""
        # Check if SKU already exists
        existing_product = self.db.query(Product).filter(Product.sku == product_data.sku).first()
        if existing_product:
            raise ValueError("Product with this SKU already exists")

        new_product = Product(
            name=product_data.name,
            sku=product_data.sku,
            description=product_data.description,
            price=product_data.price,
            stock=product_data.stock,
            status=product_data.status,
            category_id=product_data.category_id
        )
        self.db.add(new_product)
        self.db.commit()
        self.db.refresh(new_product)
        return new_product

    def get_product_by_id(self, product_id: int) -> Optional[Product]:
        """Get product by ID"""
        return self.db.query(Product).filter(Product.id == product_id).first()

    def get_all_products(self, skip: int = 0, limit: int = 100, status: Optional[str] = None) -> List[Product]:
        """Get all products with optional filtering"""
        query = self.db.query(Product)
        if status:
            query = query.filter(Product.status == status)
        return query.offset(skip).limit(limit).all()

    def update_product(self, product_id: int, product_data: ProductUpdate) -> Optional[Product]:
        """Update a product"""
        product = self.get_product_by_id(product_id)
        if not product:
            return None

        update_data = product_data.model_dump(exclude_unset=True)
        
        # Check SKU uniqueness if updating SKU
        if "sku" in update_data and update_data["sku"] != product.sku:
            existing = self.db.query(Product).filter(Product.sku == update_data["sku"]).first()
            if existing:
                raise ValueError("Product with this SKU already exists")

        for field, value in update_data.items():
            setattr(product, field, value)

        self.db.commit()
        self.db.refresh(product)
        return product

    def delete_product(self, product_id: int) -> bool:
        """Delete a product"""
        product = self.get_product_by_id(product_id)
        if not product:
            return False
        self.db.delete(product)
        self.db.commit()
        return True

    def reduce_stock(self, product_id: int, quantity: int) -> Product:
        """Reduce product stock atomically"""
        product = self.get_product_by_id(product_id)
        if not product:
            raise ValueError("Product not found")
        
        new_stock = reduce_stock_quantity(product.stock, quantity)
        product.stock = new_stock
        self.db.commit()
        self.db.refresh(product)
        return product

    def check_stock_availability(self, product_id: int, quantity: int) -> bool:
        """Check if product has sufficient stock"""
        product = self.get_product_by_id(product_id)
        if not product:
            return False
        return product.stock >= quantity
