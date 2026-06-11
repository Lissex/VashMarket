# bot/domain/entities/category.py
from dataclasses import dataclass, field
from uuid import uuid4, UUID
from typing import Optional, List


@dataclass
class Category:
    """Сущность категории"""
    id: UUID = field(default_factory=uuid4)
    name: str
    description: Optional[str] = None
    slug: str
    order: int = 0
    is_active: bool = True
    parent_id: Optional[UUID] = None
    products_count: int = 0
    children: List['Category'] = field(default_factory=list)
    
    @property
    def level(self) -> int:
        """Уровень вложенности"""
        level = 0
        current = self
        while current.parent_id:
            level += 1
            # Для реального расчета нужен доступ к родителю
            break
        return level
    
    def activate(self) -> None:
        """Активировать категорию"""
        self.is_active = True
    
    def deactivate(self) -> None:
        """Деактивировать категорию"""
        self.is_active = False