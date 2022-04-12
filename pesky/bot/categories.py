# -*- coding: utf-8 -*-
"""Specific category handlers.
"""
from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import StatesGroup, State

from pesky import messages, infra
from pesky.bot.dependencies import dp, user_middleware, database_middleware
from pesky.domain import models
from pesky.storage.database.database import Database

LOG = infra.get_logger(__name__)


class CategoryForm(StatesGroup):
    """Category form."""
    name = State()


@dp.message_handler(commands='new_category')
async def cmd_new_category(
        message: types.Message,
) -> None:
    """Create new category."""
    await CategoryForm.name.set()
    await message.answer(messages.MSG_NEW_CATEGORY)


@dp.message_handler(
    lambda message: len(message.text) > messages.MAX_CATEGORY_NAME,
    state=CategoryForm.name,
)
async def process_name_invalid(message: types.Message):
    """Category name is invalid."""
    return await message.reply(messages.MSG_NEW_CATEGORY_TOO_LONG)


@dp.message_handler(
    lambda message: len(message.text) <= messages.MAX_CATEGORY_NAME,
    state=CategoryForm.name,
)
@user_middleware
@database_middleware
async def process_name(
        message: types.Message,
        state: FSMContext,
        user: models.User,
        database: Database,
) -> None:
    """Category name is valid."""
    async with state.proxy() as data:
        data['name'] = message.text

    category = models.Category(
        id=-1,
        name=data['name'],
    )

    await database.create_category(user, category)
    await message.reply(messages.MSG_CATEGORY_CREATED.format(
        name=category.name,
    ))
    await state.finish()
