from dynaconf import Dynaconf


class Config:
    def __init__(self, settings: Dynaconf = None):
        self._settings = settings

    def __getattr__(self, item) -> any:
        return self.get(item)

    def get(self, key: str, default=None) -> any:
        return self.settings.get(key, default)

    def load(self):
        self._settings = Dynaconf(
            environments=True,
            settings_files=["settings.toml", ".secrets.toml"],
        )

    @property
    def settings(self) -> Dynaconf:
        if not self._settings:
            self.load()
        return self._settings

    @property
    def env_verbose_name(self) -> str:
        return self.get("env_verbose_name")

    @property
    def django_debug(self) -> bool:
        return self.get("django_debug") or False

    @property
    def django_secret_key(self) -> str:
        return self.get("DJANGO_SECRET_KEY")

    @property
    def sentry_dsn(self) -> str:
        return self.get("SENTRY_DSN")

    @property
    def telegram_token(self) -> str:
        return self.get("TELEGRAM_TOKEN")

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


config = Config()
