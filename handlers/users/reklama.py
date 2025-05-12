import datetime
import asyncio
from data.config import ADMINS
from loader import bot, dp, user_db
from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.dispatcher.filters import Text
from aiogram.utils.exceptions import BotBlocked, ChatNotFound, RetryAfter, Unauthorized

# Reklama yuborish jarayonlarini saqlash uchun ro'yxat
advertisements = []

class ReklamaTuriState(StatesGroup):
    tur = State()
    vaqt = State()
    time_value = State()
    content = State()
    buttons = State()

class Advertisement:
    def __init__(self, ad_id, message, ad_type, keyboard=None, send_time=None, creator_id=None):
        self.ad_id = ad_id
        self.message = message
        self.ad_type = ad_type
        self.keyboard = keyboard
        self.send_time = send_time
        self.creator_id = creator_id
        self.running = False
        self.paused = False
        self.sent_count = 0
        self.failed_count = 0
        self.total_users = 0
        self.current_message = None  # Admin bilan aloqa uchun xabar
        self.task = None

    async def start(self):
        self.running = True
        if self.send_time:
            delay = (self.send_time - datetime.datetime.now()).total_seconds()
            if delay > 0:
                await asyncio.sleep(delay)
        users = user_db.select_all_users()
        self.total_users = len(users)
        self.current_message = await bot.send_message(
            chat_id=self.creator_id,
            text=f"Reklama #{self.ad_id} yuborish boshlandi.\nYuborilgan: {self.sent_count}\nYuborilmagan: {self.failed_count}\nUmumiy: {self.sent_count + self.failed_count}/{self.total_users}\n\nStatus: Davom etmoqda",
            reply_markup=get_status_keyboard(self.ad_id)
        )
        for user in users:
            if not self.running:
                break
            while self.paused:
                await asyncio.sleep(1)
                if not self.running:
                    break
            if not self.running:
                break
            try:
                await send_advertisement_to_user(user[1], self)
                self.sent_count += 1
            except (BotBlocked, ChatNotFound, Unauthorized):
                self.failed_count += 1
            except RetryAfter as e:
                await asyncio.sleep(e.timeout)
            await asyncio.sleep(0.1)
            if self.sent_count % 10 == 0:
                await self.update_status_message()
        self.running = False
        self.paused = False
        await self.update_status_message(finished=True)

    async def pause(self):
        self.paused = True
        await self.update_status_message()

    async def resume(self):
        self.paused = False
        await self.update_status_message()

    async def stop(self):
        self.running = False
        await self.update_status_message(stopped=True)

    async def update_status_message(self, finished=False, stopped=False):
        status = "Yakunlandi" if finished else ("To'xtatildi" if stopped else ("Pauza holatida" if self.paused else "Davom etmoqda"))
        if self.current_message:
            await self.current_message.edit_text(
                text=f"Reklama #{self.ad_id}\nYuborilgan: {self.sent_count}\nYuborilmagan: {self.failed_count}\nUmumiy: {self.sent_count + self.failed_count}/{self.total_users}\n\nStatus: {status}",
                reply_markup=None if finished or stopped else get_status_keyboard(self.ad_id, self.paused)
            )


async def send_advertisement_to_user(chat_id, advertisement: Advertisement):
    message = advertisement.message
    ad_type = advertisement.ad_type
    keyboard = advertisement.keyboard
    caption = message.caption or message.text or "Matn mavjud emas."
    if ad_type == 'ad_type_text':
        await bot.send_message(chat_id=chat_id, text=caption)
    elif ad_type == 'ad_type_button':
        await handle_content_with_keyboard(chat_id, message, keyboard, caption)
    elif ad_type == 'ad_type_forward':
        await bot.forward_message(chat_id=chat_id, from_chat_id=message.chat.id, message_id=message.message_id)
    elif ad_type == 'ad_type_any':
        await handle_non_text_content(chat_id, message)
    else:
        await handle_non_text_content(chat_id, message)

async def handle_content_with_keyboard(chat_id, message, keyboard, caption):
    if message.content_type == types.ContentType.TEXT:
        await bot.send_message(chat_id=chat_id, text=caption, reply_markup=keyboard)
    elif message.content_type == types.ContentType.PHOTO:
        await bot.send_photo(chat_id=chat_id, photo=message.photo[-1].file_id, caption=caption, reply_markup=keyboard)
    elif message.content_type == types.ContentType.VIDEO:
        await bot.send_video(chat_id=chat_id, video=message.video.file_id, caption=caption, reply_markup=keyboard)
    elif message.content_type == types.ContentType.DOCUMENT:
        await bot.send_document(chat_id=chat_id, document=message.document.file_id, caption=caption, reply_markup=keyboard)
    elif message.content_type == types.ContentType.AUDIO:
        await bot.send_audio(chat_id=chat_id, audio=message.audio.file_id, caption=caption, reply_markup=keyboard)
    elif message.content_type == types.ContentType.ANIMATION:
        await bot.send_animation(chat_id=chat_id, animation=message.animation.file_id, caption=caption, reply_markup=keyboard)
    else:
        await bot.send_message(chat_id=chat_id, text=caption, reply_markup=keyboard)

async def handle_non_text_content(chat_id, message):
    if message.content_type == types.ContentType.TEXT:
        text = message.text or "Matn mavjud emas."
        await bot.send_message(chat_id=chat_id, text=text)
    elif message.content_type == types.ContentType.PHOTO:
        await bot.send_photo(chat_id=chat_id, photo=message.photo[-1].file_id, caption=message.caption)
    elif message.content_type == types.ContentType.VIDEO:
        await bot.send_video(chat_id=chat_id, video=message.video.file_id, caption=message.caption)
    elif message.content_type == types.ContentType.DOCUMENT:
        await bot.send_document(chat_id=chat_id, document=message.document.file_id, caption=message.caption)
    elif message.content_type == types.ContentType.AUDIO:
        await bot.send_audio(chat_id=chat_id, audio=message.audio.file_id, caption=message.caption)
    elif message.content_type == types.ContentType.ANIMATION:
        await bot.send_animation(chat_id=chat_id, animation=message.animation.file_id, caption=message.caption)
    else:
        await bot.send_message(chat_id=chat_id, text="Yuboriladigan kontent turi qo'llab-quvvatlanmaydi.")

async def check_super_admin_permission(telegram_id: int):
    return telegram_id in ADMINS

async def check_admin_permission(telegram_id: int):
    user = user_db.select_user(telegram_id=telegram_id)
    if not user:
        return False
    user_id = user[0]
    admin = user_db.check_if_admin(user_id=user_id)
    return admin

@dp.message_handler(text="📣 Reklama")
async def reklama_handler(message: types.Message):
    telegram_id = message.from_user.id
    if await check_admin_permission(telegram_id) or await check_super_admin_permission(telegram_id):
        await ReklamaTuriState.tur.set()  # Reklama turini tanlash holatiga o'tish
        await bot.send_message(chat_id=message.chat.id, text="Reklama turini tanlang:", reply_markup=get_ad_type_keyboard())
    else:
        await message.reply("Sizda ushbu amalni bajarish uchun ruxsat yo'q.")



@dp.callback_query_handler(lambda c: c.data in ["ad_type_text", "ad_type_forward", "ad_type_button", "ad_type_any"], state=ReklamaTuriState.tur)
async def handle_ad_type(callback_query: types.CallbackQuery, state: FSMContext):
    await state.update_data(ad_type=callback_query.data)
    await ReklamaTuriState.vaqt.set()
    await callback_query.message.edit_text("Reklama yuborish vaqtini tanlang:", reply_markup=get_time_keyboard())

@dp.callback_query_handler(lambda c: c.data in ["send_now", "send_later"], state=ReklamaTuriState.vaqt)
async def handle_send_time(callback_query: types.CallbackQuery, state: FSMContext):
    await state.update_data(send_time=callback_query.data)
    if callback_query.data == "send_later":
        await ReklamaTuriState.time_value.set()
        await callback_query.message.edit_text("Reklamani yuborish uchun vaqtni kiriting (HH:MM formatida):")
    else:
        await ReklamaTuriState.content.set()
        await callback_query.message.edit_text("Reklama kontentini yuboring:", reply_markup=get_cancel_keyboard())

@dp.message_handler(state=ReklamaTuriState.time_value)
async def handle_time_input(message: types.Message, state: FSMContext):
    time_value = message.text.strip()
    try:
        send_time = datetime.datetime.strptime(time_value, '%H:%M')
        now = datetime.datetime.now()
        send_time = send_time.replace(year=now.year, month=now.month, day=now.day)
        if send_time < now:
            send_time += datetime.timedelta(days=1)
        await state.update_data(send_time_value=send_time)
        await ReklamaTuriState.content.set()
        await message.reply("Reklama kontentini yuboring:", reply_markup=get_cancel_keyboard())
    except ValueError:
        await message.reply("❌ Vaqt formati noto'g'ri. Iltimos, HH:MM formatida kiriting.")

@dp.message_handler(state=ReklamaTuriState.content, content_types=types.ContentType.ANY)
async def rek_state(message: types.Message, state: FSMContext):
    telegram_id = message.from_user.id
    if await check_admin_permission(telegram_id) or await check_super_admin_permission(telegram_id):
        data = await state.get_data()
        ad_type = data.get('ad_type')
        if ad_type == 'ad_type_button':
            await state.update_data(ad_content=message)
            await ReklamaTuriState.buttons.set()
            await message.reply("Iltimos, tugmalarni quyidagi formatda yuboring:\nButton1 Text - URL1, Button2 Text - URL2", reply_markup=get_cancel_keyboard())
        else:
            await state.update_data(ad_content=message)
            await bot.send_message(chat_id=message.chat.id, text="Reklamani yuborishni tasdiqlaysizmi?", reply_markup=get_confirm_keyboard())
    else:
        await message.reply("Sizda ushbu amalni bajarish uchun ruxsat yo'q.")

@dp.message_handler(state=ReklamaTuriState.buttons)
async def handle_buttons_input(message: types.Message, state: FSMContext):
    buttons_text = message.text.strip()
    buttons = []
    try:
        for button_data in buttons_text.split(','):
            text_url = button_data.strip().split('-')
            if len(text_url) != 2:
                raise ValueError("Incorrect format")
            text = text_url[0].strip()
            url = text_url[1].strip()
            buttons.append(types.InlineKeyboardButton(text=text, url=url))
    except Exception as e:
        await message.reply("❌ Tugmalar formati noto'g'ri. Iltimos, qaytadan kiriting.\nFormat: Button1 Text - URL1, Button2 Text - URL2")
        return
    keyboard = types.InlineKeyboardMarkup()
    keyboard.add(*buttons)
    data = await state.get_data()
    ad_message = data.get('ad_content')
    await state.update_data(keyboard=keyboard)
    await bot.send_message(chat_id=message.chat.id, text="Reklamani yuborishni tasdiqlaysizmi?", reply_markup=get_confirm_keyboard())


@dp.callback_query_handler(lambda c: c.data == "cancel_ad", state='*')
async def cancel_ad_handler(callback_query: types.CallbackQuery, state: FSMContext):
    await state.finish()
    await callback_query.message.edit_text("Reklama yuborish bekor qilindi 🤖❌")

@dp.callback_query_handler(lambda c: c.data == "confirm_ad", state='*')
async def confirm_ad_handler(callback_query: types.CallbackQuery, state: FSMContext):
    data = await state.get_data()
    ad_type = data.get('ad_type')
    ad_content = data.get('ad_content')
    keyboard = data.get('keyboard')
    send_time = data.get('send_time_value') if data.get('send_time') == 'send_later' else None
    ad_id = len(advertisements) + 1
    advertisement = Advertisement(
        ad_id=ad_id,
        message=ad_content,
        ad_type=ad_type,
        keyboard=keyboard,
        send_time=send_time,
        creator_id=callback_query.from_user.id
    )
    advertisements.append(advertisement)
    await state.finish()
    await callback_query.message.edit_text(f"Reklama #{ad_id} yuborish jadvalga qo'shildi.")
    advertisement.task = asyncio.create_task(advertisement.start())

@dp.callback_query_handler(lambda c: c.data.startswith("pause_ad_"))
async def pause_ad_handler(callback_query: types.CallbackQuery):
    ad_id = int(callback_query.data.split("_")[-1])
    advertisement = next((ad for ad in advertisements if ad.ad_id == ad_id), None)
    if advertisement:
        await advertisement.pause()
        await callback_query.answer(f"Reklama #{ad_id} pauza holatiga o'tkazildi.")
    else:
        await callback_query.answer("Reklama topilmadi.", show_alert=True)

@dp.callback_query_handler(lambda c: c.data.startswith("resume_ad_"))
async def resume_ad_handler(callback_query: types.CallbackQuery):
    ad_id = int(callback_query.data.split("_")[-1])
    advertisement = next((ad for ad in advertisements if ad.ad_id == ad_id), None)
    if advertisement:
        await advertisement.resume()
        await callback_query.answer(f"Reklama #{ad_id} davom ettirildi.")
    else:
        await callback_query.answer("Reklama topilmadi.", show_alert=True)

@dp.callback_query_handler(lambda c: c.data.startswith("stop_ad_"))
async def stop_ad_handler(callback_query: types.CallbackQuery):
    ad_id = int(callback_query.data.split("_")[-1])
    advertisement = next((ad for ad in advertisements if ad.ad_id == ad_id), None)
    if advertisement:
        await advertisement.stop()
        await callback_query.answer(f"Reklama #{ad_id} to'xtatildi.")
    else:
        await callback_query.answer("Reklama topilmadi.", show_alert=True)

def get_cancel_keyboard():
    keyboard = types.InlineKeyboardMarkup()
    keyboard.add(types.InlineKeyboardButton("❌ Bekor qilish", callback_data="cancel_ad"))
    return keyboard

def get_confirm_keyboard():
    keyboard = types.InlineKeyboardMarkup()
    keyboard.add(types.InlineKeyboardButton("✅ Tasdiqlash", callback_data="confirm_ad"))
    keyboard.add(types.InlineKeyboardButton("❌ Bekor qilish", callback_data="cancel_ad"))
    return keyboard

def get_ad_type_keyboard():
    keyboard = types.InlineKeyboardMarkup()
    keyboard.add(types.InlineKeyboardButton("Matnli", callback_data="ad_type_text"))
    keyboard.add(types.InlineKeyboardButton("Forward", callback_data="ad_type_forward"))
    keyboard.add(types.InlineKeyboardButton("Tugmali", callback_data="ad_type_button"))
    keyboard.add(types.InlineKeyboardButton("Har qanday kontent", callback_data="ad_type_any"))
    return keyboard

def get_time_keyboard():
    keyboard = types.InlineKeyboardMarkup()
    keyboard.add(types.InlineKeyboardButton("Hozir", callback_data="send_now"))
    keyboard.add(types.InlineKeyboardButton("Keyingi vaqt", callback_data="send_later"))
    return keyboard


def get_status_keyboard(ad_id, paused=False):
    keyboard = types.InlineKeyboardMarkup()
    if paused:
        keyboard.add(types.InlineKeyboardButton("▶️ Davom ettirish", callback_data=f"resume_ad_{ad_id}"))
    else:
        keyboard.add(types.InlineKeyboardButton("⏸️ Pauza", callback_data=f"pause_ad_{ad_id}"))
    keyboard.add(types.InlineKeyboardButton("⛔️ To'xtatish", callback_data=f"stop_ad_{ad_id}"))
    return keyboard
