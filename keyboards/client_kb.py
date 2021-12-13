from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove

b1 = KeyboardButton('🛠Инструменты')
b2 = KeyboardButton('💵Узнать цену на акцию')
b3 = KeyboardButton('💰Мой портфель')

kb_client = ReplyKeyboardMarkup(resize_keyboard=True)

kb_client.row(b1, b2, b3)
