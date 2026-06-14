# bot/application/use_cases/get_catalog.py
from typing import List, Dict, Any

from infrastructure.database.repositories import (
    CategoryRepository,
    ProductRepository
)


class GetCatalogUseCase:
    def __init__(
        self,
        category_repo: CategoryRepository,
        product_repo: ProductRepository
    ):
        self.category_repo = category_repo
        self.product_repo = product_repo
    
    async def get_categories(self) -> List[Dict[str, Any]]:
        categories = await self.category_repo.get_active_categories()
        return [
            {
                "id": cat.id,
                "name": cat.name,
                "description": cat.description,
                "slug": cat.slug,
                "products_count": cat.products_count
            }
            for cat in categories
        ]
    
    async def get_products_by_category(self, category_id: str) -> List[Dict[str, Any]]:  # 👈 str
        products = await self.product_repo.get_by_category(category_id)
        return [
            {
                "id": prod.id,
                "name": prod.name,
                "description": prod.description,
                "price": prod.price,
                "formatted_price": prod.formatted_price,
                "photo_url": prod.photo_url,
                "is_in_stock": prod.is_in_stock
            }
            for prod in products
        ]
    
    async def get_product_details(self, product_id: str) -> Dict[str, Any]:  # 👈 str
        product = await self.product_repo.get_by_id(product_id)
        if not product:
            raise ValueError("Товар не найден")
        return {
            "id": product.id,
            "name": product.name,
            "description": product.description,
            "price": product.price,
            "formatted_price": product.formatted_price,
            "photo_url": product.photo_url,
            "is_in_stock": product.is_in_stock,
            "category_id": product.category_id
        }