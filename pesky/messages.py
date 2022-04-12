# -*- coding: utf-8 -*-
"""Collection of all available messages.
"""
MAX_CATEGORY_NAME = 20

MSG_START = (
    'Привет, {first_name}, я - PeskyBot!\n'
    'Я умею замерять время, которое ты тратишь.'
)

MSG_HELP = (
    'Я знаю следующие команды:\n'
    '/start - показать приветствие\n'
    '/categories - показать известные категории\n'
    '/new_category - создать новую категорию\n'
    '/help - показать справку'
)


MSG_NEW_CATEGORY = (
    'Как ты хочешь назвать новую категорию?'
)

MSG_NEW_CATEGORY_TOO_LONG = (
    'Выбери название покороче'
)

MSG_CATEGORY_CREATED = (
    'Создал категорию {name}'
)
