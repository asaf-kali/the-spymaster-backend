import base64
import json
from typing import Any, List

import boto3
import sentry_sdk
from dynaconf import Dynaconf


class LazyConfig:
    def __init__(self, settings: Dynaconf = None):
        self._settings = settings

    def __getattr__(self, item) -> Any:
        return self.get(item)

    def get(self, key: str, default=None) -> Any:
        return self.settings.get(key, default)

    def load(self, override_files: List[str] = None):
        if not override_files:
            override_files = []
        settings_files = ["settings.toml", "local.toml", "secrets.toml"] + override_files
        self._settings = Dynaconf(environments=True, settings_files=settings_files)
        try:
            self.load_kms_secrets()
        except Exception as e:
            sentry_sdk.capture_exception(e)
            print(f"Failed loading KMS secrets: {e}")

    @property
    def settings(self) -> Dynaconf:
        if not self._settings:
            self.load()
        return self._settings

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

    @property
    def base_backend_url(self) -> str:
        return self.get("BASE_BACKEND_URL")

    @property
    def should_load_models_from_s3(self) -> bool:
        return self.get("SHOULD_LOAD_MODELS_FROM_S3")

    @property
    def s3_bucket_name(self) -> str:
        return self.get("S3_BUCKET_NAME")

    @property
    def env_name(self) -> str:
        return self.get("ENV_FOR_DYNACONF")

    def load_kms_secrets(self) -> dict:
        secret_name = f"the-spymaster-{self.env_name}-secrets"
        client = boto3.client(service_name="secretsmanager")
        response = client.get_secret_value(SecretId=secret_name)
        if "SecretString" in response:
            secrets_string = response["SecretString"]
        else:
            secrets_string = base64.b64decode(response["SecretBinary"])
        secrets_dict = json.loads(secrets_string) or {}
        print("KMS secrets loaded successfully")
        self._settings.update(**secrets_dict)  # type: ignore
        return secrets_dict


def get_config() -> LazyConfig:
    return LazyConfig()
