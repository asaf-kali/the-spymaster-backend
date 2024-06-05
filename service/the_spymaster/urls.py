"""p2print URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

from django.contrib import admin
from django.core.handlers.wsgi import WSGIRequest
from django.http import JsonResponse
from django.urls import include, path, re_path

from server.views import icon_view


def echo_stage(request: WSGIRequest, stage: str):  # pylint: disable=unused-argument
    return JsonResponse({"stage": stage})


urlpatterns = [
    path("", include("server.urls")),
    path("admin/", admin.site.urls),
    path("rest-auth/", include("dj_rest_auth.urls")),
    # path("accounts/", include("allauth.urls")),
    re_path(r"^favicon(\.ico)?$", icon_view),
    re_path(r"^(?P<stage>\w+)/$", echo_stage),
]
