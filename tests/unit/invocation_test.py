import unittest

from mock import MagicMock

from hazelcast.config import _Config
from hazelcast.errors import IndeterminateOperationStateError
from hazelcast.invocation import Invocation, InvocationService


class InvocationTest(unittest.TestCase):
    def setUp(self):
        self.service = None

    def tearDown(self):
        if self.service:
            self.service.shutdown()

    def _start_service(self, config=_Config()):
        c = MagicMock()
        invocation_service = InvocationService(c, config, c._reactor)
        self.service = invocation_service
        invocation_service.init(
            c._internal_partition_service, c._connection_manager, c._listener_service
        )
        invocation_service.start()
        invocation_service.add_backup_listener()
        return c, invocation_service
