from aiogram import Router, types, F
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from sqlalchemy import select
from uuid import uuid4

from bot.application.di import get_container
from bot.presentation.keyboards.menu import admin_keyboard, categories_management_keyboard, products_edit_keyboard, product_edit_actions_keyboard
from infrastructure.database.models import Category, Product

router = Router()


class AddProductStates(StatesGroup):
    waiting_for_photo = State()
    waiting_for_name = State()
    waiting_for_description = State()
    waiting_for_price = State()
    waiting_for_stock = State()
    waiting_for_category = State()


class CategoryStates(StatesGroup):
    waiting_for_name = State()
    waiting_for_slug = State()
    waiting_for_description = State()
    waiting_for_parent = State()


class EditProductStates(StatesGroup):
    waiting_for_new_price = State()
    waiting_for_new_stock = State()
    waiting_for_new_description = State()


@router.message(F.text == "👑 Админ панель")
async def admin_panel(message: types.Message):
    async for container in get_container():
        user = await container.user_repo.get_by_telegram_id(message.from_user.id)
        
        if not user or not user.is_admin:
            await message.answer("⛔ У вас нет доступа к админ панели")
            return
        
        await message.answer(
            "👑 Админ панель\n\nВыберите действие:",
            reply_markup=admin_keyboard()
        )


# ========== УПРАВЛЕНИЕ КАТЕГОРИЯМИ ==========

@router.callback_query(F.data == "admin_categories")
async def manage_categories(callback: types.CallbackQuery):
    async for container in get_container():
        categories = await container.get_catalog_uc.get_categories()
        
        await callback.message.edit_text(
            "📁 Управление категориями\n\nНажмите на категорию для редактирования, ❌ для удаления, или добавьте новую.",
            reply_markup=categories_management_keyboard(categories)
        )
    await callback.answer()


@router.callback_query(F.data == "add_category")
async def start_add_category(callback: types.CallbackQuery, state: FSMContext):
    await callback.message.edit_text("📝 Введите название категории:")
    await state.set_state(CategoryStates.waiting_for_name)
    await callback.answer()


@router.message(CategoryStates.waiting_for_name)
async def add_category_get_slug(message: types.Message, state: FSMContext):
    await state.update_data(name=message.text)
    
    await message.answer(
        "🔗 Введите slug (уникальный идентификатор латиницей)\n"
        "Пример: electronics, clothes, phones\n\n"
        "Можно отправить '-' для автоматической генерации из названия"
    )
    await state.set_state(CategoryStates.waiting_for_slug)


@router.message(CategoryStates.waiting_for_slug)
async def add_category_get_description(message: types.Message, state: FSMContext):
    slug = message.text.lower().replace(" ", "_") if message.text != "-" else None
    
    if slug == "-" or not slug:
        data = await state.get_data()
        slug = data['name'].lower().replace(" ", "_")
    
    await state.update_data(slug=slug)
    
    await message.answer(
        "📝 Введите описание категории (можно пропустить, отправив '-'):"
    )
    await state.set_state(CategoryStates.waiting_for_description)


@router.message(CategoryStates.waiting_for_description)
async def add_category_get_parent(message: types.Message, state: FSMContext):
    description = message.text if message.text != "-" else None
    await state.update_data(description=description)
    
    async for container in get_container():
        categories = await container.get_catalog_uc.get_categories()
        
        if categories:
            keyboard = InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(text=f"📁 {cat['name']}", callback_data=f"parent_cat_{cat['id']}")]
                for cat in categories
            ])
            keyboard.inline_keyboard.append([InlineKeyboardButton(text="🚫 Без родителя", callback_data="parent_cat_none")])
            
            await message.answer(
                "📁 Выберите родительскую категорию (или 'Без родителя'):",
                reply_markup=keyboard
            )
        else:
            await state.update_data(parent_id=None)
            await save_category(message, state, None)
            return
    
    await state.set_state(CategoryStates.waiting_for_parent)


@router.callback_query(CategoryStates.waiting_for_parent)
async def add_category_save_callback(callback: types.CallbackQuery, state: FSMContext):
    parent_id = None
    if callback.data != "parent_cat_none":
        parent_id = callback.data.split("_")[2]
    
    await state.update_data(parent_id=parent_id)
    await save_category(callback.message, state, callback)
    await callback.answer()


async def save_category(message: types.Message, state: FSMContext, callback: types.CallbackQuery = None):
    data = await state.get_data()
    
    async for container in get_container():
        try:
            existing = await container.session.execute(
                select(Category).where(Category.slug == data['slug'])
            )
            if existing.scalar_one_or_none():
                error_msg = f"❌ Категория с slug '{data['slug']}' уже существует!"
                if callback:
                    await callback.message.edit_text(error_msg)
                else:
                    await message.answer(error_msg)
                return
            
            category = Category(
                id=str(uuid4()),
                name=data['name'],
                slug=data['slug'],
                description=data.get('description'),
                parent_id=data.get('parent_id'),
                is_active=True
            )
            
            container.session.add(category)
            await container.session.commit()
            
            success_msg = f"✅ Категория {data['name']} добавлена!"
            if callback:
                await callback.message.edit_text(success_msg)
            else:
                await message.answer(success_msg)
            
            categories = await container.get_catalog_uc.get_categories()
            
            if callback:
                await callback.message.answer(
                    "📁 Управление категориями",
                    reply_markup=categories_management_keyboard(categories)
                )
            else:
                await message.answer(
                    "📁 Управление категориями",
                    reply_markup=categories_management_keyboard(categories)
                )
            
        except Exception as e:
            error_msg = f"❌ Ошибка: {str(e)}"
            if callback:
                await callback.message.edit_text(error_msg)
            else:
                await message.answer(error_msg)
    
    await state.clear()


@router.callback_query(lambda c: c.data.startswith("delete_cat_"))
async def delete_category(callback: types.CallbackQuery):
    category_id = callback.data.split("_")[2]
    
    async for container in get_container():
        category = await container.session.get(Category, category_id)
        
        if not category:
            await callback.message.edit_text("❌ Категория не найдена")
            return
        
        if category.products_count > 0:
            await callback.message.edit_text(
                f"❌ Нельзя удалить категорию {category.name}! В ней есть {category.products_count} товаров."
            )
            return
        
        await container.session.delete(category)
        await container.session.commit()
        
        await callback.message.edit_text(f"✅ Категория {category.name} удалена!")
        
        categories = await container.get_catalog_uc.get_categories()
        await callback.message.answer(
            "📁 Управление категориями",
            reply_markup=categories_management_keyboard(categories)
        )
    
    await callback.answer()


# ========== ДОБАВЛЕНИЕ ТОВАРА ==========

@router.callback_query(F.data == "admin_add_product")
async def start_add_product(callback: types.CallbackQuery, state: FSMContext):
    await callback.message.edit_text("📸 Отправьте фото товара:")
    await state.set_state(AddProductStates.waiting_for_photo)
    await callback.answer()


@router.message(AddProductStates.waiting_for_photo, F.photo)
async def add_product_get_name(message: types.Message, state: FSMContext):
    photo_file_id = message.photo[-1].file_id
    await state.update_data(photo_file_id=photo_file_id)
    
    await message.answer("📝 Введите название товара:")
    await state.set_state(AddProductStates.waiting_for_name)


@router.message(AddProductStates.waiting_for_photo)
async def add_product_photo_error(message: types.Message):
    await message.answer("❌ Пожалуйста, отправьте фото товара")


@router.message(AddProductStates.waiting_for_name)
async def add_product_get_description(message: types.Message, state: FSMContext):
    await state.update_data(name=message.text)
    await message.answer("📝 Введите описание товара (можно пропустить, отправив '-'):")
    await state.set_state(AddProductStates.waiting_for_description)


@router.message(AddProductStates.waiting_for_description)
async def add_product_get_price(message: types.Message, state: FSMContext):
    description = message.text if message.text != "-" else None
    await state.update_data(description=description)
    await message.answer("💰 Введите цену товара (в рублях, только число):\nПример: 999")
    await state.set_state(AddProductStates.waiting_for_price)


@router.message(AddProductStates.waiting_for_price)
async def add_product_get_stock(message: types.Message, state: FSMContext):
    try:
        price = float(message.text.replace(",", "."))
        if price <= 0:
            raise ValueError
    except ValueError:
        await message.answer("❌ Введите корректную цену (положительное число)")
        return
    
    await state.update_data(price=price)
    await message.answer("📦 Введите количество товара в наличии (целое число):\nПример: 10")
    await state.set_state(AddProductStates.waiting_for_stock)


@router.message(AddProductStates.waiting_for_stock)
async def add_product_get_category(message: types.Message, state: FSMContext):
    try:
        stock = int(message.text)
        if stock < 0:
            raise ValueError
    except ValueError:
        await message.answer("❌ Введите корректное количество (целое положительное число)")
        return
    
    await state.update_data(stock=stock)
    
    async for container in get_container():
        categories = await container.get_catalog_uc.get_categories()
        
        if not categories:
            await message.answer("❌ Нет доступных категорий!\nСначала создайте категорию через '📁 Управление категориями'")
            return
        
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text=f"📁 {cat['name']}", callback_data=f"add_cat_{cat['id']}")]
            for cat in categories
        ])
        
        await message.answer("📁 Выберите категорию для товара:", reply_markup=keyboard)
        await state.set_state(AddProductStates.waiting_for_category)


@router.callback_query(AddProductStates.waiting_for_category)
async def add_product_save(callback: types.CallbackQuery, state: FSMContext):
    if not callback.data.startswith("add_cat_"):
        return
    
    category_id = callback.data.split("_")[2]
    data = await state.get_data()
    
    async for container in get_container():
        try:
            product = Product(
                id=str(uuid4()),
                name=data['name'],
                description=data.get('description'),
                price=data['price'],
                photo_file_id=data['photo_file_id'],
                category_id=category_id,
                stock=data['stock'],
                is_active=True
            )
            
            container.session.add(product)
            await container.session.commit()
            
            await callback.message.edit_text(
                f"✅ Товар {data['name']} добавлен!\n\n💰 Цена: {data['price']:,.0f} ₽\n📦 Количество: {data['stock']} шт.\n\nТеперь товар виден в каталоге!"
            )
            
            await callback.message.answer("👑 Админ панель", reply_markup=admin_keyboard())
            
        except Exception as e:
            await callback.message.edit_text(f"❌ Ошибка: {str(e)}")
    
    await state.clear()
    await callback.answer()


# ========== РЕДАКТИРОВАНИЕ ТОВАРОВ ==========

@router.callback_query(F.data == "admin_edit_products")
async def edit_products_list(callback: types.CallbackQuery):
    async for container in get_container():
        products = await container.product_repo.get_all_products()
        
        if not products:
            await callback.message.edit_text(
                "📭 Нет товаров для редактирования",
                reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                    [InlineKeyboardButton(text="🔙 Назад", callback_data="back_to_admin")]
                ])
            )
            return
        
        await callback.message.edit_text(
            "📦 <b>Выберите товар для редактирования:</b>\n\nНажмите на товар, чтобы изменить его параметры.",
            parse_mode="HTML",
            reply_markup=products_edit_keyboard(products)
        )
    await callback.answer()


@router.callback_query(lambda c: c.data.startswith("edit_product_"))
async def edit_product_actions(callback: types.CallbackQuery, state: FSMContext):
    product_id = callback.data.split("_")[2]
    await state.update_data(product_id=product_id)
    
    async for container in get_container():
        product = await container.product_repo.get_by_id(product_id)
        
        if not product:
            await callback.message.edit_text("❌ Товар не найден")
            return
        
        text = f"<b>📦 {product.name}</b>\n\n"
        text += f"💰 Цена: {product.price:,.0f} ₽\n"
        text += f"📦 В наличии: {product.stock} шт.\n"
        text += f"📝 Описание: {product.description or 'Нет'}\n"
        text += f"📊 Статус: {'✅ Активен' if product.is_active else '❌ Деактивирован'}\n"
        
        await callback.message.edit_text(
            text,
            parse_mode="HTML",
            reply_markup=product_edit_actions_keyboard(product_id, product.stock)
        )
    await callback.answer()


@router.callback_query(lambda c: c.data.startswith("change_price_"))
async def change_price_start(callback: types.CallbackQuery, state: FSMContext):
    product_id = callback.data.split("_")[2]
    await state.update_data(product_id=product_id)
    await callback.message.edit_text("💰 Введите новую цену товара (в рублях):\nПример: 15000")
    await state.set_state(EditProductStates.waiting_for_new_price)
    await callback.answer()


@router.message(EditProductStates.waiting_for_new_price)
async def change_price_save(message: types.Message, state: FSMContext):
    try:
        new_price = float(message.text.replace(",", "."))
        if new_price <= 0:
            raise ValueError
    except ValueError:
        await message.answer("❌ Введите корректную цену (положительное число)")
        return
    
    data = await state.get_data()
    product_id = data['product_id']
    
    async for container in get_container():
        product = await container.product_repo.get_by_id(product_id)
        if product:
            product.price = new_price
            await container.session.commit()
            await message.answer(f"✅ Цена товара обновлена! Теперь: {new_price:,.0f} ₽")
        else:
            await message.answer("❌ Товар не найден")
    
    await state.clear()


@router.callback_query(lambda c: c.data.startswith("change_stock_"))
async def change_stock_start(callback: types.CallbackQuery, state: FSMContext):
    product_id = callback.data.split("_")[2]
    await state.update_data(product_id=product_id)
    await callback.message.edit_text("📦 Введите новое количество товара в наличии:\nПример: 10\n\nЕсли поставить 0 - товар будет скрыт из каталога")
    await state.set_state(EditProductStates.waiting_for_new_stock)
    await callback.answer()


@router.message(EditProductStates.waiting_for_new_stock)
async def change_stock_save(message: types.Message, state: FSMContext):
    try:
        new_stock = int(message.text)
        if new_stock < 0:
            raise ValueError
    except ValueError:
        await message.answer("❌ Введите корректное количество (целое неотрицательное число)")
        return
    
    data = await state.get_data()
    product_id = data['product_id']
    
    async for container in get_container():
        product = await container.product_repo.get_by_id(product_id)
        if product:
            product.stock = new_stock
            await container.session.commit()
            await message.answer(f"✅ Количество обновлено! Теперь: {new_stock} шт.")
        else:
            await message.answer("❌ Товар не найден")
    
    await state.clear()


@router.callback_query(lambda c: c.data.startswith("change_desc_"))
async def change_description_start(callback: types.CallbackQuery, state: FSMContext):
    product_id = callback.data.split("_")[2]
    await state.update_data(product_id=product_id)
    await callback.message.edit_text("📝 Введите новое описание товара:\n(можно отправить '-' чтобы очистить)")
    await state.set_state(EditProductStates.waiting_for_new_description)
    await callback.answer()


@router.message(EditProductStates.waiting_for_new_description)
async def change_description_save(message: types.Message, state: FSMContext):
    description = message.text if message.text != "-" else None
    
    data = await state.get_data()
    product_id = data['product_id']
    
    async for container in get_container():
        product = await container.product_repo.get_by_id(product_id)
        if product:
            product.description = description
            await container.session.commit()
            await message.answer(f"✅ Описание товара обновлено!")
        else:
            await message.answer("❌ Товар не найден")
    
    await state.clear()


@router.callback_query(lambda c: c.data.startswith("deactivate_"))
async def deactivate_product(callback: types.CallbackQuery):
    product_id = callback.data.split("_")[1]
    
    async for container in get_container():
        product = await container.product_repo.get_by_id(product_id)
        if product:
            product.is_active = False
            await container.session.commit()
            await callback.message.edit_text(f"❌ Товар {product.name} деактивирован!\nОн больше не показывается в каталоге.")
        else:
            await callback.message.edit_text("❌ Товар не найден")
    
    await callback.answer()


# ========== НОВЫЕ ЗАКАЗЫ ==========

@router.callback_query(F.data == "admin_pending_orders")
async def admin_pending_orders(callback: types.CallbackQuery):
    async for container in get_container():
        orders = await container.get_pending_orders_uc.execute()
        
        if not orders:
            await callback.message.edit_text(
                "📭 Нет новых заказов",
                reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                    [InlineKeyboardButton(text="🔙 Назад", callback_data="back_to_admin")]
                ])
            )
            return
        
        text = "📦 Новые заказы:\n\n"
        for order in orders[:5]:
            text += f"🆔 Заказ #{order['id']}\n"
            text += f"📦 Товар: {order['product_name']}\n"
            text += f"👤 Покупатель: @{order['username'] or 'Нет юзернейма'}\n"
            text += f"💰 Сумма: {order['formatted_price']}\n"
            text += f"📞 Телефон: {order['customer_phone']}\n"
            text += f"📍 Адрес: {order['customer_address']}\n"
            text += f"🕐 Создан: {order['created_at'].strftime('%d.%m.%Y %H:%M')}\n"
            text += "─" * 20 + "\n\n"
        
        await callback.message.edit_text(
            text,
            reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(text="🔙 Назад", callback_data="back_to_admin")]
            ])
        )
    
    await callback.answer()


@router.callback_query(lambda c: c.data.startswith("confirm_order_"))
async def confirm_order(callback: types.CallbackQuery):
    order_id = callback.data.split("_")[2]
    
    async for container in get_container():
        result = await container.confirm_order_uc.execute(order_id, callback.from_user.id)
        
        if result:
            order = result['order']
            user = result['user']
            product = result['product']
            
            await callback.bot.send_message(
                user.telegram_id,
                f"✅ Ваш заказ #{order.id} подтвержден!\n\n📦 Товар: {product.name}\n💰 Сумма: {product.formatted_price}\n\nСкоро с вами свяжется продавец."
            )
            
            await callback.message.edit_text(f"✅ Заказ #{order.id} подтвержден!\nПользователь уведомлен.")
        else:
            await callback.message.edit_text("❌ Заказ не найден или уже подтвержден")
    
    await callback.answer()


@router.callback_query(F.data == "back_to_admin")
async def back_to_admin(callback: types.CallbackQuery):
    await callback.message.edit_text("👑 Админ панель\n\nВыберите действие:", reply_markup=admin_keyboard())
    await callback.answer()