# -*- coding: utf-8 -*-
"""
priority/tree
~~~~~~~~~~~~~

Implementation of the Priority tree data structure.
"""
from __future__ import division

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
        self.parent = None
        self.child_queue = queue.PriorityQueue()
        self.active = True
        self.last_weight = 0

    def add_child(self, child):
        """
        Add a stream that depends on this one.
        """
        child.parent = self
        self.children.append(child)
        self.child_queue.put((self.last_weight, child))

    def add_child_exclusive(self, child):
        """
        Add a stream that exclusively depends on this one.
        """
        old_children = self.children
        self.children = []
        self.child_queue = queue.PriorityQueue()
        self.last_weight = 0
        self.add_child(child)

        for old_child in old_children:
            child.add_child(old_child)

    def remove_child(self, child):
        """
        Removes a child stream from this stream. This is a potentially somewhat
        expensive operation.
        """
        # To do this we do the following:
        #
        # - remove the child stream from the list of children
        # - build a new priority queue, filtering out the child when we find
        #   it in the old one
        self.children.remove(child)

        new_queue = queue.PriorityQueue()

        while not self.child_queue.empty():
            level, stream = self.child_queue.get()
            if stream == child:
                continue

            new_queue.put((level, stream))

        self.child_queue = new_queue

    def schedule(self):
        """
        Returns the stream ID of the next child to schedule. Potentially
        recurses down the tree of priorities.
        """
        # Cannot be called on active streams.
        assert not self.active

        level, child = self.child_queue.get()

        if child.active:
            next_stream = child.stream_id
        else:
            next_stream = child.schedule()

        self.last_weight = level

        level += (256 // child.weight)
        self.child_queue.put((level, child))

        return next_stream

    # Custom repr
    def __repr__(self):
        return "Stream<id=%d, weight=%d>" % (self.stream_id, self.weight)

    # Custom comparison
    def __eq__(self, other):
        if not isinstance(other, Stream):
            raise TypeError("Streams can only be equal to other streams")

        return self.stream_id == other.stream_id

    def __ne__(self, other):
        return not self.__eq__(other)

    def __lt__(self, other):
        if not isinstance(other, Stream):
            return NotImplemented

        return self.stream_id < other.stream_id

    def __le__(self, other):
        if not isinstance(other, Stream):
            return NotImplemented

        return self.stream_id <= other.stream_id

    def __gt__(self, other):
        if not isinstance(other, Stream):
            return NotImplemented

        return self.stream_id > other.stream_id

    def __ge__(self, other):
        if not isinstance(other, Stream):
            return NotImplemented

        return self.stream_id >= other.stream_id


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
        assert stream_id not in self._streams
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

    def remove_stream(self, stream_id):
        """
        Removes a stream from the priority tree.
        """
        # TODO: At some point we should actually prune streams we no longer
        # need. For now, just mark it permanently blocked.
        self._streams[stream_id].active = False

    def block(self, stream_id):
        """
        Marks a given stream as blocked, with no data to send.
        """
        self._streams[stream_id].active = False

    def unblock(self, stream_id):
        """
        Marks a given stream as unblocked, with more data to send.
        """
        self._streams[stream_id].active = True

    # The iterator protocol
    def __iter__(self):
        return self

    def __next__(self):
        return self._root_stream.schedule()

    def next(self):
        return self.__next__()
