# -*- coding: utf-8 -*-
"""Core components of the bot.
"""
import functools
from typing import Coroutine, Callable

from aiogram import Bot, Dispatcher, types

from pesky.config import config
from pesky.domain import models
from pesky.storage.database.database import Database

bot = Bot(token=config.pesky_token)
dp = Dispatcher(bot)
database = Database()


def user_middleware(
        func: Callable[..., Coroutine],
) -> Callable[..., Coroutine]:
    """Add user as an argument."""

    @functools.wraps(func)
    async def wrapper(message: types.Message, *args, **kwargs):
        """Wrapper."""
        user = models.User(
            id=message.from_user.id,
            first_name=message.from_user.first_name,
        )
        await func(message, user, *args, **kwargs)

    return wrapper


def database_middleware(
        func: Callable[..., Coroutine],
) -> Callable[..., Coroutine]:
    """Add database as an argument."""

    @functools.wraps(func)
    async def wrapper(message: types.Message, *args, **kwargs):
        """Wrapper."""
        await func(message, *args, database, **kwargs)

    return wrapper
