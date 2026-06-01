import logging
import re
from .config import settings
from contextvars import ContextVar

class LogConsoleFormatter(logging.Formatter):
    COLORS = {
        "DEBUG":    "\033[90m",  # gray
        "INFO":     "\033[34m",  # blue
        "WARNING":  "\033[33m",  # yellow
        "ERROR":    "\033[38;5;208m",  # orange (256-color)
        "CRITICAL": "\033[31m",  # red
    }
    BOLD = "\033[1m"
    RESET = "\033[0m"

    method: ContextVar[str] = ContextVar("method", default = "-")
    route: ContextVar[str] = ContextVar("route", default = "-")

    def format(self, record):
        # Colors the log level
        color = self.COLORS.get(record.levelname, self.RESET)
        record.levelprefix = f"{color}[{record.levelname}]{self.RESET}"
        
        # Adds method and route to the log
        record.method = self.method.get()
        record.route = self.route.get()
        
        # Checks if arguments were passed to the formatter. If they were, args are printed in bold.
        if record.args:
            args = record.args if isinstance(record.args, tuple) else (record.args,)
            bold_args = tuple(f"{self.BOLD}{arg}{self.RESET}" for arg in args)
            record.msg = re.sub(r'%[^%]', '{}', record.msg).format(*bold_args)
            record.args = None
        return super().format(record)

LOG_CONFIG = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "default": {
            "()": LogConsoleFormatter,
            "format": "%(levelprefix)s[%(name)s][%(method)s %(route)s] %(asctime)s: %(message)s",
            "datefmt": "%Y-%m-%d %H:%M:%S"
        }
    },
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "formatter": "default"
        }
    },
    "root": {
        "level": settings.HAAPI_LOG_LEVEL,
        "handlers": ["console"]
    },
}
