import unittest

from hazelcast.util import RandomLB, RoundRobinLB


class _MockClusterService:
    def __init__(self, members):
        self._members = members

    def add_listener(self, listener, *_):
        for m in self._members:
            listener(m)

    def get_members(self):
        return self._members


class LoadBalancersTest(unittest.TestCase):
    def test_random_lb_with_no_members(self):
        cluster = _MockClusterService([])
        lb = RandomLB()
        lb.init(cluster)
        self.assertIsNone(lb.next())
