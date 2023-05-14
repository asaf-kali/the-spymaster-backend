from django.test import TestCase, override_settings
from moto.dynamodb import mock_dynamodb

from server.logic.db import GameItem
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

        from server.management.commands.dev_init import (  # pylint: disable=import-outside-toplevel
            create_admin,
        )
        from server.models.user import (  # pylint: disable=import-outside-toplevel
            SpymasterUser,
        )

        create_admin()
        cls.admin = SpymasterUser.objects.get(username="admin")

    @classmethod
    def tearDownClass(cls) -> None:
        cls.mock_dynamo.stop()
        super().tearDownClass()
