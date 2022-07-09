from rest_framework.test import APIClient

from api.tests.spymaster_test import SpymasterTest

API_V1 = "/api/v1"


class ApiTest(SpymasterTest):
    @classmethod
    def setUpClass(cls) -> None:
        super().setUpClass()
        cls.api_client = APIClient()
