# bot/domain/entities/user.py
from dataclasses import dataclass, field
from uuid import uuid4, UUID
from datetime import datetime
from typing import Optional


@dataclass
class User:
    """Сущность пользователя"""
    id: UUID = field(default_factory=uuid4)
    telegram_id: int
    username: Optional[str] = None
    full_name: Optional[str] = None
    role: str = "user"
    orders_count: int = 0
    first_visited_at: datetime = field(default_factory=datetime.now)
    is_admin: bool = False
    is_banned: bool = False
    
    def ban(self) -> None:
        """Забанить пользователя"""
        self.is_banned = True
    
    def unban(self) -> None:
        """Разбанить пользователя"""
        self.is_banned = False
    
    def make_admin(self) -> None:
        """Сделать админом"""
        self.is_admin = True
        self.role = "admin"
    
    def increment_orders_count(self) -> None:
        """Увеличить счетчик заказов"""
        self.orders_count += 1