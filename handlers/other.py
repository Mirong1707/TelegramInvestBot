from aiogram import types, Dispatcher


# @dp.message_handler()
async def echo_send(message: types.Message):
    if message.text == 'Привет':
        await message.answer('И тебе привет!')


def register_handlers_other(dp: Dispatcher):
    dp.register_message_handler(echo_send)
