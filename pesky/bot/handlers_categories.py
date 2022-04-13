# -*- coding: utf-8 -*-
"""Category-related handlers.
"""
from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import StatesGroup, State

from pesky import infra, utils
from pesky.bot.dependencies import (
    dp, user_middleware, database_middleware, DEFAULT_KEYBOARD,
)
from pesky.domain import models
from pesky.storage.database.database import Database

LOG = infra.get_logger(__name__)


@dp.message_handler(commands='Категории')
async def cmd_categories(message: types.Message) -> None:
    """Entry point for categories."""
    keyboard = types.ReplyKeyboardMarkup(
        resize_keyboard=True,
        one_time_keyboard=True,
    )

    keyboard.add(
        '/Показать_категории',
        '/Новая_категория',
        '/Переименовать_категорию',
        '/Удалить_категорию',
        '/Отмена',
    )

    output = (
        'Здесь можно настроить категории.'
    )

    await message.answer(output, reply_markup=keyboard)


# =============================================================================


@dp.message_handler(commands='Показать_категории')
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

    else:
        output = (
            'У тебя нет ни одной категории.'
        )

    await message.answer(output, reply_markup=DEFAULT_KEYBOARD)


# =============================================================================


class CreateCategoryGroup(StatesGroup):
    """FSM for category creation."""
    name = State()


MAX_CATEGORY_NAME_LENGTH = 20


@dp.message_handler(commands='Новая_категория')
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
        output += ' (немного изменил).'

    await database.create_category(user, category)
    await message.answer(output, reply_markup=DEFAULT_KEYBOARD)
    await state.finish()


# =============================================================================


class DropCategoryGroup(StatesGroup):
    """FSM for category deletion."""
    name = State()
    confirm = State()


@dp.message_handler(commands='Удалить_категорию')
@user_middleware
@database_middleware
async def cmd_drop_category(
        message: types.Message,
        user: models.User,
        database: Database,
) -> None:
    """Drop existing category."""
    categories = await database.get_categories(user)
    keyboard = types.ReplyKeyboardMarkup(
        resize_keyboard=True,
        one_time_keyboard=True,
    )

    if categories:
        output = (
            f'Выбери категорию, которую хочешь удалить:'
        )
        await DropCategoryGroup.name.set()
        keyboard.add(*map(str, categories))
        await message.answer(output, reply_markup=keyboard)

    else:
        output = (
            'У тебя нет ни одной категории.'
        )

        await message.answer(output, reply_markup=DEFAULT_KEYBOARD)


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
    await message.answer(output, reply_markup=DEFAULT_KEYBOARD)


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
        await message.answer(output, reply_markup=DEFAULT_KEYBOARD)

    elif message.text == 'Нет':
        output = (
            'Не будем удалять категорию'
        )
        await state.finish()
        await message.answer(output, reply_markup=DEFAULT_KEYBOARD)

    else:
        output = (
            'Ну так да или нет?'
        )
        await message.answer(output)


# =============================================================================


class RenameCategoryGroup(StatesGroup):
    """FSM for category rename."""
    name = State()
    new_name = State()
    confirm = State()


@dp.message_handler(commands='Переименовать_категорию')
@user_middleware
@database_middleware
async def cmd_rename_category(
        message: types.Message,
        user: models.User,
        database: Database,
) -> None:
    """Rename existing category."""
    categories = await database.get_categories(user)
    keyboard = types.ReplyKeyboardMarkup(
        resize_keyboard=True,
        one_time_keyboard=True,
    )

    if categories:
        output = (
            f'Выбери категорию, которую хочешь переименовать:'
        )
        await RenameCategoryGroup.name.set()
        keyboard.add(*map(str, categories))
        await message.answer(output, reply_markup=keyboard)

    else:
        output = (
            'У тебя нет ни одной категории.'
        )

        await message.answer(output, reply_markup=DEFAULT_KEYBOARD)


@dp.message_handler(state=RenameCategoryGroup.name)
@user_middleware
@database_middleware
async def cmd_rename_category_start(
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

    await RenameCategoryGroup.new_name.set()

    output = (
        'Введи новое имя для категории'
    )
    await state.update_data(candidate=candidate)
    await message.answer(output)


@dp.message_handler(
    lambda message: len(message.text) > MAX_CATEGORY_NAME_LENGTH,
    state=RenameCategoryGroup.new_name,
)
async def cmd_rename_category_name_too_long(message: types.Message):
    """Category name is too long."""
    output = (
        f'Выбери название покороче (максимум {MAX_CATEGORY_NAME_LENGTH} симв.)'
    )
    return await message.reply(output)


@dp.message_handler(state=RenameCategoryGroup.new_name)
async def cmd_rename_category_new_name(
        message: types.Message,
        state: FSMContext,
) -> None:
    """Enter new name for category."""
    data = await state.get_data()
    candidate = data['candidate']
    new_name = utils.sanitize_user_input(message.text)
    await state.update_data(new_name=new_name)

    keyboard = types.ReplyKeyboardMarkup(
        resize_keyboard=True,
        one_time_keyboard=True,
    )
    keyboard.add('Да', 'Нет')
    output = (
        f"Переименовываем {candidate} в {new_name}?"
    )
    await RenameCategoryGroup.confirm.set()
    await message.answer(output, reply_markup=keyboard)


@dp.message_handler(state=RenameCategoryGroup.confirm)
@user_middleware
@database_middleware
async def cmd_rename_category_confirm(
        message: types.Message,
        state: FSMContext,
        user: models.User,
        database: Database,
) -> None:
    """Confirm deletion of category."""
    data = await state.get_data()
    candidate = data['candidate']
    new_name = data['new_name']

    if message.text == 'Да':
        output = (
            f'Переименовал {candidate} в {new_name}'
        )
        await state.finish()
        await database.rename_category(user, candidate, new_name)
        await message.answer(output, reply_markup=DEFAULT_KEYBOARD)

    else:
        output = (
            'Выбери другое название'
        )
        await RenameCategoryGroup.new_name.set()
        await message.answer(output)
