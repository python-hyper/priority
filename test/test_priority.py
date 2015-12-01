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
