Changelog
=========

1.2.1 (2016-10-26)
------------------

**Bugfixes**

- Allow insertion of streams that have parents in the idle or closed states.
  This would previously raise a KeyError.

1.2.0 (2016-08-04)
------------------

**Security Fixes**

- CVE-2016-6580: All versions of this library prior to 1.2.0 are vulnerable to
  a denial of service attack whereby a remote peer can cause a user to insert
  an unbounded number of streams into the priority tree, eventually consuming
  all available memory.

  This version adds a ``TooManyStreamsError`` exception that is raised when
  too many streams are inserted into the priority tree. It also adds a keyword
  argument to the priority tree, ``maximum_streams``, which limits how many
  streams may be inserted. By default, this number is set to 1000.
  Implementations should strongly consider whether they can set this value
  lower.

1.1.1 (2016-05-28)
------------------

**Bugfixes**

- 2.5x performance improvement by swapping from ``queue.PriorityQueue`` to
  ``heapq``.

1.1.0 (2016-01-08)
------------------

**API Changes**

- Throw ``DuplicateStreamError`` when inserting a stream that is already in the
  tree.
- Throw ``MissingStreamError`` when reprioritising a stream that is not in the
  tree.

1.0.0 (2015-12-07)
------------------

- Initial release.
