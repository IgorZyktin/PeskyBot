# -*- coding: utf-8 -*-
"""Application domain models."""
from pydantic import BaseModel


class User(BaseModel):
    """Simple user model."""
    id: int
    first_name: str
