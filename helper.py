import logging
import re

logger = logging.getLogger("MTA_Subway_Ridership_Dashboard")


def log_function_call(func):
    """Decorator to log the function name and parameters when called."""

    def wrapper(*args, **kwargs):
        logger.debug(
            f"Function called: {func.__name__} with args: {args} and kwargs: {kwargs}"
        )
        return func(*args, **kwargs)

    return wrapper

def extract_lines(station):
    """Extract lines from station name."""
    lines_txt = re.findall(r"\((.*?)\)", station)
    lines = []

    for line in lines_txt:
        line = line.split(",")
        if len(line) > 0:
            line = [l.strip() for l in line]
            lines += line

    lines = sorted(list(set(lines)))

    return lines

