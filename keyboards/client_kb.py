from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove

b1 = KeyboardButton('/Прочее')
b2 = KeyboardButton('/Узнать_цену_на_акцию')
b3 = KeyboardButton('/Мой_портфель')

kb_client = ReplyKeyboardMarkup(resize_keyboard=True)

kb_client.row(b1, b2, b3)
