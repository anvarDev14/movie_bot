from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.handler import CancelHandler
from aiogram.types import CallbackQuery

from data.config import ADMINS
from keyboards.inline.admin import keyboard, ad_menu
from loader import dp, kino_db, user_db, bot
from states.states import KinoAddState, DeleteState, EditCap

# Hafta va oylik filmlarni olish
hafta_movies = kino_db.get_movies_hafta()
oy_movies = kino_db.get_movies_oy()


@dp.message_handler(commands='admin')
async def user_count(message: types.Message):
    if str(message.from_user.id) in ADMINS:
        await message.answer(text='.', reply_markup=keyboard)
    else:
        await message.answer("Siz admin emassiz.")

@dp.callback_query_handler(text='today')
async def bugun_stat(call: CallbackQuery):
    bugun = kino_db.get_movies_bugun()
    if bugun:
        for movie in bugun:
            await call.message.answer(movie["name"] + "\n")
    else:
        await call.message.answer("Bugungi kinolar yo'q")

@dp.callback_query_handler(text="week")
async def week_stat(call: CallbackQuery):
    if hafta_movies:
        for movie in hafta_movies:
            await call.message.answer(movie["name"])
    else:
        await call.message.answer("Bu haftada kinolar yo'q")

@dp.callback_query_handler(text='month')
async def month_stat(call: CallbackQuery):
    if oy_movies:
        for movie in oy_movies:
            await call.message.answer(movie["name"])
    else:
        await call.message.answer("Bu oyda kinolar yo'q")

@dp.callback_query_handler(text='stats')
async def statistika(call: CallbackQuery):
    await call.message.delete()
    count = user_db.count_users()
    await call.message.answer(f"Bazada <b>{count}</b> ta foydalanuvchi bor")


@dp.callback_query_handler(text='ad')
async def reklama(call: CallbackQuery):
    if str(call.message.from_user.id) in ADMINS:
        await call.message.answer("Reklama yuborilmaydi, adminlar uchun.")
        return

    await call.message.delete()
    await call.message.answer("Reklama videosi yoki rasmini yoziv bilan yuboring.")

@dp.message_handler(content_types=['photo', 'video', 'text'])
async def handle_ad_message(ad_message: types.Message):
    global stop  # Use the global stop flag
    not_sent = 0
    sent = 0
    admins = 0
    text = f"Xabar yuborish\nYuborilgan: {sent}\nYuborilmagan: {not_sent}\nUmumiy: 0/{user_db.count_users()}\n\nStatus: Boshlanmoqda"
    status_message = await ad_message.answer(text, reply_markup=ad_menu)
    users = user_db.select_all_user_ids()

    for user_id in users:
        if str(user_id) in ADMINS:
            not_sent += 1
            admins += 1
            continue

        try:
            await ad_message.forward(user_id)
            sent += 1
        except:
            not_sent += 1

        text = f"Xabar yuborish\nYuborilgan: {sent}\nYuborilmagan: {not_sent} ({admins}ta Admin)\nUmumiy: {sent + not_sent}/{user_db.count_users()}\nStatus: Davom etmoqda"
        await bot.edit_message_text(text, chat_id=ad_message.chat.id, message_id=status_message.message_id, reply_markup=ad_menu)

        if stop:
            stop = False
            raise CancelHandler

    text = f"Xabar yuborish\nYuborilgan: {sent}\nYuborilmagan: {not_sent} ({admins}ta Admin)\nUmumiy: {user_db.count_users()}/{user_db.count_users()}\nStatus: Tugatildi"
    await bot.edit_message_text(text, chat_id=ad_message.chat.id, message_id=status_message.message_id)

@dp.callback_query_handler(text='pause_ad')
async def stop_ad(call: CallbackQuery):
    global stop
    stop = True
    await call.message.answer("To'xtatildi.")
    raise CancelHandler
@dp.callback_query_handler(text='admin_menu_ad')
async def back_from_ad(call:CallbackQuery):
    global stop
    stop = True
    await call.message.delete()
    await call.message.answer("To'xtatildi",reply_markup=keyboard)
    raise CancelHandler

@dp.message_handler(content_types=['photo', 'video', 'text'])
async def handle_ad_message(ad_message: types.Message):
        not_sent = 0
        sent = 0
        for user_id in user_db.select_all_user_ids():
            try:
                await ad_message.forward(user_id)
                sent += 1
            except Exception as e:
                print(f"ERR: {e}")
                not_sent += 1
        await ad_message.answer(f"Reklama {sent} ta odamga yuborildi, {not_sent} ta odamga yuborilmadi")

@dp.callback_query_handler(text='count_movie')
async def counting(call: CallbackQuery):
    counter = kino_db.count_kino()
    if counter:
        await call.message.delete()
        await call.message.answer(f"Bazada <b>{counter}</b> ta kino bor")
    else:
        await call.message.delete()
        await call.message.answer("Bazada kino yo'q")

@dp.message_handler(commands='add_movie')
async def kino_add_func(message: types.Message):
    if str(message.from_user.id) in ADMINS:
        await KinoAddState.kino_add.set()
        await message.reply("Kino va kinoning nomini yuboring")
    else:
        await message.answer("Siz admin emassiz")

@dp.message_handler(state=KinoAddState.kino_add, content_types=types.ContentType.VIDEO)
async def message_kino_added(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['file_id'] = message.video.file_id
        data['caption'] = message.caption
    await KinoAddState.kino_kod.set()
    await message.answer("Kino uchun kod yuboring")

@dp.message_handler(state=KinoAddState.kino_kod, content_types=types.ContentType.TEXT)
async def message_kino_cod_handler(message: types.Message, state: FSMContext):
    try:
        post_id = int(message.text)
        async with state.proxy() as data:
            data['post_id'] = post_id
            kino_db.add_movie(post_id, file_id=data['file_id'], name="Kino nomi", caption=data['caption'])
        await message.answer(f"Kino muvaffaqqiyatli qo'shildi\nKino codi {post_id}")
        await state.finish()
    except ValueError:
        await message.answer("Iltimos, kino kodi sifatida faqat raqam kiriting")

@dp.message_handler(commands='delete_movie')
async def delete_movie_handler(message: types.Message):
    if str(message.from_user.id) in ADMINS:
        await message.answer("Post IDni yuboring")
        await DeleteState.kutish.set()
    else:
        await message.answer("Siz admin emassiz")

@dp.message_handler(state=DeleteState.kutish)
async def wait_for_delete_id(message: types.Message, state: FSMContext):
    try:
        post_id = int(message.text)
    except ValueError:
        await message.reply("Iltimos, to'g'ri post ID kiriting.")
        await state.finish()
        return
    if kino_db.get_movie_by_post_id(post_id):
        kino_db.delete_movie(post_id)
        await message.reply(f"{post_id} koddagi kino muvaffaqqiyatli o'chirildi")
    else:
        await message.reply("Kino topilmadi. O'chirish uchun berilgan post ID mavjud emas.")
    await state.finish()

@dp.message_handler(commands='update')
async def update_cap(message: types.Message):
    await message.answer("Post IDni kiriting")
    await EditCap.ID.set()

@dp.message_handler(state=EditCap.ID)
async def getid(message: types.Message, state: FSMContext):
    try:
        post_id = int(message.text)
        await state.update_data({'pst_id': post_id})
        await message.answer("Captionni kiriting")
        await EditCap.caption.set()
    except ValueError:
        await message.reply("Iltimos, to'g'ri post ID kiriting.")
        await state.finish()

@dp.message_handler(state=EditCap.caption)
async def caption(message: types.Message, state: FSMContext):
    datao = await state.get_data()
    caption1 = message.text
    if kino_db.get_movie_by_post_id(datao['pst_id']):
        kino_db.update_kino_caption(caption1, datao['pst_id'])
        await message.answer("Caption muvaffaqiyatli o'zgartirildi")
    else:
        await message.answer("Bu kino mavjud emas")
    await state.finish()
