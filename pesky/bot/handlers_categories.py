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
            f'У тебя есть {len(categories)} кат.:\n'
        )

        num = utils.make_num(len(categories))
        numbered = [
            f'{num(i)}. {category}'
            for i, category in enumerate(categories, start=1)
        ]

        output += '\n'.join(numbered)
        output += '\n/new_category - завести новую'
        output += '\n/drop_category - удалить существующую'

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

    output += '\n/new_category - завести ещё одну'

    await database.create_category(user, category)
    await message.answer(output)
    await state.finish()


# =============================================================================


class DropCategoryGroup(StatesGroup):
    """FSM for category deletion."""
    name = State()
    confirm = State()


@dp.message_handler(commands='drop_category')
@user_middleware
@database_middleware
async def cmd_drop_category(
        message: types.Message,
        user: models.User,
        database: Database,
) -> None:
    """Drop existing category."""
    categories = await database.get_categories(user)

    if categories:
        output = (
            f'Выбери категорию, которую хочешь удалить:\n'
        )
        await DropCategoryGroup.name.set()
        keyboard = types.ReplyKeyboardMarkup(
            resize_keyboard=True,
            one_time_keyboard=True,
        )
        keyboard.add(*map(str, categories))
        await message.answer(output, reply_markup=keyboard)

    else:
        output = (
            'У тебя нет ни одной категории.\n'
            '/new_category - завести первую'
        )
        await message.answer(output)


@dp.message_handler(state=DropCategoryGroup.name)
@user_middleware
@database_middleware
async def cmd_drop_category_start(
        message: types.Message,
        state: FSMContext,
        user: models.User,
        database: Database,
) -> None:
    """Get deletion candidate."""
    categories = await database.get_categories(user)
    candidate = message.text

    if candidate not in map(str, categories):
        output = (
            'Это не похоже на имя категории. Введи название из списка.'
        )
        await message.reply(output)
        return

    await DropCategoryGroup.next()
    has_records = await database.category_has_records(user, candidate)
    if has_records:
        await DropCategoryGroup.confirm.set()
        output = (
            'У этой категории есть записи. '
            'Они будут удалены вместе с категорией. '
            'Продолжить?'
        )
        keyboard = types.ReplyKeyboardMarkup(
            resize_keyboard=True,
            one_time_keyboard=True,
        )
        keyboard.add('Да', 'Нет')
        await state.update_data(candidate=candidate)
        await message.answer(output, reply_markup=keyboard)
        return

    await database.drop_category(user, candidate)

    output = (
        f'Категория {candidate} удалена'
    )

    await state.finish()
    await message.answer(output)


@dp.message_handler(state=DropCategoryGroup.confirm)
@user_middleware
@database_middleware
async def cmd_drop_category_confirm(
        message: types.Message,
        state: FSMContext,
        user: models.User,
        database: Database,
) -> None:
    """Confirm deletion of category."""
    data = await state.get_data()
    candidate = data['candidate']

    if message.text == 'Да':
        output = (
            f'Категория {candidate} удалена'
        )
        await state.finish()
        await database.drop_category(user, candidate)
        await message.answer(output)

    elif message.text == 'Нет':
        output = (
            'Не будем удалять категорию'
        )
        await state.finish()
        await message.answer(output)

    else:
        output = (
            'Ну так да или нет?'
        )
        await message.answer(output)
