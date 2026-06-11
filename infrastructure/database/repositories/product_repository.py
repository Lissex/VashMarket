# bot/infrastructure/database/repositories/product_repository.py
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from uuid import UUID
from typing import List
from ..models import Product


class ProductRepository:
    """Репозиторий для работы с товарами"""
    
    def __init__(self, session: AsyncSession):
        self.session = session
    
    async def get_by_category(self, category_id: UUID) -> List[Product]:
        result = await self.session.execute(
            select(Product)
            .where(Product.category_id == category_id, Product.is_active == True, Product.stock > 0)
            .order_by(Product.name)
        )
        return result.scalars().all()
    
    async def get_by_id(self, product_id: UUID) -> Product | None:
        result = await self.session.execute(
            select(Product).where(Product.id == product_id, Product.is_active == True)
        )
        return result.scalar_one_or_none()
    
    async def reduce_stock(self, product_id: UUID, quantity: int = 1) -> bool:
        product = await self.get_by_id(product_id)
        if product and product.stock >= quantity:
            product.stock -= quantity
            await self.session.flush()
            return True
        return False