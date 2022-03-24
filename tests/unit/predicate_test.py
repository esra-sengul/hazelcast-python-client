import unittest

from hazelcast.predicate import (
    sql,
    and_,
    equal,
    between,
    less_or_equal,
    like,
    ilike,
    in_,
    instance_of,
    not_equal,
    not_,
    or_,
    regex,
    true,
    false,
    paging,
)


class PredicateStrTest(unittest.TestCase):
    def test_sql(self):
        predicate = sql("this == 'value-1'")
        self.assertEqual(str(predicate), "SqlPredicate(sql='this == 'value-1'')")

    def test_and(self):
        predicate = and_(equal("this", "value-1"), equal("this", "value-2"))
        self.assertEqual(
            str(predicate),
            "AndPredicate(EqualPredicate(attribute='this', value=value-1),"
            " EqualPredicate(attribute='this', value=value-2))",
        )

    def test_paging(self):
        predicate = paging(true(), 5)
        self.assertEqual(
            str(predicate),
            "PagingPredicate(predicate=TruePredicate(), page_size=5, comparator=None)",
        )
