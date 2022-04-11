# -*- coding: utf-8 -*-
"""Application domain models."""
from pydantic import BaseModel


class User(BaseModel):
    """Simple user model."""
    id: int
    first_name: str

    @property
    def sid(self) -> str:
        """Return string version of id."""
        return str(self.id)


class Category(BaseModel):
    """User activity category."""
    id: int
    name: str

    def __str__(self) -> str:
        """Return string representation."""
        return self.name
