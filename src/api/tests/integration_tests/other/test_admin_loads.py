import logging
from typing import Callable

from django.contrib import admin
from django.test import Client
from django.urls import URLPattern, reverse
from parameterized import param, parameterized
from rest_framework import status

from api.management.commands.dev_init import DEFAULT_PASSWORD
from api.tests.spymaster_test import SpymasterTest

log = logging.getLogger(__name__)


def get_model_page_load_test_name(func: Callable, _, params: param):
    suffix = parameterized.to_safe_name("_".join(str(x) for x in params.args))
    return f"{func.__name__}{suffix}"


class TestAdminLoads(SpymasterTest):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.client = Client()
        login_url = reverse("admin:login")
        response = cls.client.post(login_url, data={"username": "admin", "password": DEFAULT_PASSWORD})
        cls.cookies = response.cookies

    @parameterized.expand(
        [(reg,) for reg in admin.site._registry.values()],  # pylint: disable=protected-access
        name_func=get_model_page_load_test_name,
    )
    def test_all_model_page_load(self, admin_page):
        pattern: URLPattern = admin_page.urls[0]
        url = reverse(f"admin:{pattern.name}")
        log.debug(f"Getting {url}")
        self.client.cookies.update(self.cookies)
        response = self.client.get(url)
        assert response.status_code == status.HTTP_200_OK
