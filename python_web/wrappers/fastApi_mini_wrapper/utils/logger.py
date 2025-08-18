import logging
from colorlog import ColoredFormatter


def setup_logger(log_level=None, log_file=None):
    logger = logging.getLogger(__name__)
    logger.propagate = False  # Prevent propagation to root logger

    # Clear existing handlers to avoid duplication
    if logger.handlers:
        logger.handlers.clear()

    # Rest of your setup (console handler, file handler, etc.)
    console_handler = logging.StreamHandler()
    color_formatter = ColoredFormatter(
        '%(log_color)s%(asctime)s - %(message)s',
        log_colors={
            'DEBUG': 'cyan',
            'INFO': 'green',
            'WARNING': 'yellow',
            'ERROR': 'red',
            'CRITICAL': 'red,bg_white',
        }
    )
    console_handler.setFormatter(color_formatter)
    logger.addHandler(console_handler)

    if log_file:
        file_handler = logging.FileHandler(log_file, mode='a')
        file_formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        file_handler.setFormatter(file_formatter)
        logger.addHandler(file_handler)

    # Set level
    levels = {
        'INFO': logging.INFO,
        'DEBUG': logging.DEBUG,
        'WARNING': logging.WARNING,
        'CRITICAL': logging.CRITICAL,
        'ERROR': logging.ERROR
    }
    logger.setLevel(levels.get(log_level, logging.CRITICAL))
    if log_level not in levels:
        logger.critical('[setup_logger] invalid level specified: valid=INFO/DEBUG/WARNING/CRITICAL/ERROR')
        return None

    return logger
