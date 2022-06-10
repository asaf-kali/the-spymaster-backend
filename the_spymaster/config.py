from typing import List

from the_spymaster_util import LazyConfig


class Config(LazyConfig):
    def load(self, override_files: List[str] = None):
        super().load(override_files)
        secret_name = f"the-spymaster-{self.env_name}-secrets"
        try:
            self.load_kms_secrets(secret_name)
        except Exception:
            pass

    @property
    def env_verbose_name(self) -> str:
        return self.get("ENV_VERBOSE_NAME")

    @property
    def django_debug(self) -> bool:
        return self.get("DJANGO_DEBUG") or False

    @property
    def django_secret_key(self) -> str:
        return self.get("DJANGO_SECRET_KEY")

    @property
    def sentry_dsn(self) -> str:
        return self.get("SENTRY_DSN")

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
    def should_load_models_from_s3(self) -> bool:
        return self.get("SHOULD_LOAD_MODELS_FROM_S3")

    @property
    def s3_bucket_name(self) -> str:
        return self.get("S3_BUCKET_NAME")


def get_config() -> Config:
    return Config()
