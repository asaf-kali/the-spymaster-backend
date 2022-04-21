import json
import logging
import sys
from datetime import datetime
from logging import Filter, Formatter, Logger, LogRecord
from logging.config import dictConfig


class ContextLogger(Logger):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.context = {}

    def _log(self, *args, **kwargs) -> None:
        extra = kwargs.get("extra")
        kwargs["extra"] = {"extra": extra, "context": self.context}
        super()._log(*args, **kwargs)  # noqa

    def update_context(self, data: dict = None, **kwargs):
        if data:
            self.context.update(data)
        if kwargs:
            self.context.update(kwargs)

    def set_context(self, data: dict):
        self.context = data

    def reset_context(self):
        self.set_context({})


class ExtraDataFormatter(Formatter):
    def format(self, record: LogRecord) -> str:
        message = super().format(record)
        extra = getattr(record, "extra", None)
        if extra:
            message += f" extra: {extra}"
        return message


class JsonFormatter(Formatter):
    def __init__(self, detailed: bool = False, indented: bool = False):
        super().__init__()
        self.detailed = detailed
        self.indent = 2 if indented else None
        self.tz = datetime.now().astimezone().tzinfo

    def format(self, record: LogRecord) -> str:
        data: dict = {
            "datetime": datetime.fromtimestamp(record.created, self.tz).isoformat(sep=" ", timespec="milliseconds"),
            "message": record.msg or record.message,
        }
        context = getattr(record, "context", None)
        extra = getattr(record, "extra", None)
        if context:
            data["context"] = context
        if extra:
            data["extra"] = extra
        if self.detailed:
            data.update(
                {
                    "level": record.levelname,
                    "func_name": record.funcName,
                    "module": record.module,
                    "file_path": record.pathname,
                    "line_number": record.lineno,
                    "process": record.process,
                    "thread": record.thread,
                    "process_name": record.processName,
                    "thread_name": record.threadName,
                    "exc_info": record.exc_info,
                    "level_code": record.levelno,
                    "timestamp": record.created,
                }
            )
        return json.dumps(data, indent=self.indent, ensure_ascii=False)


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


def configure_logging(
    formatter: str = None, level: str = None, detailed_json: bool = True, indented_json: bool = False
):
    config = {
        "version": 1,
        "disable_existing_loggers": False,
        "formatters": {
            "simple": {"class": "utils.logging.ExtraDataFormatter"},
            "debug": {
                "class": "utils.logging.ExtraDataFormatter",
                "format": "[%(asctime)s.%(msecs)03d] [%(levelname)-.4s]: %(message)s @@@ "
                "[%(threadName)s] [%(name)s:%(lineno)s]",
                "datefmt": "%Y-%m-%d %H:%M:%S",
            },
            "json": {
                "()": "utils.logging.JsonFormatter",
                "detailed": detailed_json,
                "indented": indented_json,
            },
            "test": {
                "class": "utils.logging.ExtraDataFormatter",
                "format": "[%(asctime)s.%(msecs)03d] [%(levelname)-.4s]: %(message)s "
                "[%(threadName)s] [%(name)s:%(lineno)s]",
                "datefmt": "%H:%M:%S",
            },
        },
        "filters": {
            "std_filter": {"()": "utils.logging.LevelRangeFilter", "high": logging.WARNING},
            "err_filter": {"()": "utils.logging.LevelRangeFilter", "low": logging.WARNING},
        },
        "handlers": {
            "console_out": {
                "class": "logging.StreamHandler",
                "filters": ["std_filter"],
                "formatter": formatter or "simple",
                "stream": sys.stdout,
            },
            "console_err": {
                "class": "logging.StreamHandler",
                "filters": ["err_filter"],
                "formatter": formatter or "debug",
                "stream": sys.stdout,
                # "stream": sys.stderr,
            },
            "file": {
                "class": "logging.FileHandler",
                "filename": "run.log",
                "formatter": formatter or "debug",
            },
        },
        "root": {"handlers": ["console_out", "console_err", "file"], "level": level or "DEBUG"},
    }
    dictConfig(config)
    log.debug("Logging configured")


def wrap(o: object) -> str:
    return f"[{o}]"


RUN_ID = datetime.now().timestamp()
