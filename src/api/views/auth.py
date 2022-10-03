import logging

from allauth.socialaccount.providers.google.views import GoogleOAuth2Adapter
from dj_rest_auth.views import LogoutView as RestAuthLogoutView
from django.conf import settings
from django.core.handlers.wsgi import WSGIRequest
from django.http import JsonResponse
from django.shortcuts import redirect
from django.urls import reverse
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.generics import RetrieveAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from rest_framework.viewsets import GenericViewSet
from the_spymaster_util.logging import wrap

from api.serializers import UserDetailsSerializer, UserSummarizeSerializer
from api.views.social_hooks import (
    CustomOAuth2CallbackView,
    CustomOAuth2LoginView,
    _generate_key_response,
)

log = logging.getLogger(__name__)


class LoginCallbackView(RetrieveAPIView):
    def get(self, request: WSGIRequest, **kwargs):
        log.debug(f"Login callback called for user {wrap(request.user)}")
        return _generate_key_response(self.request)


class LogoutView(RestAuthLogoutView):
    def logout(self, request):
        response = super().logout(request)
        if response.status_code == status.HTTP_200_OK:
            response = redirect(reverse(settings.LOGOUT_REDIRECT_URL))
        return response


class UserDetailsView(GenericViewSet):
    serializer_class = UserSummarizeSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = None

    @action(detail=False)
    def me(self, request: Request, *args, **kwargs):  # noqa: W0613
        return JsonResponse(data=UserDetailsSerializer(request.user).data, status=status.HTTP_200_OK)


oauth2_login = CustomOAuth2LoginView.adapter_view(GoogleOAuth2Adapter)
oauth2_callback = CustomOAuth2CallbackView.adapter_view(GoogleOAuth2Adapter)
