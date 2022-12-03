import logging
from typing import List, Optional

from the_spymaster_util.config import LazyConfig

log = logging.getLogger(__name__)


class Config(LazyConfig):
    def load(self, override_files: Optional[List[str]] = None):
        super().load(override_files)
        if self.load_ssm_secrets:
            self._load_parameters()
        log.info("Config loaded")

    def _load_parameters(self):
        parameters = [f"{self.service_prefix}-django-secret-key", f"{self.service_prefix}-sentry-dsn"]
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
        return self.is_test or bool(self.get("DJANGO_DEBUG"))

    @property
    def is_test(self) -> bool:
        return self.env_name == "test"

    @property
    def is_local(self) -> bool:
        return self.env_name == "local"

    @property
    def sentry_setup(self) -> bool:
        return not self.is_test and not self.is_local

    @property
    def setup_sqlite_db(self) -> bool:
        return self.is_test or self.is_local

    @property
    def game_items_table_name(self) -> str:
        return self.get("game_items_table_name") or f"{self.service_prefix}-game-items"

    @property
    def django_secret_key(self) -> str:
        value = self.get(f"{self.service_prefix}-django-secret-key") or self.get("DJANGO_SECRET_KEY")
        if value:
            return value
        if self.is_test:
            return "54dc6d2d8ccc4cec8196397af5ff355c"
        raise ValueError("DJANGO_SECRET_KEY is not set")

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

    @property
    def dynamo_db_host(self) -> Optional[str]:
        if self.is_local:
            return "http://localhost:4444"
        return None


_config = Config()


def get_config() -> Config:
    return _config
