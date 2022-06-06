import json
import logging
import sys
import threading
from datetime import datetime, timezone
from logging import Filter, Formatter, Logger, LogRecord
from logging.config import dictConfig
from typing import Optional

import ulid

CONTEXT_KEY = "_logging_context"
EMPTY_EXEC_INFO = (None, None, None)
_thread_storage = threading.local()


class ContextLogger(Logger):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._thread_storage = _thread_storage

    @property
    def context(self) -> dict:
        current_context = getattr(self._thread_storage, CONTEXT_KEY, None)
        if current_context is None:
            return self.reset_context()
        return current_context

    def update_context(self, **kwargs) -> dict:
        new_context = self.context
        new_context.update(kwargs)
        return self.set_context(new_context)

    def set_context(self, context: Optional[dict] = None, **kwargs) -> dict:
        context = context or {}
        if "context_id" not in context:
            context = {"context_id": ulid.new().str, **context}  # Always keep context_id first.
        setattr(self._thread_storage, CONTEXT_KEY, context)
        if kwargs:
            return self.update_context(**kwargs)
        return context

    def reset_context(self) -> dict:
        return self.set_context({})

    def _log(self, *args, **kwargs) -> None:
        extra = kwargs.get("extra")
        kwargs["extra"] = {"extra": extra, "context": self.context}
        super()._log(*args, **kwargs)  # noqa


class ContextFormatter(Formatter):
    def __init__(self, *args, log_extra: bool = True, log_context: bool = True, **kwargs):
        super().__init__(*args, **kwargs)
        self.log_extra = log_extra
        self.log_context = log_context

    def format(self, record: LogRecord) -> str:
        message = original_message = record.msg
        extra = getattr(record, "extra", None)
        context = getattr(record, "context", None)
        message = str(message)
        if extra and self.log_extra:
            message += f" | {extra}"
        if context and self.log_context:
            message += f" | {context}"
        record.msg = message
        result = super().format(record)
        record.msg = original_message
        return result


class JsonFormatter(Formatter):
    def __init__(self, *args, indented: bool = False, tz: Optional[timezone] = None, **kwargs):
        super().__init__(*args, **kwargs)
        self.indent = 2 if indented else None
        self.tz = tz or datetime.now().astimezone().tzinfo

    def format(self, record: LogRecord) -> str:
        record_data = {
            # Base
            "date_time": self._format_date_time(record.created),
            "level": record.levelname,
            "message": super().format(record),
            "extra": getattr(record, "extra", None),
            "context": getattr(record, "context", None),
            # Debug
            "func_name": record.funcName,
            "file_path": record.pathname,
            "line_number": record.lineno,
            # More
            "level_code": record.levelno,
            "timestamp": record.created,
            "logger": record.name,
            "thread_name": record.threadName,
        }
        exc_info = getattr(record, "exc_info", None) or sys.exc_info()
        if exc_info and exc_info != EMPTY_EXEC_INFO and record.levelno >= logging.ERROR:
            record_data["exc_info"] = self.formatException(exc_info)
        try:
            return json.dumps(record_data, indent=self.indent, ensure_ascii=False)
        except Exception as e:  # noqa
            log.debug(f"Record serialization failed: {e}")
            return str(record_data)

    def _format_date_time(self, timestamp: float) -> str:
        return datetime.fromtimestamp(timestamp, self.tz).isoformat(sep=" ", timespec="milliseconds")


class LevelRangeFilter(Filter):
    def __init__(self, low=0, high=100):
        Filter.__init__(self)
        self.low = low
        self.high = high

    def filter(self, record):
        if self.low <= record.levelno < self.high:
            return True
        return False


logging.setLoggerClass(ContextLogger)


def get_logger(name: str) -> ContextLogger:
    return logging.getLogger(name)  # type: ignore


log = get_logger(__name__)


def configure_logging():
    from the_spymaster import settings

    dictConfig(settings.LOGGING)
    log.debug("Logging configured")


def wrap(o: object) -> str:
    return f"[{o}]"


RUN_ID = datetime.now().timestamp()
