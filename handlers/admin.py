from aiogram import types, Dispatcher
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.dispatcher.filters import Text
from create_bot import bot
from data_base import sqlite_db
from keyboards import kb_admin
from keyboards import kb_inline
from data_base import sqlite_db

ID = 443431624
survey = {}
competitors = []
competitors_id = []


class FSMAdmin(StatesGroup):
    photo = State()
    name = State()
    description = State()
    price = State()


# @dp.message_handler(state="*", commands='отмена')
# @dp.message_handler(Text(equals='отмена'), ignore_case=True), state="*")
async def cancel_handler(message: types.Message, state: FSMContext):
    if message.from_user.id != ID:
        return
    current_state = await state.get_state()
    if current_state is None:
        return
    await state.finish()
    await message.reply('OK')


# @dp.callback_query_handler(func=lambda c: c.data == 'button1')
async def process_callback_button1(callback_query: types.CallbackQuery):
    global survey
    global competitors
    global competitors_id
    await survey[callback_query.from_user.username].delete()
    await bot.answer_callback_query(callback_query.id)
    await sqlite_db.sql_user_prepare_competition(callback_query.from_user.username)
    await bot.send_message(callback_query.from_user.id, 'Вы стали участником')
    competitors.append(callback_query.from_user.username)
    competitors_id.append(callback_query.from_user.id)


# @dp.callback_query_handler(func=lambda c: c.data == 'button2')
async def process_callback_button2(callback_query: types.CallbackQuery):
    global survey
    await survey[callback_query.from_user.username].delete()
    await bot.answer_callback_query(callback_query.id)
    await bot.send_message(callback_query.from_user.id, 'Вы отказались от участия')


async def test_competition(message: types.Message):
    # if message.from_user.id != ID:
    #    return
    global survey
    survey.clear()
    competitors.clear()
    competitors_id.clear()
    ids = await sqlite_db.sql_users_info()
    for user in ids:
        ms1 = await bot.send_message(user[1], "Начинается новое соревнование. Принять участие?", reply_markup=kb_inline)
        survey.update({user[0]: ms1})


async def start_competition(message: types.Message):
    # if message.from_user.id != ID:
    #    return
    users = await sqlite_db.sql_users()
    global survey
    global competitors
    global competitors_id
    for info in await sqlite_db.sql_users_info():
        await sqlite_db.sql_create_user_table_0(info[0], info[1])
    for user in users:
        try:
            await survey[user].delete()
        except:
            pass
    survey.clear()
    ms = 'Набор участников закончен. Все портфели участников обнулены. Удачных голодных игр!\n\n' \
         'Список участников:\n'
    for user in competitors:
        ms += user + '\n'
    for m_id in competitors_id:
        await bot.send_message(m_id, ms)


async def end_competition(message: types.Message):
    # if message.from_user.id != ID:
    #    return
    users = await sqlite_db.sql_users()
    global survey
    global competitors
    global competitors_id
    ms = 'Соревнование закончено. Всем спасибо за участие\n\n' \
         'Результаты:\n'
    for um in competitors:
        await sqlite_db.sql_count_user_table_without_message(um)
    ms += await sqlite_db.sql_top_competitors(competitors)
    for m_id in competitors_id:
        await bot.send_message(m_id, ms)
    survey.clear()
    competitors.clear()
    competitors_id.clear()


def register_handlers_admin(dp: Dispatcher):
    dp.register_message_handler(test_competition, text=['Регистрация участников'], state='*')
    dp.register_message_handler(start_competition, text=['Начать соревнование'], state='*')
    dp.register_message_handler(end_competition, text=['Закончить соревнование'], state='*')
    dp.register_callback_query_handler(process_callback_button1, lambda c: c.data == 'button1', state='*')
    dp.register_callback_query_handler(process_callback_button2, lambda c: c.data == 'button2', state='*')
    # dp.register_message_handler(cm_start, commands=['Загрузить'])
    # dp.register_message_handler(load_photo, content_types=['photo'], state=FSMAdmin.photo)
    # dp.register_message_handler(load_name, state=FSMAdmin.name)
    # dp.register_message_handler(load_description, state=FSMAdmin.description)
    # dp.register_message_handler(load_price, state=FSMAdmin.price)
    # dp.register_message_handler(cancel_handler, state="*", commands='отмена')
    # dp.register_message_handler(cancel_handler, Text(equals='отмена', ignore_case=True), state="*")
    # dp.register_message_handler(make_changes_command, commands=['moderator'], is_chat_admin=True)
