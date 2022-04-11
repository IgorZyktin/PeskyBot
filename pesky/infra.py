# -*- coding: utf-8 -*-
"""Common infrastructure.
"""
import logging

logging.basicConfig(level=logging.INFO)


def get_logger(name: str):
    """Return logger instance."""
    return logging.getLogger(name)
