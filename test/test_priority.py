# -*- coding: utf-8 -*-
"""
test_priority
~~~~~~~~~~~~~

Tests for the Priority trees
"""
import itertools

from hypothesis import given
from hypothesis.strategies import integers, lists, tuples

import priority


STREAMS_AND_WEIGHTS = lists(
    elements=tuples(
        integers(min_value=1), integers(min_value=1, max_value=255)
    ),
    unique_by=lambda x: x[0],
)


class TestStream(object):
    def test_stream_repr(self):
        """
        The stream representation renders according to the README.
        """
        s = priority.Stream(stream_id=80, weight=16)
        assert repr(s) == "Stream<id=80, weight=16>"


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

    def test_priorities_repr(self, readme_tree):
        """
        The priorities representation renders according to the README.
        """
        priorities = readme_tree.priorities()
        r = repr(priorities)

        # Dictionaries hurt ordering, so just check all possible orderings.
        stream_reprs = [
            'Stream<id=1, weight=16>',
            'Stream<id=3, weight=16>',
            'Stream<id=7, weight=32>',
        ]
        possible_orderings = [
            ', '.join(permutation)
            for permutation in itertools.permutations(stream_reprs)
        ]
        base_repr = "Priorities<total_weight=64, streams=[%s]>"
        all_reprs = [
            base_repr % streams for streams in possible_orderings
        ]

        assert any(r == representation for representation in all_reprs)

    def test_drilling_down(self, readme_tree):
        """
        We can drill down each layer of the tree by stream ID.
        """
        top_level = readme_tree.priorities()
        assert 7 in top_level

        dependents = top_level[7]
        assert len(dependents) == 1
        assert 11 in dependents
        assert dependents.total_weight == 16

        second_level_dependents = dependents[11]
        assert len(second_level_dependents) == 1
        assert 9 in second_level_dependents
        assert second_level_dependents.total_weight == 8

    def test_automatic_resolution(self, readme_tree):
        """
        Implements the automatic resolution logic from the README.
        """
        priorities = readme_tree.priorities(blocked=[1, 5, 7])
        assert priorities.total_weight == 48
        assert len(priorities) == 2
        assert 3 in priorities
        assert 11 in priorities

        assert priorities.stream_weight(3) == 16
        assert priorities.stream_weight(11) == 32

    def test_automatic_resolution_blocked_unblock_match(self, readme_tree):
        """
        Tests that the automatic resolution logic correctly inverts the logic
        of blocked and unblocked so that they produce the same results.
        """
        blocked = readme_tree.priorities(blocked=[1, 5, 7])
        unblocked = readme_tree.priorities(unblocked=[3, 9, 11])

        assert blocked == unblocked
