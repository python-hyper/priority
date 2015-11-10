Priority: A HTTP/2 Priority Implementation
==========================================

Priority is a pure-Python implementation of the priority logic for HTTP/2, set
out in `RFC 7540 Section 5.3 (Stream Priority)`_. This logic allows for clients
to express a preference for how the server allocates its (limited) resources to
the many outstanding HTTP requests that may be running over a single HTTP/2
connection.

While priority information in HTTP/2 is only a suggestion, rather than an
enforceable constraint, where possible servers should respect the priority
requests of their clients.

Using Priority
--------------

Priority has a simple API. Streams are inserted into the tree: when they are
inserted, they may optionally have a weight, depend on another stream, or
become an exclusive dependent of another stream.

.. code-block:: python

    >>> p = priority.PriorityTree()
    >>> p.insert_stream(stream_id=1)
    >>> p.insert_stream(stream_id=3)
    >>> p.insert_stream(stream_id=5, depends_on=1)
    >>> p.insert_stream(stream_id=7, weight=32)
    >>> p.insert_stream(stream_id=9, depends_on=7, weight=8)
    >>> p.insert_stream(stream_id=11, depends_on=7, exclusive=True)

Once streams are inserted, the stream priorities can be requested. This allows
the server to make decisions about how to allocate resources.

Querying The Tree: Manual Walk
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Priority supports a number of methods of querying the priority tree. One way is
to manually walk the tree, starting from the level of highest priority.

.. code-block:: python

    >>> tree = p.priorities()
    >>> tree
    PrioritySet<total_weight=64, streams=[Stream<id=1, weight=16>, Stream<id=3, weight=16>, Stream<id=7, weight=32]>,

Currently, these streams are all the highest priority: they do not depend on
another stream, and so should be served first if resources are available. Of
these three streams, stream 7 should receive 1/2 of the resources available,
with streams 1 and 3 receiving 1/4 of the resources available each.

If for any reason a stream is blocked or cannot be served (e.g. because you
are waiting on I/O), you can allocate the resources that were intended for that
stream to its dependents. To do this, index into the ``PrioritySet`` by
stream ID. For example, if you were unable to serve stream 7:

.. code-block:: python

    >>> dependents = tree[7]
    >>> dependents
    PrioritySet<total_weight=16, streams=[Stream<id=11, weight=16>]>
    >>> second_level_dependents = dependents[11]
    >>> second_level_dependents
    PrioritySet<total_weight=8, streams=[Stream<id=9, weight=8>]>

Here, if stream 7 could not be served, all its resources should be diverted to
serving stream 11. If that were also unable to be served, we should instead
divert all the resources to stream 11.

Querying The Tree: Automated Resolution
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

An alternative approach is to inform Priority of what streams are blocked (or,
alternatively, which are unblocked), in which case Priority will return a list
of the streams that should be satisfied, and their weights.

.. code-block:: python

    >>> priorities = p.priorities(blocked=[1, 5, 7])
    >>> priorities
    PrioritySet<total_weight=48, streams=[Stream<id=3, weight=16>, Stream<id=11, weight=32>]>
    >>> p.priorities(blocked=[1, 5, 7]) == p.priorities(unblocked=[3, 9, 11])
    True


Querying The Tree: Gate
~~~~~~~~~~~~~~~~~~~~~~~

The Priority 'gate' is an alternative approach of accessing HTTP/2 priorities
based on `this presentation`_. It works by providing an iterator that acts as a
'gate'. Each value popped off the iterator is the next stream that should be
acted on. The PriorityTree can be mutated on the fly to add, remove, block, and
unblock streams, which affects what the next value from the iterator will be.

This works well when combined with some kind of signaling mechanism to block
and unblock threads of execution. This would allow you to do something like
this:

.. code-block:: python

    >>> for stream_id in p.gate():
    ...     unblock(stream_id)  # Sends a single DATA frame.

In this circumstance, each time a stream is unblocked it should send a single
DATA frame and then go back to waiting to be unblocked. This way we ensure that
the data from streams is correctly multiplexed.

You can also block and unblock streams in the iterator, like so:

For example:

.. code-block:: python

    >>> for stream_id in p.gate()
    ...    now_blocked = unblock(stream_id)
    ...    if now_blocked:
    ...        p.blocked(stream_id)
    ...    unblocked = all_unblocked_streams()
    ...    for unblocked_stream_id in unblocked:
    ...        p.unblock(unblocked_stream_id)


License
-------

Priority is made available under the MIT License. For more details, see the
LICENSE file in the repository.

Authors
-------

Priority is maintained by Cory Benfield, with contributions from others. For
more details about the contributors, please see CONTRIBUTORS.rst in the
repository.


.. _RFC 7540 Section 5.3 (Stream Priority): https://tools.ietf.org/html/rfc7540#section-5.3
.. _this presentation: http://example.com/
