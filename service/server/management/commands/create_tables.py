# pylint: skip-file

import logging

from django.core.management import BaseCommand

from server.logic.db import GameItem

log = logging.getLogger(__name__)


class Command(BaseCommand):
    def handle(self, *args, **options):
        create_tables()
        log.info("Tables created.")


def create_tables():
    GameItem.create_table(read_capacity_units=1, write_capacity_units=1)
