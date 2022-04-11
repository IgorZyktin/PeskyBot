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
        self._write(data)
        return user
