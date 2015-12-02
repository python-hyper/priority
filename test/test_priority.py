# -*- coding: utf-8 -*-
"""
test_priority
~~~~~~~~~~~~~

Tests for the Priority trees
"""
from __future__ import division

import itertools

from hypothesis import given
from hypothesis.strategies import integers, lists, tuples

import priority

try:
    from functools import reduce
except ImportError:
    pass

try:
    from math import gcd
except ImportError:
    from fractions import gcd


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


class TestPriorityTreeOutput(object):
    """
    These tests use Hypothesis to attempt to bound the output of iterating over
    the priority tree. In particular, their goal is to ensure that the output
    of the tree is "good enough": that it meets certain requirements on
    fairness and equidistribution.
    """
    @given(STREAMS_AND_WEIGHTS)
    def test_period_of_repetition(self, streams_and_weights):
        """
        The period of repetition of a priority sequence is given by the sum of
        the weights of the streams. Once that many values have been pulled out
        the sequence repeats identically.
        """
        p = priority.PriorityTree()
        weights = []

        for stream, weight in streams_and_weights:
            p.insert_stream(stream_id=stream, weight=weight)
            weights.append(weight)

        period = sum(weights)

        # Pop off the first n elements, which will always be evenly
        # distributed.
        print(streams_and_weights)
        for _ in weights:
            print("    " + str(next(p)))

        pattern = [next(p) for _ in range(period)]
        print("    " + str(pattern))
        pattern = itertools.cycle(pattern)

        for i in range(period * 20):
            assert next(p) == next(pattern), i
