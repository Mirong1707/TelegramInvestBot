from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove

b1 = KeyboardButton('Ещё')
b2 = KeyboardButton('Вернуться')

kb_list = ReplyKeyboardMarkup(resize_keyboard=True)

kb_list.row(b1, b2)
