from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove

b1 = KeyboardButton('/Купить')
b2 = KeyboardButton('/Продать')
b3 = KeyboardButton('/Вернуться')

kb_buy_stock = ReplyKeyboardMarkup(resize_keyboard=True)

kb_buy_stock.row(b1, b2, b3)
