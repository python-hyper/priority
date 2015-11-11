# -*- coding: utf-8 -*-
"""
test_priority
~~~~~~~~~~~~~

Tests for the Priority trees
"""
import priority


class TestPriorityTree(object):
    def test_priority_tree_one_stream(self):
        p = priority.PriorityTree()
        p.insert_stream(stream_id=1)

        priorities = p.priorities()
        assert len(priorities) == 1
        priorities.total_weight == 16
