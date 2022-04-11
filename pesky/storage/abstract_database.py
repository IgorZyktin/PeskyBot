# -*- coding: utf-8 -*-
"""Basic database interface.
"""
import abc

from pesky.domain import models


class AbstractDatabase(abc.ABC):
    """Basic database interface.
    """

    @abc.abstractmethod
    async def user_exists(self, user: models.User) -> bool:
        """Return True if user is already registered."""

    @abc.abstractmethod
    async def register_user(self, user: models.User) -> models.User:
        """Save new user to the database."""
