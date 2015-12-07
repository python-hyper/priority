Priority: A pure-Python HTTP/2 Priority implementation
======================================================

Priority is a pure-Python implementation of the priority logic for HTTP/2, set
out in `RFC 7540 Section 5.3 (Stream Priority)`_. This logic allows for clients
to express a preference for how the server allocates its (limited) resources to
the many outstanding HTTP requests that may be running over a single HTTP/2
connection.

Specifically, this Python implementation uses a variant of the implementation
used in the excellent `H2O`_ project. This original implementation is also the
inspiration for `nghttp2's`_ priority implementation, and generally produces a
very clean and even priority stream. The only notable changes from H2O's
implementation are small modifications to allow the priority implementation to
work cleanly as a separate implementation, rather than being embedded in a
HTTP/2 stack directly.

Contents:

.. toctree::
   :maxdepth: 2

   installation
   using-priority
   api
   license
   authors


.. _RFC 7540 Section 5.3 (Stream Priority): https://tools.ietf.org/html/rfc7540#section-5.3
.. _nghttp2's: https://nghttp2.org/blog/2015/11/11/stream-scheduling-utilizing-http2-priority/
.. _H2O: https://h2o.examp1e.net/
