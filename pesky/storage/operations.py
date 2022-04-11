# -*- coding: utf-8 -*-
"""Abstract storage operations.
"""
from pesky.domain import models
from pesky.storage.abstract_database import AbstractDatabase


async def maybe_register_user(
        database: AbstractDatabase,
        user: models.User,
) -> None:
    """Register user if first seen, ignore otherwise."""
