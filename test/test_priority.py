# -*- coding: utf-8 -*-
"""
test_priority
~~~~~~~~~~~~~

Tests for the Priority trees
"""
from hypothesis import given
from hypothesis.strategies import integers, lists

import priority


class TestPriorityTree(object):
    def test_priority_tree_one_stream(self):
        """
        When only one stream is in the PriorityTree, priorities are easy.
        """
        p = priority.PriorityTree()
        p.insert_stream(stream_id=1)

        priorities = p.priorities()
        assert len(priorities) == 1
        priorities.total_weight == 16

    @given(lists(elements=integers(min_value=0)))
    def test_priority_tree_single_level(self, weights):
        """
        If lots of elements are added to the tree all at the top level, their
        weights are summed properly and the priorities object has the correct
        length.
        """
        p = priority.PriorityTree()
        stream_id = 1

        for weight in weights:
            p.insert_stream(stream_id=stream_id, weight=weight)
            stream_id += 1

        priorities = p.priorities()
        assert len(priorities) == len(weights)
        assert priorities.total_weight == sum(weights)
