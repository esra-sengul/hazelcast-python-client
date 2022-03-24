import unittest

from hazelcast.core import AddressHelper


class AddressHelperTest(unittest.TestCase):
    v4_address = "127.0.0.1"
    v6_address = "2001:0db8:85a3:0000:0000:8a2e:0370:7334"
    localhost = "localhost"
    port = 8080
    default_port = 5701
    default_port_count = 3

    def _validate_without_port(self, address, host):
        primaries, secondaries = AddressHelper.get_possible_addresses(address)
        self.assertEqual(1, len(primaries))
        self.assertEqual(self.default_port_count - 1, len(secondaries))

        for i in range(self.default_port_count):
            if i == 0:
                address = primaries[i]
            else:
                address = secondaries[i - 1]
            self.assertEqual(host, address.host)
            self.assertEqual(self.default_port + i, address.port)
