# -*- coding: utf-8 -*-
"""Application settings.
"""
from pydantic import BaseSettings


class Config(BaseSettings):
    """Application settings."""
    pesky_token: str


config = Config()
