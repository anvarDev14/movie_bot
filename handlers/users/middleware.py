from aiogram import types
from aiogram.dispatcher.handler import CancelHandler
from aiogram.dispatcher.middlewares import BaseMiddleware
from aiogram.utils.exceptions import MessageNotModified

from data.config import ADMINS
from handlers.users.channel_add import get_unsubscribed_channels
from handlers.users.start import get_subscription_keyboard, is_subscribed_to_all_channels
from loader import bot


class SubscriptionMiddleware(BaseMiddleware):
    async def on_pre_process_update(self, update: types.Update, data: dict):
        user_id = None
        chat_id = None
        message = None

        if update.message:
            user_id = update.message.from_user.id
            chat_id = update.message.chat.id
            message = update.message
        elif update.callback_query:
            user_id = update.callback_query.from_user.id
            chat_id = update.callback_query.message.chat.id
            message = update.callback_query.message

        if not user_id or not chat_id:
            return

        if isinstance(ADMINS, list) and user_id in ADMINS:
            return

        if not await is_subscribed_to_all_channels(user_id):
            unsubscribed = await get_unsubscribed_channels(user_id)
            text = "📌 <b>Botdan foydalanish uchun quyidagi kanallarga obuna bo'ling:</b>"
            markup = get_subscription_keyboard(unsubscribed)

            if message.chat.type == "private":
                if update.message:
                    await message.answer(text, reply_markup=markup, parse_mode="HTML")
                elif update.callback_query:
                    if message.text != text or (message.reply_markup and message.reply_markup != markup):
                        try:
                            await message.edit_text(text, reply_markup=markup, parse_mode="HTML")
                        except MessageNotModified:
                            await message.delete()
                            await message.answer(text, reply_markup=markup, parse_mode="HTML")

            else:
                try:
                    if message.text != text or message.reply_markup != markup:
                        await bot.send_message(user_id, text, reply_markup=markup, parse_mode="HTML")
                    if update.message and update.message.chat.type != "channel":
                        await message.reply("📩 Shaxsiy xabarda obuna bo'lishni tekshiring!")
                except Exception as e:
                    print(f"Foydalanuvchiga shaxsiy xabar yuborib bo'lmadi: {e}")
                    if update.message and update.message.chat.type != "channel":
                        await message.reply("🚫 Iltimos, botga shaxsiy xabar yuboring va obunani tekshiring!")
            raise CancelHandler()