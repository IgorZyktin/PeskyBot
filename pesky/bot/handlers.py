# -*- coding: utf-8 -*-
"""Message handlers.
"""
from aiogram import types
from aiogram.utils import exceptions

from pesky import messages, infra
from pesky.bot.dependencies import dp

LOG = infra.get_logger(__name__)


@dp.message_handler(commands='start')
async def cmd_start(message: types.Message) -> None:
    """Greet user for the first time."""
    await message.reply(messages.MSG_START)


@dp.message_handler(commands='test1')
async def cmd_test1(message: types.Message):
    await message.reply('Test 1')


@dp.errors_handler(exception=exceptions.BotBlocked)
async def error_bot_blocked(update: types.Update,
                            exception: exceptions.BotBlocked):
    """Handle case when bot is blocked."""
    LOG.warning(f'User blocked me, message=%s, exc=%s', update, exception)
    return True
