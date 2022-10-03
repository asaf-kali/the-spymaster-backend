from django.test import TestCase, override_settings
from moto.dynamodb import mock_dynamodb

from api.logic.db import GameItem
from the_spymaster.config import get_config


@override_settings(DEBUG=True)
class SpymasterTest(TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        super().setUpClass()
        cls.config = get_config()
        cls.mock_dynamo = mock_dynamodb()
        cls.mock_dynamo.start()
        GameItem.create_table()

        from api.management.commands.dev_init import create_admin
        from api.models.user import SpymasterUser

        create_admin()
        cls.admin = SpymasterUser.objects.get(username="admin")

    @classmethod
    def tearDownClass(cls) -> None:
        cls.mock_dynamo.stop()
        super().tearDownClass()
