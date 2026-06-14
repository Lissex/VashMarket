from aiogram import Router, types, F
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from uuid import UUID

from bot.application.di import get_container
from bot.presentation.keyboards.menu import (
    categories_keyboard,
    main_keyboard,
    products_keyboard,
    product_detail_keyboard
)

router = Router()


@router.message(F.text == "🛍 Каталог")
async def show_categories(message: types.Message):
    async for container in get_container():
        categories = await container.get_catalog_uc.get_categories()
        
        if not categories:
            await message.answer("📭 Категории пока не добавлены")
            return
        
        await message.answer(
            "📁 Выберите категорию:",
            reply_markup=categories_keyboard(categories)
        )


@router.callback_query(lambda c: c.data.startswith("category_"))
async def show_products(callback: types.CallbackQuery):
    category_id = UUID(callback.data.split("_")[1])
    
    async for container in get_container():
        products = await container.get_catalog_uc.get_products_by_category(category_id)
        
        if not products:
            await callback.message.edit_text(
                "📭 В этой категории пока нет товаров",
                reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                    [InlineKeyboardButton(text="🔙 Назад", callback_data="back_to_categories")]
                ])
            )
            return
        
        text = "🛍 Товары в категории:\n\n"
        for p in products[:5]:
            text += f"• {p['name']} - {p['formatted_price']}\n"
        
        if len(products) > 5:
            text += f"\n... и еще {len(products) - 5} товаров"
        
        await callback.message.edit_text(
            text,
            reply_markup=products_keyboard(products)
        )
    
    await callback.answer()


@router.callback_query(lambda c: c.data.startswith("product_"))
async def show_product_detail(callback: types.CallbackQuery):
    product_id = UUID(callback.data.split("_")[1])
    
    async for container in get_container():
        try:
            product = await container.get_catalog_uc.get_product_details(product_id)
            
            text = f"📦 <b>{product['name']}</b>\n\n"
            text += f"{product['description']}\n\n" if product['description'] else ""
            text += f"💰 Цена: <b>{product['formatted_price']}</b>\n"
            text += f"📦 Наличие: {'✅ Есть' if product['is_in_stock'] else '❌ Нет'}\n"
            
            if product.get('photo_url'):
                await callback.message.delete()
                await callback.message.answer_photo(
                    photo=product['photo_url'],
                    caption=text,
                    parse_mode="HTML",
                    reply_markup=product_detail_keyboard(product['id'], product['is_in_stock'])
                )
            else:
                await callback.message.edit_text(
                    text,
                    parse_mode="HTML",
                    reply_markup=product_detail_keyboard(product['id'], product['is_in_stock'])
                )
                
        except ValueError as e:
            await callback.message.edit_text(str(e))
    
    await callback.answer()


@router.callback_query(F.data == "back_to_categories")
async def back_to_categories(callback: types.CallbackQuery):
    async for container in get_container():
        categories = await container.get_catalog_uc.get_categories()
        
        await callback.message.edit_text(
            "📁 Выберите категорию:",
            reply_markup=categories_keyboard(categories)
        )
    
    await callback.answer()


@router.callback_query(F.data == "back_to_products")
async def back_to_products(callback: types.CallbackQuery):
    await callback.message.delete()
    await show_categories(callback.message)
    await callback.answer()


@router.callback_query(F.data == "back_to_main")
async def back_to_main(callback: types.CallbackQuery):
    async for container in get_container():
        user = await container.user_repo.get_by_telegram_id(callback.from_user.id)
        is_admin = user.is_admin if user else False
        
        await callback.message.delete()
        await callback.message.answer(
            "🏠 Главное меню",
            reply_markup=main_keyboard(is_admin)
        )
    
    await callback.answer()