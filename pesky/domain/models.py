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
