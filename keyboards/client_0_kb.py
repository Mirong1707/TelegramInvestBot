from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove

b1 = KeyboardButton('/Вернуться')
b2 = KeyboardButton('/Список_акций')
b3 = KeyboardButton('/Топ_трейдеров')
b4 = KeyboardButton('/Текущие_результаты_соревнования')

kb_client_0 = ReplyKeyboardMarkup(resize_keyboard=True)

kb_client_0.row(b1, b2, b3)
kb_client_0.row(b4)
