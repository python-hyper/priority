# -*- coding: utf-8 -*-
"""
priority/tree
~~~~~~~~~~~~~

Implementation of the Priority tree data structure.
"""
from collections import Mapping


class Stream(object):
    """
    Priority information for a given stream.
    """
    def __init__(self, stream_id, weight=16):
        self.stream_id = stream_id
        self.weight = weight
        self.children = []

    # Custom repr
    def __repr__(self):
        return "Stream<id=%d, weight=%d>" % (self.stream_id, self.weight)


class Priorities(Mapping):
    """
    A set of objects that represent a current list of priorities. Can be
    indexed by stream ID, returning a
    :class:`Priorities <priority.priority.Priorities>` object for the streams
    dependent on the indexed one.

    :param streams: (optional) An iterable of
        :class:`Stream <priority.priority.Stream>` objects.
    """
    def __init__(self, streams=None):
        if streams is None:
            streams = []

        self._nodes = {node.stream_id: node for node in streams}
        self._total_weight = None

    @property
    def total_weight(self):
        """
        The total weight of all the streams at this priority level.
        """
        if self._total_weight is None:
            self._total_weight = sum(
                node.weight for node in self._nodes.values()
            )

        return self._total_weight

    def stream_weight(self, stream_id):
        return self._nodes[stream_id].weight

    # Abstract methods for Mapping
    def __getitem__(self, key):
        node = self._nodes[key]
        return self.__class__(node.children)

    def __iter__(self):
        for key in self._nodes:
            yield self[key]

    def __len__(self):
        return len(self._nodes)

    # Custom repr
    def __repr__(self):
        stream_reprs = ', '.join(
            repr(node) for node in self._nodes.values()
        )
        result = "Priorities<total_weight=%d, streams=[%s]>" % (
            self.total_weight,
            stream_reprs
        )
        return result


class PriorityTree(object):
    """
    A HTTP/2 Priority Tree.

    This tree stores HTTP/2 streams according to their HTTP/2 priorities.
    """
    def __init__(self):
        # This flat array keeps hold of all the streams that are logically
        # dependent on stream 0.
        self._top_level = []
        self._streams = {}

    def _exclusive_insert(self, parent_stream, inserted_stream):
        """
        Insert ``inserted_stream`` beneath ``parent_stream``, obeying the
        semantics of exclusive insertion.
        """
        old_children = parent_stream.children
        parent_stream.children = [inserted_stream]
        inserted_stream.children = old_children

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

        if depends_on:
            tree_level = self._streams[depends_on].children
        else:
            tree_level = self._top_level

        tree_level.append(stream)
        self._streams[stream_id] = stream

    def priorities(self, blocked=None, unblocked=None):
        """
        Return the prioritised streams.

        :param blocked: (optional) Currently does nothing.
        :param unblocked: (optional) Currently does nothing.
        """
        assert blocked is None
        assert unblocked is None

        return Priorities(self._top_level)
