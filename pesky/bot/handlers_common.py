# -*- coding: utf-8 -*-
"""Common handlers.
"""
from aiogram import types
from aiogram.utils import exceptions

from pesky import infra
from pesky.bot.dependencies import dp, user_middleware, database_middleware
from pesky.domain import models
from pesky.storage import operations
from pesky.storage.database.database import Database

LOG = infra.get_logger(__name__)


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


@dp.errors_handler(exception=exceptions.BotBlocked)
async def error_bot_blocked(update: types.Update,
                            exception: exceptions.BotBlocked):
    """Handle case when bot is blocked."""
    LOG.warning(f'User blocked me, message=%s, exc=%s', update, exception)
    return True
