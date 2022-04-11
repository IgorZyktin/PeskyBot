# -*- coding: utf-8 -*-
"""Entry point."""
from aiogram import executor

from pesky import infra
from pesky.bot.dependencies import dp

LOG = infra.get_logger(__name__)


def main():
    """Entry point."""
    LOG.info('Starting PeskyBot!')
    executor.start_polling(dp)


if __name__ == "__main__":
    main()
