import sys
import os
from decimal import Decimal

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from sqlalchemy.orm import Session
from app.database import SessionLocal, engine
from app.models.category import Category
from app.models.product import Product
from app.database import Base


def seed_categories_and_products():
    """Seed categories and products"""
    # Create tables if they don't exist
    Base.metadata.create_all(bind=engine)
    
    db: Session = SessionLocal()
    try:
        # Create categories
        electronics = Category(name="Electronics", description="Electronic devices and gadgets")
        db.add(electronics)
        db.flush()

        phones = Category(name="Smartphones", parent_id=electronics.id, description="Mobile phones")
        laptops = Category(name="Laptops", parent_id=electronics.id, description="Laptop computers")
        db.add(phones)
        db.add(laptops)
        db.flush()

        clothing = Category(name="Clothing", description="Apparel and fashion")
        db.add(clothing)
        db.flush()

        shirts = Category(name="Shirts", parent_id=clothing.id, description="T-shirts and shirts")
        pants = Category(name="Pants", parent_id=clothing.id, description="Trousers and pants")
        db.add(shirts)
        db.add(pants)
        db.flush()

        # Create products
        products_data = [
            {
                "name": "iPhone 15 Pro",
                "sku": "IPHONE15PRO",
                "description": "Latest iPhone with advanced features",
                "price": Decimal("999.99"),
                "stock": 50,
                "status": "active",
                "category_id": phones.id
            },
            {
                "name": "Samsung Galaxy S24",
                "sku": "SGS24",
                "description": "Flagship Android smartphone",
                "price": Decimal("899.99"),
                "stock": 40,
                "status": "active",
                "category_id": phones.id
            },
            {
                "name": "MacBook Pro 16",
                "sku": "MBP16",
                "description": "Professional laptop for developers",
                "price": Decimal("2499.99"),
                "stock": 20,
                "status": "active",
                "category_id": laptops.id
            },
            {
                "name": "Dell XPS 15",
                "sku": "DELLXPS15",
                "description": "High-performance Windows laptop",
                "price": Decimal("1799.99"),
                "stock": 25,
                "status": "active",
                "category_id": laptops.id
            },
            {
                "name": "Cotton T-Shirt",
                "sku": "TSHIRT001",
                "description": "Comfortable cotton t-shirt",
                "price": Decimal("19.99"),
                "stock": 100,
                "status": "active",
                "category_id": shirts.id
            },
            {
                "name": "Denim Jeans",
                "sku": "JEANS001",
                "description": "Classic blue denim jeans",
                "price": Decimal("49.99"),
                "stock": 75,
                "status": "active",
                "category_id": pants.id
            },
            {
                "name": "Wireless Earbuds",
                "sku": "EARBUDS001",
                "description": "Noise-cancelling wireless earbuds",
                "price": Decimal("129.99"),
                "stock": 60,
                "status": "active",
                "category_id": electronics.id
            },
            {
                "name": "Smart Watch",
                "sku": "WATCH001",
                "description": "Fitness tracking smartwatch",
                "price": Decimal("299.99"),
                "stock": 30,
                "status": "active",
                "category_id": electronics.id
            }
        ]

        for product_data in products_data:
            # Check if product already exists
            existing = db.query(Product).filter(Product.sku == product_data["sku"]).first()
            if not existing:
                product = Product(**product_data)
                db.add(product)

        db.commit()
        print("Categories and products seeded successfully!")
        print(f"Created {len(products_data)} products across multiple categories")
    except Exception as e:
        print(f"Error seeding products: {e}")
        db.rollback()
    finally:
        db.close()


if __name__ == "__main__":
    seed_categories_and_products()
