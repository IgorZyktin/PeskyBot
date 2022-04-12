# -*- coding: utf-8 -*-
"""Abstract storage operations.
"""
from pesky import infra
from pesky.domain import models
from pesky.storage.abstract_database import AbstractDatabase

LOG = infra.get_logger(__name__)


async def maybe_register_user(
        database: AbstractDatabase,
        user: models.User,
) -> bool:
    """Register user if first seen, ignore otherwise."""
    if await database.user_exists(user):
        return False

    LOG.info('Registering new user: %s, %s', user.id, user.first_name)
    await database.register_user(user)
    return True
