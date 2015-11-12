# -*- coding: utf-8 -*-
"""
test_priority
~~~~~~~~~~~~~

Tests for the Priority trees
"""
from hypothesis import given
from hypothesis.strategies import integers, lists, tuples

import priority


STREAMS_AND_WEIGHTS = lists(
    elements=tuples(
        integers(min_value=1), integers(min_value=1, max_value=255)
    ),
    unique_by=lambda x: x[0],
)


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

    @given(STREAMS_AND_WEIGHTS)
    def test_priorities_stream_weights(self, stream_data):
        """
        For a given set of priorities, we can index by ID and find the weight
        of the stream.
        """
        p = priority.PriorityTree()

        for stream_id, weight in stream_data:
            p.insert_stream(stream_id=stream_id, weight=weight)

        priorities = p.priorities()

        for stream_id, weight in stream_data:
            assert weight == priorities.stream_weight(stream_id)
