from aiogram import Router, types, F
from aiogram.filters import CommandStart, Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

from bot.application.di import get_container
from bot.presentation.keyboards.menu import main_keyboard

router = Router()

# СПИСОК АДМИНОВ (добавь свои Telegram ID)
ADMIN_IDS = [
    123456789,  # Замени на свой ID
]


class OrderStates(StatesGroup):
    waiting_for_phone = State()
    waiting_for_address = State()


@router.message(CommandStart())
async def cmd_start(message: types.Message):
    """Обработчик команды /start"""
    async for container in get_container():
        user = await container.user_repo.get_or_create(
            telegram_id=message.from_user.id,
            username=message.from_user.username,
            full_name=message.from_user.full_name
        )
        
        if message.from_user.id in ADMIN_IDS and not user.is_admin:
            user.is_admin = True
            user.role = "admin"
            await container.session.commit()
            await message.answer("🎉 Вы назначены администратором!\nВам доступна админ-панель.")
        
        is_admin = user.is_admin
        
        await message.answer(
            f"👋 Привет, {message.from_user.full_name}!\n\n"
            f"Добро пожаловать в магазин!\n"
            f"Здесь ты можешь посмотреть каталог и сделать заказ.\n\n"
            f"📖 Отправь /help для справки.",
            reply_markup=main_keyboard(is_admin)
        )


@router.message(Command("help"))
async def cmd_help(message: types.Message):
    """Команда /help - справка"""
    async for container in get_container():
        user = await container.user_repo.get_by_telegram_id(message.from_user.id)
        is_admin = user.is_admin if user else False
        
        help_text = """
📖 <b>Справка по боту</b>

🛍 <b>Каталог</b> - просмотр товаров по категориям
📋 <b>Мои заказы</b> - история ваших заказов

<b>Как купить:</b>
1. Выберите товар в каталоге
2. Нажмите "Купить"
3. Укажите телефон и адрес
4. Дождитесь подтверждения от продавца

<b>Статусы заказов:</b>
⏳ Ожидает подтверждения администратора
✅ Подтвержден
💰 Оплачен
📦 Отправлен
🎉 Выполнен
❌ Отменен

По вопросам: @hayk_11_99
"""
        
        if is_admin:
            help_text += """
\n━━━━━━━━━━━━━━━━━━━━
👑 <b>Админ команды:</b>

📁 <b>Управление категориями:</b>
   • Добавление категории
   • Редактирование категории
   • Удаление категории

🛍 <b>Добавление товара:</b>
   • Отправь фото
   • Название, описание, цена
   • Выбор категории

📦 <b>Подтверждение заказов:</b>
   • Новые заказы
   • Подтверждение кнопкой

💡 <b>Советы:</b>
• Описание можно пропустить, отправив "-"
• Цену указывать только числом
• Slug генерируется автоматически из названия
"""
        
        await message.answer(help_text, parse_mode="HTML")