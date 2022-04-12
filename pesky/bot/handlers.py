# -*- coding: utf-8 -*-
"""Message handlers.
"""
from aiogram import types
from aiogram.utils import exceptions

from pesky import messages, infra
from pesky.bot.dependencies import dp

LOG = infra.get_logger(__name__)


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
