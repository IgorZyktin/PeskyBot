# -*- coding: utf-8 -*-
"""Core components of the bot.
"""
import functools
from typing import Coroutine, Callable

from aiogram import Bot, Dispatcher, types

from pesky.config import config
from pesky.domain import models

bot = Bot(token=config.pesky_token)
dp = Dispatcher(bot)


def user_middleware(
        func: Callable[..., Coroutine],
) -> Callable[..., Coroutine]:
    """Add user as an argument."""

    @functools.wraps(func)
    async def wrapper(message: types.Message):
        """Wrapper."""
        user = models.User(
            id=message.from_user.id,
            first_name=message.from_user.first_name,
        )
        await func(user, message)

    return wrapper
