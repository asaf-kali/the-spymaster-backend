import json
import logging
import threading
from datetime import datetime, timezone
from logging import Filter, Formatter, Logger, LogRecord
from logging.config import dictConfig
from typing import Optional

CONTEXT_KEY = "_logging_context"


class ContextLogger(Logger):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._thread_storage = threading.local()

    @property
    def context(self) -> dict:
        current_context = getattr(self._thread_storage, CONTEXT_KEY, None)
        if current_context is None:
            current_context = {}
            self.set_context(current_context)
        return current_context

    def _log(self, *args, **kwargs) -> None:
        extra = kwargs.get("extra")
        kwargs["extra"] = {"extra": extra, "context": self.context}
        super()._log(*args, **kwargs)  # noqa

    def update_context(self, data: dict = None, **kwargs):
        new_context = self.context
        if data:
            new_context.update(data)
        if kwargs:
            new_context.update(kwargs)
        self.set_context(new_context)

    def set_context(self, data: dict):
        setattr(self._thread_storage, CONTEXT_KEY, data)

    def reset_context(self):
        self.set_context({})


class ContextFormatter(Formatter):
    def format(self, record: LogRecord) -> str:
        message = original_message = record.msg
        extra = getattr(record, "extra", None)
        context = getattr(record, "context", None)
        if extra:
            message += f" | {extra}"
        if context:
            message += f" | {context}"
        record.msg = message
        result = super().format(record)
        record.msg = original_message
        return result


class JsonFormatter(Formatter):
    def __init__(self, indented: bool = False, tz: Optional[timezone] = None):
        super().__init__()
        self.indent = 2 if indented else None
        self.tz = tz or datetime.now().astimezone().tzinfo

    def format(self, record: LogRecord) -> str:
        data = {
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
        exc_info = getattr(record, "exc_info", None)
        if exc_info:
            data["exc_info"] = self.formatException(exc_info)
        try:
            return json.dumps(data, indent=self.indent, ensure_ascii=False)
        except Exception as e:  # noqa
            log.debug(f"Log serialization failed, trying without extra: {e}")
            data.pop("extra")
            try:
                return json.dumps(data, indent=self.indent, ensure_ascii=False)
            except Exception as e:  # noqa
                log.warning("Log serialization failed")
                return str(data)

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
