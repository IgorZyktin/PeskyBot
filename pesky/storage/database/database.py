# -*- coding: utf-8 -*-
"""Application database.
"""
import json

from pesky.domain import models
from pesky.storage.abstract_database import AbstractDatabase


class Database(AbstractDatabase):
    """Application database."""

    # FIXME - temporary implementation

    @staticmethod
    def _read() -> dict:
        """Dummy read method."""
        try:
            with open('~database.json', mode='r', encoding='utf-8') as file:
                data = json.load(file)
        except FileNotFoundError:
            data = {
                'users': {},
                'categories': {},
            }
        return data

    @staticmethod
    def _write(data: dict) -> None:
        """Dummy write method."""
        with open('~database.json', mode='w+', encoding='utf-8') as file:
            json.dump(data, file, ensure_ascii=False, indent=4)

    async def user_exists(self, user: models.User) -> bool:
        """Return True if user is already registered."""
        _db = self._read()

        return user.sid in _db.get('users', [])

    async def register_user(self, user: models.User) -> models.User:
        """Save new user to the database."""
        data = self._read()
        data['users'].setdefault(user.sid, {
            'sid': user.sid,
            'first_name': user.first_name,
        })
        data['categories'].setdefault(user.sid, {})
        self._write(data)
        return user

    async def get_categories(self, user: models.User) -> list[models.Category]:
        """Try loading categories for user."""
        data = self._read()

        raw = data['categories'].get(user.sid)

        if raw is None:
            return []

        categories = [
            models.Category(**x)
            for x in raw.values()
        ]

        return categories

    async def create_category(
            self,
            user: models.User,
            category: models.Category,
    ) -> models.Category:
        """Create new category."""
        data = self._read()

        categories = data['categories'].setdefault(user.sid, {})
        category_id = str(len(categories) + 1)
        categories[category_id] = {
            'id': category_id,
            'name': category.name,
        }

        category.id = category_id
        self._write(data)
        return category

    async def category_has_records(
            self,
            user: models.User,
            name: str,
    ) -> bool:
        """Return True if category has records."""
        # TODO
        return False

    async def drop_category(
            self,
            user: models.User,
            name: str,
    ) -> None:
        """Delete category."""
        data = self._read()
        key = None

        if user.sid in data['categories']:
            for cat_id, model in data['categories'][user.sid].items():
                if model['name'] == name:
                    key = cat_id
                    break

            if key is not None:
                del data['categories'][user.sid][key]

        self._write(data)
