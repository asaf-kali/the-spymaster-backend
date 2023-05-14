from django.test import Client
from django.urls import reverse
from rest_framework import status

from server.tests.spymaster_test import SpymasterTest


class TestIndexLoads(SpymasterTest):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.client = Client()

    def test_index_loads(self):
        url = reverse("index")
        response = self.client.get(url)
        assert response.status_code == status.HTTP_200_OK
