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
