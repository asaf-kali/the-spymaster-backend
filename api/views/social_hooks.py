from urllib.parse import urlencode

from allauth.account.models import EmailAddress
from allauth.account.utils import perform_login
from allauth.socialaccount.adapter import DefaultSocialAccountAdapter
from allauth.socialaccount.models import SocialLogin
from allauth.socialaccount.providers.oauth2.views import (
    OAuth2CallbackView,
    OAuth2LoginView,
)
from allauth.socialaccount.signals import pre_social_login
from django.core.handlers.wsgi import WSGIRequest
from django.dispatch import receiver
from django.http import HttpResponse
from django.shortcuts import redirect
from django.urls import reverse

from api.logic.errors import BadRequestError, UnauthorizedError
from api.models import SpymasterUser
from api.views import log
from utils import wrap


def _create_email_address(existing_user: SpymasterUser):
    email_address, created = EmailAddress.objects.get_or_create(user=existing_user, email=existing_user.email)
    email_address.primary = email_address.verified = True
    email_address.save()


@receiver(signal=pre_social_login)
def find_existing_user_hook(request: WSGIRequest, sociallogin: SocialLogin, *args, **kwargs):
    log.debug("find_existing_user_hook called")
    social_user: SpymasterUser = sociallogin.user  # This user might not exist in DB yet
    if social_user.id:
        log.debug("User already exists and connected to social login")
        return
    log.debug("Social login doesnt exist, looking for user...")
    try:
        existing_user = SpymasterUser.objects.get(email=social_user.email)
        log.debug("User exists, updating details from social login")
        if not existing_user.first_name or not existing_user.last_name:
            existing_user.first_name = social_user.first_name
            existing_user.last_name = social_user.last_name
        sociallogin.state["process"] = "connect"
        sociallogin.state["next"] = reverse("login_complete")
        _create_email_address(existing_user)
        perform_login(request, existing_user, "none")
    except SpymasterUser.DoesNotExist:
        log.debug("User didn't exist")
        social_user.username = social_user.email.split("@")[0]


def _generate_key_response(request: WSGIRequest) -> HttpResponse:
    user: SpymasterUser = request.user  # noqa
    if not user.is_authenticated:
        raise UnauthorizedError("User is not authenticated")
    # params = {}
    # nonce = request.GET.get("nonce", None)
    callback_url = request.GET.get("callback_url", None)
    # if nonce:
    #     log.debug(f"Generate key response called with nonce {wrap(nonce)}")
    #     params.update({"nonce": nonce})
    url = callback_url if callback_url else "/"
    log.debug(f"Redirecting to {wrap(url)}")
    return redirect(url)


def _is_authorized_callback(url: str) -> bool:
    allowed_endpoints = ["http://localhost:8000", "http://localhost:3000"]
    return any(url.startswith(ep) for ep in allowed_endpoints)


class CustomSocialAccountAdapter(DefaultSocialAccountAdapter):
    def get_connect_redirect_url(self, request, socialaccount):
        return reverse("login_complete")


class CustomOAuth2LoginView(OAuth2LoginView):
    def dispatch(self, request: WSGIRequest, *args, **kwargs):
        result = super().dispatch(request, *args, **kwargs)
        nonce = request.GET.get("nonce", None)
        callback_url = request.GET.get("callback_url", None)
        log.debug(f"Login called with nonce {wrap(nonce)} and callback {wrap(callback_url)}")
        if nonce:
            request.session["nonce"] = nonce
        if callback_url:
            if not nonce:
                raise BadRequestError("Can't have callback_url with no nonce")
            if not _is_authorized_callback(callback_url):
                raise BadRequestError(f"Unauthorized callback URL {callback_url}")
            request.session["callback_url"] = callback_url
        return result


class CustomOAuth2CallbackView(OAuth2CallbackView):
    def dispatch(self, request: WSGIRequest, *args, **kwargs):
        nonce = request.session.get("nonce", None)
        callback_url = request.session.get("callback_url", None)
        log.debug(f"Callback url is {wrap(callback_url)}")
        log.debug(f"Callback nonce is {wrap(nonce)}")
        result = super().dispatch(request, *args, **kwargs)
        if nonce:
            params = {"nonce": nonce}
            if callback_url:
                params["callback_url"] = callback_url
            encoded = urlencode(params)
            new_url = f"{result.url}?{encoded}"
            result["Location"] = new_url
        return result
