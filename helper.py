import logging

logger = logging.getLogger("MTA_Subway_Ridership_Dashboard")


def log_function_call(func):
    """Decorator to log the function name and parameters when called."""

    def wrapper(*args, **kwargs):
        logger.debug(
            f"Function called: {func.__name__} with args: {args} and kwargs: {kwargs}"
        )
        return func(*args, **kwargs)

    return wrapper
