# -*- coding: utf-8 -*-
"""
priority/tree
~~~~~~~~~~~~~

Implementation of the Priority tree data structure.
"""
from collections import Mapping, deque
from copy import copy

try:
    import Queue as queue
except ImportError:  # Python 3:
    import queue


class Stream(object):
    """
    Priority information for a given stream.
    """
    def __init__(self, stream_id, weight=16):
        self.stream_id = stream_id
        self.weight = weight
        self.children = []
        self.child_queue = queue.PriorityQueue()
        self.active = True
        self.last_weight = 0

    def add_child(self, child):
        """
        Add a stream that depends on this one.
        """
        self.children.append(child)
        self.child_queue.put((self.current_val, child))

    def add_child_exclusive(self, child):
        """
        Add a stream that exclusively depends on this one.
        """
        old_children = self.children
        self.children = [child]

        for old_child in old_children:
            child.add_child(old_child)

    def schedule(self):
        """
        Returns the stream ID of the next child to schedule.
        """
        # Cannot be called on active streams.
        assert not self.active

        level, child = self.child_queue.get()

        if child.active:
            next_stream = child.stream_id
        else:
            next_stream = child.schedule()

        new_level = level + child.weight
        self.child_queue.put((new_level, child))
        self.last_weight = new_level

        return next_stream

    # Custom repr
    def __repr__(self):
        return "Stream<id=%d, weight=%d>" % (self.stream_id, self.weight)

    # Custom equality
    def __eq__(self, other):
        if not isinstance(other, self.__class__):
            return False

        return (
            self.stream_id == other.stream_id and
            self.weight == other.weight and
            self.children == other.children
        )

    def __ne__(self, other):
        return not self.__eq__(other)



class PriorityTree(object):
    """
    A HTTP/2 Priority Tree.

    This tree stores HTTP/2 streams according to their HTTP/2 priorities.
    """
    def __init__(self):
        # This flat array keeps hold of all the streams that are logically
        # dependent on stream 0.
        self._root_stream = Stream(stream_id=0, weight=1)
        self._root_stream.active = False
        self._streams = {0: self._root_stream}

    def _exclusive_insert(self, parent_stream, inserted_stream):
        """
        Insert ``inserted_stream`` beneath ``parent_stream``, obeying the
        semantics of exclusive insertion.
        """
        parent_stream.add_child_exclusive(inserted_stream)

    def insert_stream(self,
                      stream_id,
                      depends_on=None,
                      weight=16,
                      exclusive=False):
        """
        Insert a stream into the tree.

        :param stream_id: The stream ID of the stream being inserted.
        :param depends_on: (optional) The ID of the stream that the new stream
            depends on, if any.
        :param weight: (optional) The weight to give the new stream. Defaults
            to 16.
        :param exclusive: (optional) Whether this new stream should be an
            exclusive dependency of the parent.
        """
        stream = Stream(stream_id, weight)

        if exclusive:
            assert depends_on is not None
            parent_stream = self._streams[depends_on]
            self._exclusive_insert(parent_stream, stream)
            return

        if not depends_on:
            depends_on = 0

        parent = self._streams[depends_on]
        parent.add_child(stream)
        self._streams[stream_id] = stream
