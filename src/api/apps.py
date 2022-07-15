import logging

from django.apps import AppConfig
from django.conf import settings
from the_spymaster_util.logging import wrap

log = logging.getLogger(__name__)


class ApiConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "api"

    def ready(self):
        log.info(f"{self.verbose_name} is ready, environment: {wrap(settings.ENVIRONMENT)}")
