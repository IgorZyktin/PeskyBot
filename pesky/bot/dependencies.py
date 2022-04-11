# -*- coding: utf-8 -*-
"""Core components of the bot.
"""
from aiogram import Bot, Dispatcher

from pesky.config import config

bot = Bot(token=config.pesky_token)
dp = Dispatcher(bot)
