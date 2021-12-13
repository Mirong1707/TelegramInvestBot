from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove

b1 = KeyboardButton('Вернуться')
b2 = KeyboardButton('📊Список акций')
b3 = KeyboardButton('🏆Топ трейдеров')
b4 = KeyboardButton('🏆Текущие результаты соревнования')
b5 = KeyboardButton('Регистрация участников')
b6 = KeyboardButton('Начать соревнование')
b7 = KeyboardButton('Закончить соревнование')

kb_client_0 = ReplyKeyboardMarkup(resize_keyboard=True)

kb_client_0.row(b1, b2, b3)
kb_client_0.row(b4)
kb_client_0.row(b5)
kb_client_0.row(b6, b7)
