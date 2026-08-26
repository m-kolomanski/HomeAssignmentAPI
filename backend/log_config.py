import logging
import re
import json
import copy
from .config import settings
from contextvars import ContextVar

class HAAPILogFormatter(logging.Formatter):
    method: ContextVar[str] = ContextVar("method", default = "-")
    route: ContextVar[str] = ContextVar("route", default = "-")

class LogConsoleFormatter(HAAPILogFormatter):
    COLORS = {
        "DEBUG":    "\033[90m",  # gray
        "INFO":     "\033[34m",  # blue
        "WARNING":  "\033[33m",  # yellow
        "ERROR":    "\033[38;5;208m",  # orange (256-color)
        "CRITICAL": "\033[31m",  # red
    }
    BOLD = "\033[1m"
    RESET = "\033[0m"
    
    def format(self, record):
        # Colors the log level
        record = copy.copy(record)

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

class LogJsonFormatter(HAAPILogFormatter):
    def format(self, record):
        log_entry = {
            "timestamp": self.formatTime(record, "%Y-%m-%d %H:%M:%S"),
            "level": record.levelname,
            "logger": record.name,
            "method": self.method.get(),
            "route": self.route.get(),
            "message": record.getMessage(),
        }

        return json.dumps(log_entry)

LOG_CONFIG = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "default": {
            "()": LogConsoleFormatter,
            "format": "%(levelprefix)s[%(name)s][%(method)s %(route)s] %(asctime)s: %(message)s",
            "datefmt": "%Y-%m-%d %H:%M:%S"
        },
        "json": {
            "()": LogJsonFormatter
        }
    },
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "formatter": "default"
        },
        "file": {
            "class": "logging.handlers.TimedRotatingFileHandler",
            "filename": settings.HAAPI_LOG_FILE_PATH,
            "formatter": "json",
            "when": "midnight",
            "interval": 1,
            "backupCount": 7
        }
    },
    "root": {
        "level": settings.HAAPI_LOG_LEVEL,
        "handlers": ["console", "file"]
    },
    "loggers": {
        "uvicorn": {"handlers": [], "propagate": False},
        "uvicorn.error": {"handlers": [], "propagate": False},
        "uvicorn.access": {"handlers": [], "propagate": False},
    },
}
