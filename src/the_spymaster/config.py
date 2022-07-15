import logging
from typing import List

from the_spymaster_util.config import LazyConfig

log = logging.getLogger(__name__)


class Config(LazyConfig):
    def load(self, override_files: List[str] = None):
        super().load(override_files)
        if self.load_ssm_secrets:
            self._load_parameters()
        log.info("Config loaded")

    def _load_parameters(self):
        parameters = [
            f"{self.service_prefix}-django-secret-key",
            f"{self.service_prefix}-sentry-dsn",
            f"{self.service_prefix}-db-password",
        ]
        self.load_ssm_parameters(parameters)
        for parameter_name in parameters:
            new_parameter_name = parameter_name.replace(f"{self.service_prefix}-", "").replace("-", "_")
            parameter_value = self.get(parameter_name)
            if parameter_value:
                self.set(new_parameter_name, parameter_value)

    @property
    def env_verbose_name(self) -> str:
        return self.get("ENV_VERBOSE_NAME")

    @property
    def service_prefix(self):
        return f"the-spymaster-backend-{self.env_name}"

    @property
    def django_debug(self) -> bool:
        return self.get("DJANGO_DEBUG") or False

    @property
    def django_secret_key(self) -> str:
        value = self.get(f"{self.service_prefix}-django-secret-key") or self.get("DJANGO_SECRET_KEY")
        if not value:
            raise ValueError("DJANGO_SECRET_KEY is not set")
        return value

    @property
    def sentry_dsn(self) -> str:
        return self.get(f"{self.service_prefix}-sentry-dsn") or self.get("SENTRY_DSN")

    @property
    def solvers_backend_url(self) -> str:
        return self.get("SOLVERS_BACKEND_URL") or "http://localhost:5000"

    @property
    def recaptcha_site_key(self) -> str:
        return self.get("RECAPTCHA_SITE_KEY")

    @property
    def recaptcha_private_key(self) -> str:
        return self.get("RECAPTCHA_PRIVATE_KEY")

    @property
    def google_oauth_client_id(self) -> str:
        return self.get("GOOGLE_OAUTH_CLIENT_ID")

    @property
    def google_oauth_client_secret(self) -> str:
        return self.get("GOOGLE_OAUTH_CLIENT_SECRET")

    @property
    def load_ssm_secrets(self) -> bool:
        return self.get("LOAD_SSM_SECRETS")


_config = Config()


def get_config() -> Config:
    return _config
