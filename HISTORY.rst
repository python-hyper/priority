Changelog
=========

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
