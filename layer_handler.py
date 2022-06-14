import logging

log = logging.getLogger(__name__)


def handle(*args, **kwargs):
    print(f"Layer handler called: {args} {kwargs}")
    log.info(f"Layer handler called: {args} {kwargs}")
