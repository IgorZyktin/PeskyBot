# -*- coding: utf-8 -*-
"""Message handlers.
"""
from aiogram import types

from pesky import messages, infra
from pesky.bot.dependencies import dp

LOG = infra.get_logger(__name__)


@dp.message_handler(commands='help')
async def cmd_help(message: types.Message):
    """Show list of known operations."""
    await message.answer(messages.MSG_HELP)
