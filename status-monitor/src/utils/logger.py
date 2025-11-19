import logging

def setup_logger(name: str) -> logging.Logger:
    """Set up a logger with the specified name."""
    logger = logging.getLogger(name)
    logger.setLevel(logging.DEBUG)

    ch = logging.StreamHandler()
    ch.setLevel(logging.DEBUG)

    # Create formatter
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

    ch.setFormatter(formatter)

    logger.addHandler(ch)

    return logger

def log_info(logger: logging.Logger, message: str):
    """Log an info message."""
    logger.info(message)

def log_error(logger: logging.Logger, message: str):
    """Log an error message."""
    logger.error(message)

def log_warning(logger: logging.Logger, message: str):
    """Log a warning message."""
    logger.warning(message)