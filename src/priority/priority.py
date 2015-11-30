# -*- coding: utf-8 -*-
"""
priority/tree
~~~~~~~~~~~~~

Implementation of the Priority tree data structure.
"""
from collections import Mapping, deque
from copy import copy


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

    def __eq__(self, other):
        if not isinstance(other, self.__class__):
            return False

        return self._nodes == other._nodes

    def __ne__(self, other):
        return not self.__eq__(other)

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
        Return the prioritised streams. Only one of ``blocked`` and
        ``unblocked`` can be used at any one time.

        :param blocked: An iterable of stream IDs that are blocked. All other
            stream IDs are assumed to be unblocked.
        :param unblocked: An iterable of stream IDs that are unblocked. All
            toehr stream IDs are assumed to be blocked.
        """
        if (blocked is None) and (unblocked is None):
            # Fast return path for the common case.
            return Priorities(self._top_level)

        if blocked is not None and unblocked is not None:
            raise ValueError("Must provide only one of blocked and unblocked")

        if unblocked is not None:
            unblocked = set(unblocked)
            all_stream_ids = set(self._streams.keys())
            blocked = all_stream_ids - unblocked

        assert blocked is not None

        return Priorities(self._walk(blocked))

    def _walk(self, stream_filter):
        """
        Walk the tree, yielding the streams that are currently prioritised,
        accounting for blocked streams.

        :param stream_filter: A set of stream IDs to be filtered out.
        :type stream_filter: `set`
        """
        # Let's explain the algorithm we use here.
        #
        # Starting with the top level of the tree, we want to build up a list
        # of all the streams and their eventual *effective* weight. The
        # *effective* weight of a stream is based on the relative weight of the
        # stream and the effective weight of its parent. The relative weight of
        # a stream is:
        #
        # (weight of current stream / total weight of level) * weight of parent
        #
        # where the 'total weight of level' is the sum of the weights of all
        # siblings with the same parent.
        #
        # We build up a list of tuples of 'possible stream IDs' and their
        # effective weights. Then, for each stream in the list, we check
        # whether it's in the stream_filter. If it isn't, we yield it.
        #
        # If it *is* in the stream_filter, we grab its children and calculate
        # their effective weights, and then place them on the list of streams
        # to examine. When we've run out of streams to examine, that's it: we
        # have our final list of streams and their effective weights.
        def level_weight(streams):
            return sum(s.weight for s in streams)

        def effective_stream_weight(weight,
                                    total_sibling_weight,
                                    parent_weight):
            fractional_weight = weight / total_sibling_weight
            return fractional_weight * parent_weight

        # Populate the original level.
        possible_streams = deque((s, s.weight) for s in self._top_level)

        while possible_streams:
            stream, effective_weight = possible_streams.popleft()

            if stream.stream_id in stream_filter:
                total_weight = level_weight(stream.children)
                possible_streams.extend(
                    (
                        c,
                        effective_stream_weight(c.weight,
                                                total_weight,
                                                stream.weight)
                    )
                    for c in stream.children
                )
            else:
                s = copy(stream)
                s.weight = effective_weight
                yield s
