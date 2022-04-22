from django.core.management import BaseCommand

from utils import get_logger

log = get_logger(__name__)


class Command(BaseCommand):
    def handle(self, *args, **options):
        log.info("Hi")
