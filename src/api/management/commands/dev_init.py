import logging

from allauth.socialaccount.models import SocialApp
from django.conf import settings
from django.contrib.sites.models import Site
from django.core import management
from django.core.management import BaseCommand
from rest_framework.authtoken.models import Token
from the_spymaster_util.http.errors import BadRequestError

from api.models.user import SpymasterUser

log = logging.getLogger(__name__)
DEFAULT_EMAIL = "admin@the-spymaster.xyz"
DEFAULT_PASSWORD = "qweasd"


class EnvironmentSafetyError(BadRequestError):
    operation_name: str
    environment: str

    def __init__(self, operation_name: str, environment: str):
        self.operation_name = operation_name
        self.environment = environment
        super().__init__(
            message="Can't perform operation on current environment.",
            data={"operation_name": self.operation_name, "environment": self.environment},
        )


def _create_user(  # pylint: disable=too-many-arguments
    username: str,
    email: str,
    first_name: str,
    last_name: str,
    password: str = DEFAULT_PASSWORD,
    is_staff: bool = False,
    is_superuser: bool = False,
) -> SpymasterUser:
    user, created = SpymasterUser.objects.get_or_create(username=username)  # pylint: disable=unused-variable
    user.email, user.first_name, user.last_name = email, first_name, last_name
    user.is_staff, user.is_superuser = is_staff, is_superuser
    user.set_password(password)
    user.save()
    return user


def create_admin():
    if not settings.DEBUG:
        log.warning("Not creating admins on non-debug environment!")
        return
    log.info("Creating admin...")
    _create_user(
        username="admin", email=DEFAULT_EMAIL, first_name="Test", last_name="Admin", is_staff=True, is_superuser=True
    )


def create_social_app():
    log.info("Creating Google social app...")
    client_id = settings.GOOGLE_OAUTH_CLIENT_ID
    if client_id is None:
        log.warning("Google OAuth Client ID not found, skipping Google OAuth client configuration.")
        return
    app, _ = SocialApp.objects.get_or_create(
        name="Google",
        provider="google",
        client_id=client_id,
        secret=settings.GOOGLE_OAUTH_CLIENT_SECRET,
    )
    app.sites.add(1)
    app.save()


def set_default_passwords():
    if not settings.DEBUG:
        log.error("Should not happen!")
        return
    log.info("Resetting passwords...")
    if not settings.DEBUG:
        return
    for user in SpymasterUser.objects.all():
        user.set_password("qweasd")
        user.save()


def configure_site():
    site = Site.objects.get(pk=1)
    site.name = site.domain = "localhost"
    site.save()


def create_tokens():
    for user in SpymasterUser.objects.all():
        Token.objects.get_or_create(user=user)  # pylint: disable=no-member


def create_all():
    log.info("Create all called...")
    create_admin()
    create_tokens()
    create_social_app()
    configure_site()
    set_default_passwords()


class Command(BaseCommand):
    def handle(self, *args, **options):
        if not settings.DEBUG:
            raise EnvironmentSafetyError(operation_name="dev_init", environment=settings.ENVIRONMENT)
        log.info("Calling load data...")
        try:
            management.call_command("loaddata", "dev.json")
        except Exception as e:  # pylint: disable=invalid-name, broad-except
            log.error(e)
        create_all()
        log.info("Dev init done")
