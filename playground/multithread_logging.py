from random import random
from threading import Thread
from time import sleep

from the_spymaster.utils import configure_logging, get_logger

configure_logging()
log = get_logger(__name__)


def worker(name: str):
    log.update_context(thread=name)
    log.info(f"{name} start", extra={"data": 1})
    sleep(random() / 10)
    log.info(f"{name} end")


def main():
    log.info("main")
    for i in range(5):
        Thread(target=worker, args=(f"t{i + 1}",), name=f"t{i + 1}").start()


if __name__ == "__main__":
    main()
