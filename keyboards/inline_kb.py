from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

kb_inline = InlineKeyboardMarkup(row_width=1)
b1 = InlineKeyboardButton(text='да', callback_data='button1')
b2 = InlineKeyboardButton(text='нет', callback_data='button2')
kb_inline.add(b1, b2)
