# bot/infrastructure/database/base.py
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy import DateTime, func, String
from datetime import datetime
from uuid import uuid4, UUID


class Base(DeclarativeBase):
    """Базовая модель для всех таблиц"""
    
    __abstract__ = True
    
    id: Mapped[UUID] = mapped_column(
        String(36),  # UUID как строка
        primary_key=True,
        default=lambda: str(uuid4())
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False
    )