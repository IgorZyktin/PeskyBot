# -*- coding: utf-8 -*-
"""Message handlers.
"""
from aiogram import types
from aiogram.utils import exceptions

from pesky import messages, infra
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
    await operations.maybe_register_user(database, user)
    await message.answer(messages.MSG_START.format(
        first_name=user.first_name,
    ))


@dp.message_handler(commands='help')
async def cmd_help(message: types.Message):
    """Show list of known operations."""
    await message.answer(messages.MSG_HELP)


@dp.errors_handler(exception=exceptions.BotBlocked)
async def error_bot_blocked(update: types.Update,
                            exception: exceptions.BotBlocked):
    """Handle case when bot is blocked."""
    LOG.warning(f'User blocked me, message=%s, exc=%s', update, exception)
    return True
