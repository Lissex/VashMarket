from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List, Optional
from ..models import Product


class ProductRepository:
    def __init__(self, session: AsyncSession):
        self.session = session
    
    async def get_by_category(self, category_id: str) -> List[Product]:
        result = await self.session.execute(
            select(Product)
            .where(Product.category_id == str(category_id))
            .where(Product.is_active == True)
            .where(Product.stock > 0)
            .order_by(Product.name)
        )
        return result.scalars().all()
    
    async def get_by_id(self, product_id: str) -> Optional[Product]:
        result = await self.session.execute(
            select(Product).where(Product.id == str(product_id), Product.is_active == True)
        )
        return result.scalar_one_or_none()
    
    async def reduce_stock(self, product_id: str, quantity: int = 1) -> bool:
        product = await self.get_by_id(product_id)
        if product and product.stock >= quantity:
            product.stock -= quantity
            await self.session.flush()
            return True
        return False
    
    async def get_all_products(self) -> List[Product]:
        result = await self.session.execute(
            select(Product).where(Product.is_active == True).order_by(Product.name)
        )
        return result.scalars().all()