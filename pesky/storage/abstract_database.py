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

    @abc.abstractmethod
    async def get_categories(self, user: models.User) -> list[models.Category]:
        """Try loading categories for user."""

    async def create_category(
            self,
            user: models.User,
            category: models.Category,
    ) -> models.Category:
        """Create new category."""

    @abc.abstractmethod
    async def category_has_records(
            self,
            user: models.User,
            name: str,
    ) -> bool:
        """Return True if category has records."""

    async def drop_category(
            self,
            user: models.User,
            name: str,
    ) -> None:
        """Delete category."""
