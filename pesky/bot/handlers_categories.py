# -*- coding: utf-8 -*-
"""Category-related handlers.
"""
from aiogram import types

from pesky import infra, utils
from pesky.bot.dependencies import dp, user_middleware, database_middleware
from pesky.domain import models
from pesky.storage.database.database import Database

LOG = infra.get_logger(__name__)


@dp.message_handler(commands='list_categories')
@user_middleware
@database_middleware
async def cmd_list_categories(
        message: types.Message,
        user: models.User,
        database: Database,
) -> None:
    """Show list of known categories."""
    categories = await database.get_categories(user)

    if categories:
        output = (
            f'У тебя есть {len(categories)} категорий:'
        )

        num = utils.make_num(len(categories))
        numbered = [
            f'{num(i)}. {category}'
            for i, category in enumerate(categories, start=1)
        ]

        output += '\n' + '\n'.join(numbered)
        output += '\n/new_category - завести первую'

    else:
        output = (
            'У тебя нет ни одной категории.\n'
            '/new_category - завести первую'
        )

    await message.answer(output)
