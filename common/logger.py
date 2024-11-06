import sys

from loguru import logger


def get_logger(log_file="record.log", level="DEBUG"):
    logger.remove()
    logger.add(
        log_file,
        rotation="1 MB",
        retention="10 days",
        level=level,
        format="{time} {level} {message}",
        colorize=True,
    )
    logger.add(
        sink=sys.stderr, level="ERROR", format="{time} {level} {message}", colorize=True
    )
    return logger
