# -*- coding: utf-8 -*-
"""Message handlers.
"""
from aiogram import types

from pesky.bot.dependencies import dp


@dp.message_handler(commands='test1')
async def cmd_test1(message: types.Message):
    await message.reply('Test 1')
