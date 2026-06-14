from aiogram import Router, types, F
from aiogram.fsm.context import FSMContext
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from uuid import UUID

from bot.application.di import get_container
from bot.presentation.handlers.start import OrderStates
from bot.presentation.keyboards.menu import main_keyboard

router = Router()

# TODO: Заменить на реальный ID продавца
SELLER_TELEGRAM_ID = 5581350056


@router.callback_query(lambda c: c.data.startswith("buy_"))
async def start_buy(callback: types.CallbackQuery, state: FSMContext):
    product_id = callback.data.split("_")[1]
    await state.update_data(product_id=product_id)
    
    await callback.message.answer(
        "📞 Пожалуйста, отправьте ваш номер телефона для связи:\n"
        "(можно отправить контактом или просто текстом)"
    )
    await state.set_state(OrderStates.waiting_for_phone)
    await callback.answer()


@router.message(OrderStates.waiting_for_phone)
async def get_phone(message: types.Message, state: FSMContext):
    phone = message.contact.phone_number if message.contact else message.text
    await state.update_data(customer_phone=phone)
    
    await message.answer(
        "📍 Пожалуйста, отправьте ваш адрес доставки:"
    )
    await state.set_state(OrderStates.waiting_for_address)


@router.message(OrderStates.waiting_for_address)
async def get_address(message: types.Message, state: FSMContext):
    address = message.text
    data = await state.get_data()
    
    product_id = UUID(data['product_id'])
    phone = data['customer_phone']
    
    async for container in get_container():
        try:
            result = await container.create_order_uc.execute(
                telegram_id=message.from_user.id,
                product_id=product_id,
                customer_phone=phone,
                customer_address=address,
                customer_name=message.from_user.full_name
            )
            
            order = result['order']
            product = result['product']
            
            await message.answer(
                f"✅ Заказ #{order.id} оформлен!\n\n"
                f"📦 Товар: {product.name}\n"
                f"💰 Сумма: {product.formatted_price}\n"
                f"📞 Телефон: {phone}\n"
                f"📍 Адрес: {address}\n\n"
                f"⏳ Ожидайте подтверждения от продавца.\n"
                f"Продавец свяжется с вами в ближайшее время.",
                reply_markup=main_keyboard(False)
            )
            
            await message.bot.send_message(
                SELLER_TELEGRAM_ID,
                f"🆕 <b>НОВЫЙ ЗАКАЗ!</b>\n\n"
                f"🆔 Заказ: #{order.id}\n"
                f"📦 Товар: {product.name}\n"
                f"💰 Сумма: {product.formatted_price}\n"
                f"👤 Покупатель: @{message.from_user.username or 'Нет юзернейма'}\n"
                f"📞 Телефон: {phone}\n"
                f"📍 Адрес: {address}\n\n"
                f"⏳ Статус: ожидает подтверждения",
                parse_mode="HTML",
                reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                    [InlineKeyboardButton(
                        text="✅ Подтвердить заказ",
                        callback_data=f"confirm_order_{order.id}"
                    )]
                ])
            )
            
        except ValueError as e:
            await message.answer(f"❌ Ошибка: {str(e)}")
    
    await state.clear()


@router.message(F.text == "📋 Мои заказы")
async def my_orders(message: types.Message):
    async for container in get_container():
        orders = await container.get_user_orders_uc.execute(message.from_user.id)
        
        if not orders:
            await message.answer("📭 У вас пока нет заказов")
            return
        
        text = "📋 <b>Ваши заказы:</b>\n\n"
        for order in orders[:10]:
            text += f"{order['status_emoji']} <b>Заказ #{order['id']}</b>\n"
            text += f"📦 Товар: {order['product_name']}\n"
            text += f"💰 Сумма: {order['formatted_price']}\n"
            text += f"📅 Дата: {order['created_at'].strftime('%d.%m.%Y %H:%M')}\n"
            text += f"📊 Статус: {order['status_text']}\n"
            text += "─" * 20 + "\n\n"
        
        if len(orders) > 10:
            text += f"\n... и еще {len(orders) - 10} заказов"
        
        await message.answer(text, parse_mode="HTML")