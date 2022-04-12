# -*- coding: utf-8 -*-
"""Common handlers.
"""
from aiogram import types

from pesky.bot.dependencies import dp, user_middleware, database_middleware
from pesky.domain import models
from pesky.storage import operations
from pesky.storage.database.database import Database


@dp.message_handler(commands='start')
@user_middleware
@database_middleware
async def cmd_start(
        message: types.Message,
        user: models.User,
        database: Database,
) -> None:
    """Greet user for the first time."""
    registered = await operations.maybe_register_user(database, user)

    output = (
        f'Привет, {user.first_name}, я - PeskyBot!\n'
        'Я умею замерять время, которое ты тратишь.'
    )

    if registered:
        output += '\nРад знакомству!'

    await message.answer(output)
