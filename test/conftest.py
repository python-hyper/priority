# -*- coding: utf-8 -*-
"""
conftest
~~~~~~~~

Py.test fixtures for testing Priority.
"""
import pytest

import priority


@pytest.fixture
def readme_tree():
    """
    Provide a tree configured as the one in the readme.
    """
    p = priority.PriorityTree()
    p.insert_stream(stream_id=1)
    p.insert_stream(stream_id=3)
    p.insert_stream(stream_id=5, depends_on=1)
    p.insert_stream(stream_id=7, weight=32)
    p.insert_stream(stream_id=9, depends_on=7, weight=8)
    p.insert_stream(stream_id=11, depends_on=7, exclusive=True)
    return p
