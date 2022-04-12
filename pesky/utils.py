# -*- coding: utf-8 -*-
"""Common utils.
"""
from typing import Callable


def make_num(total: int) -> Callable[[int], str]:
    """Factory for enumerators."""
    digits = len(str(total))
    prefix = '{{number:0{digits}}}'.format(digits=digits)

    def num(number: int) -> str:
        """Make bullet point."""
        return prefix.format(number=number)

    return num


def sanitize_user_input(raw_text: str) -> str:
    """Clear specific symbols from user input."""
    # TODO - remove anything code/tags like
    return raw_text
