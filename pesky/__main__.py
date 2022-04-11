# -*- coding: utf-8 -*-
"""Entry point."""
from aiogram import executor

from pesky.bot.dependencies import dp


def main():
    """Entry point."""
    executor.start_polling(dp)


if __name__ == "__main__":
    main()
