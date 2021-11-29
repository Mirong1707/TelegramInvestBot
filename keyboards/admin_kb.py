from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove

b1 = KeyboardButton('/Загрузить')
b2 = KeyboardButton('/Удалить')

kb_admin = ReplyKeyboardMarkup(resize_keyboard=True).row(b1, b2)

