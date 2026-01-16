from sqlalchemy.orm import Session
from typing import List, Set, Optional
from app.models.category import Category
from app.models.product import Product
from app.core.cache import get_cache, set_cache, delete_cache


class CategoryService:
    """Service class for category management with DFS traversal"""

    def __init__(self, db: Session):
        self.db = db

    def get_category_tree(self, category_id: int) -> List[Category]:
        """
        Get category tree using DFS traversal with caching.
        Returns all categories in the subtree rooted at category_id.
        """
        cache_key = f"category_tree:{category_id}"
        
        # Try to get from cache
        cached_tree = get_cache(cache_key)
        if cached_tree:
            # Reconstruct Category objects from cached data
            categories = []
            for cat_data in cached_tree:
                cat = self.db.query(Category).filter(Category.id == cat_data["id"]).first()
                if cat:
                    categories.append(cat)
            return categories

        # Perform DFS traversal
        visited: Set[int] = set()
        result: List[Category] = []

        def dfs(cat_id: int):
            if cat_id in visited:
                return
            visited.add(cat_id)

            category = self.db.query(Category).filter(Category.id == cat_id).first()
            if category:
                result.append(category)
                # Get children
                children = self.db.query(Category).filter(Category.parent_id == cat_id).all()
                for child in children:
                    dfs(child.id)

        dfs(category_id)

        # Cache the result (store as list of dicts for serialization)
        cache_data = [{"id": cat.id, "name": cat.name, "parent_id": cat.parent_id} for cat in result]
        set_cache(cache_key, cache_data, ttl=3600)  # Cache for 1 hour

        return result

    def get_related_products(self, product_id: int, limit: int = 10) -> List[Product]:
        """
        Get related products using DFS traversal of category tree.
        Finds products in the same category subtree.
        """
        cache_key = f"product_recommendations:{product_id}"
        
        # Try to get from cache
        cached_products = get_cache(cache_key)
        if cached_products:
            product_ids = [p["id"] for p in cached_products]
            return self.db.query(Product).filter(Product.id.in_(product_ids)).all()

        # Get product's category
        product = self.db.query(Product).filter(Product.id == product_id).first()
        if not product or not product.category_id:
            return []

        # Get all categories in the subtree
        category_tree = self.get_category_tree(product.category_id)
        category_ids = [cat.id for cat in category_tree]

        # Get products from these categories (excluding the original product)
        related_products = self.db.query(Product).filter(
            Product.category_id.in_(category_ids),
            Product.id != product_id,
            Product.status == "active"
        ).limit(limit).all()

        # Cache the result
        cache_data = [{"id": p.id, "name": p.name} for p in related_products]
        set_cache(cache_key, cache_data, ttl=3600)

        return related_products

    def get_category_by_id(self, category_id: int) -> Optional[Category]:
        """Get category by ID"""
        return self.db.query(Category).filter(Category.id == category_id).first()

    def get_all_categories(self) -> List[Category]:
        """Get all categories"""
        return self.db.query(Category).all()

    def invalidate_category_cache(self, category_id: int):
        """Invalidate cache for a category tree"""
        delete_cache(f"category_tree:{category_id}")
        # Also invalidate product recommendations that might use this category
        delete_cache(f"product_recommendations:*")
