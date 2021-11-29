from aiogram import types, Dispatcher
from create_bot import bot
from keyboards import kb_client
from keyboards import kb_client_0
from keyboards import kb_list
from aiogram.types import ReplyKeyboardRemove
from data_base import sqlite_db
from aiogram.dispatcher.filters.state import State, StatesGroup
from handlers.admin import competitors


class FSMClient(StatesGroup):
    load_stock_name = State()
    trading_stock = State()
    buy_stock_state = State()
    sell_stock_state = State()


class FSMAnother(StatesGroup):
    main = State()


class FSMClient_portfolio(StatesGroup):
    count_portfolio = State()


class FSMClient_stocks_list(StatesGroup):
    list = State()


# @dp.message_handler(commands=['start', 'help'])
async def command_start(message: types.Message):
    try:
        await sqlite_db.sql_create_user_table(message)
        await bot.send_message(message.from_user.id, 'Удачной торговли', reply_markup=kb_client)
        await message.delete()
    except:
        await message.reply('Общение с ботом через ЛС, напишите ему:\nhttps://t.me/Pizza_SheefBot')


# @dp.message_handler(commands=['Список_акций'])
async def tinkoff_prices(message: types.Message, state: FSMAnother.main):
    global ind
    ind = 0
    await bot.send_message(message.from_user.id, 'Список акций', reply_markup=kb_list)
    await sqlite_db.sql_read(message, ind)
    ind += 1
    await state.finish()
    await FSMClient_stocks_list.list.set()


# @dp.message_handler(commands=['Вернуться'])
async def tinkoff_another_back(message: types.Message, state: FSMAnother.main):
    await bot.send_message(message.from_user.id, 'Готово', reply_markup=kb_client)
    await state.finish()


# @dp.message_handler(commands=['Топ_трейдеров'])
async def tinkoff_another_top_traders(message: types.Message, state: FSMAnother.main):
    await sqlite_db.sql_top_traders(message)
    await state.finish()


# @dp.message_handler(commands=['Текущие_результаты_соревнования'])
async def tinkoff_another_top_competitors(message: types.Message, state: FSMAnother.main):
    if len(competitors) == 0:
        res = "На данный момент соревнование не идёт"
        await bot.send_message(message.from_user.id, res, reply_markup=kb_client)
        await state.finish()
        return
    res = "Текущие результаты соревнования\n\n"
    res += await sqlite_db.sql_top_competitors(competitors)
    await bot.send_message(message.from_user.id, res, reply_markup=kb_client)
    await state.finish()


# @dp.message_handler(commands=['Ещё'])
async def tinkoff_prices_0(message: types.Message, state: FSMClient_stocks_list.list):
    global ind
    await sqlite_db.sql_read(message, ind)
    ind += 1


# @dp.message_handler(commands=['Вернуться'])
async def tinkoff_prices_1(message: types.Message, state: FSMClient_stocks_list.list):
    await bot.send_message(message.from_user.id, 'Готово', reply_markup=kb_client)
    await state.finish()


# @dp.message_handler(commands=['/Прочее'])
async def tinkoff_another(message: types.Message):
    await FSMClient.load_stock_name.set()
    await message.reply('Выберите команду', reply_markup=kb_client_0)
    await FSMAnother.main.set()


# @dp.message_handler(commands=['/Узнать_цену_на_акцию'])
async def tinkoff_find_name(message: types.Message):
    await FSMClient.load_stock_name.set()
    await message.reply('Напишите название акции', reply_markup=ReplyKeyboardRemove())


# @dp.message_handler(state=FSMClient.load_stock_name)
async def load_stock_name(message: types.Message, state: FSMClient.load_stock_name):
    name = await sqlite_db.sql_find_real_name(message.text)
    await sqlite_db.sql_update(name)
    res = await sqlite_db.sql_read_one(message, name)
    if not res:
        await state.finish()
        return
    await FSMClient.trading_stock.set()


# @dp.message_handler(state=FSMClient.trading_stock)
async def buy_stock(message: types.Message, state: FSMClient.trading_stock):
    await bot.send_message(message.from_user.id, "Напишите количество акций, которые хотите купить\n\n"
                                                 "Можно купить до " + str(
        await sqlite_db.sql_mx_buy(message)) + " акций",
                           reply_markup=ReplyKeyboardRemove())
    await FSMClient.buy_stock_state.set()


# @dp.message_handler(state=FSMClient.buy_stock_state)
async def buy_stock_1(message: types.Message, state: FSMClient.buy_stock_state):
    if not message.text.isdigit():
        await bot.send_message(message.from_user.id, "Введите число")
        return
    if not await sqlite_db.sql_buy_stock(message):
        return
    await state.finish()


# @dp.message_handler(state=FSMClient.trading_stock)
async def sell_stock(message: types.Message, state: FSMClient.trading_stock):
    await bot.send_message(message.from_user.id, "Напишите количество акций, которые хотите продать",
                           reply_markup=ReplyKeyboardRemove())
    await FSMClient.sell_stock_state.set()


# @dp.message_handler(state=FSMClient.sell_stock_state)
async def sell_stock_1(message: types.Message, state: FSMClient.sell_stock_state):
    if not message.text.isdigit():
        await bot.send_message(message.from_user.id, "Введите число")
        return
    if not await sqlite_db.sql_sell_stock(message):
        return
    await state.finish()


# @dp.message_handler(state=FSMClient.trading_stock)
async def stock_stop_trading(message: types.Message, state: FSMClient.trading_stock):
    await bot.send_message(message.from_user.id, "Стоп", reply_markup=kb_client)
    await state.finish()


# @dp.message_handler(commands=['/Мой_портфель'])
async def tinkoff_portfolio(message: types.Message):
    await FSMClient_portfolio.count_portfolio.set()
    await sqlite_db.sql_print_user_table(message)


# @dp.message_handler(commands=['/Рассчитать_цену_портфеля'])
async def tinkoff_portfolio_count(message: types.Message, state: FSMClient_portfolio.count_portfolio):
    await sqlite_db.sql_count_user_table(message)
    await state.finish()


# @dp.message_handler(commands=['/Вернуться'])
async def tinkoff_portfolio_break(message: types.Message, state: FSMClient_portfolio.count_portfolio):
    await bot.send_message(message.from_user.id, "Готово", reply_markup=kb_client)
    await state.finish()


def register_handlers_client(dp: Dispatcher):
    dp.register_message_handler(command_start, commands=['start', 'help'])
    dp.register_message_handler(tinkoff_prices, commands=['Список_акций'], state=FSMAnother.main)
    dp.register_message_handler(tinkoff_another_top_traders, commands=['Топ_трейдеров'], state=FSMAnother.main)
    dp.register_message_handler(tinkoff_another_top_competitors, commands=['Текущие_результаты_соревнования'],
                                state=FSMAnother.main)
    dp.register_message_handler(tinkoff_another_back, commands=['Вернуться'], state=FSMAnother.main)
    dp.register_message_handler(tinkoff_prices_0, commands=['Ещё'], state=FSMClient_stocks_list.list)
    dp.register_message_handler(tinkoff_prices_1, commands=['Вернуться'], state=FSMClient_stocks_list.list)
    dp.register_message_handler(tinkoff_find_name, commands=['Узнать_цену_на_акцию'])
    dp.register_message_handler(tinkoff_another, commands=['Прочее'])
    dp.register_message_handler(load_stock_name, state=FSMClient.load_stock_name)
    dp.register_message_handler(buy_stock, commands=['Купить'], state=FSMClient.trading_stock)
    dp.register_message_handler(buy_stock_1, state=FSMClient.buy_stock_state)
    dp.register_message_handler(sell_stock, commands=['Продать'], state=FSMClient.trading_stock)
    dp.register_message_handler(sell_stock_1, state=FSMClient.sell_stock_state)
    dp.register_message_handler(stock_stop_trading, commands=['Вернуться'], state=FSMClient.trading_stock)
    dp.register_message_handler(tinkoff_portfolio, commands=['Мой_портфель'])
    dp.register_message_handler(tinkoff_portfolio_count, commands=['Рассчитать_цену_портфеля'],
                                state=FSMClient_portfolio.count_portfolio)
    dp.register_message_handler(tinkoff_portfolio_break, commands=['Вернуться'],
                                state=FSMClient_portfolio.count_portfolio)
