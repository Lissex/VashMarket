# bot/application/di.py
from typing import AsyncGenerator
from sqlalchemy.ext.asyncio import AsyncSession

from infrastructure.database.accessor import get_session
from infrastructure.database.repositories import (
    UserRepository,
    CategoryRepository,
    ProductRepository,
    OrderRepository
)
from bot.application.use_cases import (
    CreateOrderUseCase,
    ConfirmOrderUseCase,
    GetCatalogUseCase,
    GetUserOrdersUseCase,
    GetPendingOrdersUseCase
)


class Container:
    """DI контейнер для всех зависимостей"""
    
    def __init__(self, session: AsyncSession):
        self.session = session
        
        # Репозитории
        self.user_repo = UserRepository(session)
        self.category_repo = CategoryRepository(session)
        self.product_repo = ProductRepository(session)
        self.order_repo = OrderRepository(session)
        
        # Use Cases
        self.create_order_uc = CreateOrderUseCase(
            self.user_repo,
            self.product_repo,
            self.order_repo
        )
        self.confirm_order_uc = ConfirmOrderUseCase(self.order_repo)
        self.get_catalog_uc = GetCatalogUseCase(
            self.category_repo,
            self.product_repo
        )
        self.get_user_orders_uc = GetUserOrdersUseCase(
            self.user_repo,
            self.order_repo
        )
        self.get_pending_orders_uc = GetPendingOrdersUseCase(self.order_repo)


async def get_container() -> AsyncGenerator[Container, None]:
    """Генератор DI контейнера для каждого запроса"""
    async for session in get_session():
        yield Container(session)