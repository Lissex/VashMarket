# bot/infrastructure/database/repositories/category_repository.py
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from uuid import UUID
from typing import List
from ..models import Category


class CategoryRepository:
    """Репозиторий для работы с категориями"""
    
    def __init__(self, session: AsyncSession):
        self.session = session
    
    async def get_active_categories(self) -> List[Category]:
        result = await self.session.execute(
            select(Category)
            .where(Category.is_active == True, Category.parent_id == None)
            .order_by(Category.order)
        )
        return result.scalars().all()
    
    async def get_by_slug(self, slug: str) -> Category | None:
        result = await self.session.execute(
            select(Category).where(Category.slug == slug, Category.is_active == True)
        )
        return result.scalar_one_or_none()
    
    async def get_with_children(self, category_id: UUID) -> Category | None:
        result = await self.session.execute(
            select(Category)
            .where(Category.id == category_id)
            .options(selectinload(Category.children))
        )
        return result.scalar_one_or_none()