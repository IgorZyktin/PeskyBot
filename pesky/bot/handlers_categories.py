# -*- coding: utf-8 -*-
"""Category-related handlers.
"""
from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import StatesGroup, State

from pesky import infra, utils
from pesky.bot.dependencies import dp, user_middleware, database_middleware
from pesky.domain import models
from pesky.storage.database.database import Database

LOG = infra.get_logger(__name__)


@dp.message_handler(commands='list_categories')
@user_middleware
@database_middleware
async def cmd_list_categories(
        message: types.Message,
        user: models.User,
        database: Database,
) -> None:
    """Show list of known categories."""
    categories = await database.get_categories(user)

    if categories:
        output = (
            f'У тебя есть {len(categories)} кат.:'
        )

        num = utils.make_num(len(categories))
        numbered = [
            f'{num(i)}. {category}'
            for i, category in enumerate(categories, start=1)
        ]

        output += '\n' + '\n'.join(numbered)
        output += '\n/new_category - завести новую'

    else:
        output = (
            'У тебя нет ни одной категории.\n'
            '/new_category - завести первую'
        )

    await message.answer(output)


# =============================================================================


class CreateCategoryGroup(StatesGroup):
    """FSM for category creation."""
    name = State()


MAX_CATEGORY_NAME_LENGTH = 20


@dp.message_handler(commands='new_category')
async def cmd_new_category(
        message: types.Message,
) -> None:
    """Create new category."""
    await CreateCategoryGroup.name.set()

    output = (
        'Как ты хочешь назвать новую категорию?'
    )

    await message.answer(output)


@dp.message_handler(
    lambda message: len(message.text) > MAX_CATEGORY_NAME_LENGTH,
    state=CreateCategoryGroup.name,
)
async def cmd_new_category_name_too_long(message: types.Message):
    """Category name is too long."""
    output = (
        f'Выбери название покороче (максимум {MAX_CATEGORY_NAME_LENGTH} симв.)'
    )
    return await message.reply(output)


@dp.message_handler(
    lambda message: len(message.text) <= MAX_CATEGORY_NAME_LENGTH,
    state=CreateCategoryGroup.name,
)
@user_middleware
@database_middleware
async def cmd_new_category_name_save(
        message: types.Message,
        state: FSMContext,
        user: models.User,
        database: Database,
) -> None:
    """Save new category to the database."""
    category = models.Category(
        id=-1,
        name=utils.sanitize_user_input(message.text),
    )

    output = (
        f'Я сохранил для тебя категорию {category.name}'
    )

    if category.name != message.text:
        LOG.warning('User %s entered strange category name: %r',
                    user.verbose_name, message.text)
        output += '\n. Я немного изменил название.'

    await database.create_category(user, category)
    await message.answer(output)
    await state.finish()
