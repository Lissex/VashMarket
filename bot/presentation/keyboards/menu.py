from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton


def main_keyboard(is_admin: bool = False) -> ReplyKeyboardMarkup:
    buttons = [
        [KeyboardButton(text="🛍 Каталог")],
        [KeyboardButton(text="📋 Мои заказы")]
    ]
    if is_admin:
        buttons.append([KeyboardButton(text="👑 Админ панель")])
    return ReplyKeyboardMarkup(keyboard=buttons, resize_keyboard=True)


def categories_keyboard(categories: list) -> InlineKeyboardMarkup:
    buttons = []
    for cat in categories:
        buttons.append([InlineKeyboardButton(text=f"📁 {cat['name']} ({cat['products_count']})", callback_data=f"category_{cat['id']}")])
    buttons.append([InlineKeyboardButton(text="🔙 Назад", callback_data="back_to_main")])
    return InlineKeyboardMarkup(inline_keyboard=buttons)


def products_keyboard(products: list) -> InlineKeyboardMarkup:
    buttons = []
    for prod in products:
        buttons.append([InlineKeyboardButton(text=f"🛒 {prod['name']} - {prod['formatted_price']}", callback_data=f"product_{prod['id']}")])
    buttons.append([InlineKeyboardButton(text="🔙 Назад", callback_data="back_to_categories")])
    return InlineKeyboardMarkup(inline_keyboard=buttons)


def product_detail_keyboard(product_id: str, is_in_stock: bool) -> InlineKeyboardMarkup:
    buttons = []
    if is_in_stock:
        buttons.append([InlineKeyboardButton(text="✅ Купить", callback_data=f"buy_{product_id}")])
    buttons.append([InlineKeyboardButton(text="🔙 Назад", callback_data="back_to_products")])
    return InlineKeyboardMarkup(inline_keyboard=buttons)


def admin_keyboard() -> InlineKeyboardMarkup:
    buttons = [
        [InlineKeyboardButton(text="📁 Управление категориями", callback_data="admin_categories")],
        [InlineKeyboardButton(text="➕ Добавить товар", callback_data="admin_add_product")],
        [InlineKeyboardButton(text="✏️ Редактировать товары", callback_data="admin_edit_products")],
        [InlineKeyboardButton(text="📦 Новые заказы", callback_data="admin_pending_orders")],
        [InlineKeyboardButton(text="🔙 Назад", callback_data="back_to_main")]
    ]
    return InlineKeyboardMarkup(inline_keyboard=buttons)


def categories_management_keyboard(categories: list) -> InlineKeyboardMarkup:
    buttons = []
    for cat in categories:
        buttons.append([
            InlineKeyboardButton(text=f"📁 {cat['name']} ({cat['products_count']})", callback_data=f"edit_cat_{cat['id']}"),
            InlineKeyboardButton(text="❌", callback_data=f"delete_cat_{cat['id']}")
        ])
    buttons.append([InlineKeyboardButton(text="➕ Добавить категорию", callback_data="add_category")])
    buttons.append([InlineKeyboardButton(text="🔙 Назад", callback_data="back_to_admin")])
    return InlineKeyboardMarkup(inline_keyboard=buttons)


def products_edit_keyboard(products: list) -> InlineKeyboardMarkup:
    buttons = []
    for prod in products:
        stock_status = f"✅ {prod.stock} шт" if prod.stock > 0 else "❌ Нет в наличии"
        buttons.append([InlineKeyboardButton(text=f"✏️ {prod.name} - {prod.price}₽ ({stock_status})", callback_data=f"edit_product_{prod.id}")])
    buttons.append([InlineKeyboardButton(text="🔙 Назад", callback_data="back_to_admin")])
    return InlineKeyboardMarkup(inline_keyboard=buttons)


def product_edit_actions_keyboard(product_id: str, current_stock: int) -> InlineKeyboardMarkup:
    buttons = [
        [InlineKeyboardButton(text="💰 Изменить цену", callback_data=f"change_price_{product_id}")],
        [InlineKeyboardButton(text="📦 Изменить количество", callback_data=f"change_stock_{product_id}")],
        [InlineKeyboardButton(text="📝 Изменить описание", callback_data=f"change_desc_{product_id}")],
        [InlineKeyboardButton(text="❌ Деактивировать", callback_data=f"deactivate_{product_id}")],
        [InlineKeyboardButton(text="🔙 Назад", callback_data="admin_edit_products")]
    ]
    return InlineKeyboardMarkup(inline_keyboard=buttons)