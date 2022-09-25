from django.test import TestCase, override_settings

from api.management.commands.dev_init import create_admin
from api.models.user import SpymasterUser


class SpymasterTest(TestCase):
    @classmethod
    @override_settings(DEBUG=True)
    def setUpClass(cls) -> None:
        super().setUpClass()
        create_admin()
        cls.admin = SpymasterUser.objects.get(username="admin")
