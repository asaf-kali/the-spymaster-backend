from dynaconf import Dynaconf


class Config:
    def __init__(self, settings: Dynaconf = None):
        self._settings = settings

    def get(self, key, default=None):
        return self.settings.get(key, default)

    @property
    def settings(self) -> Dynaconf:
        if not self._settings:
            self._settings = Dynaconf(
                envvar_prefix="DYNACONF",
                settings_files=["settings.toml", ".secrets.toml"],
            )
        return self._settings

    @property
    def telegram_token(self) -> str:
        return self.get("TELEGRAM_TOKEN")


config = Config()
