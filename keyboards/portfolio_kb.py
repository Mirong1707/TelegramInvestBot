from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove

b1 = KeyboardButton('Рассчитать цену портфеля')
b2 = KeyboardButton('Вернуться')

kb_portfolio = ReplyKeyboardMarkup(resize_keyboard=True)

kb_portfolio.row(b1, b2)
