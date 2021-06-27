Changelog
=========

2.0.0 (2021-06-27)
------------------

**API Changes**

- Python 3.6 is the minimal support Python version.
- Support for Python 3.7 has been added.
- Support for Python 3.8 has been added.
- Support for Python 3.9 has been added.
- Support for Python 2.7 has been removed.
- Support for Python 3.3 has been removed.
- Support for Python 3.4 has been removed.
- Support for Python 3.5 has been removed.
- Support for PyPy (Python 2.7 compatible) has been removed.
- Add type hints throughout and support PEP 561 via a py.typed
  file. This should allow projects to type check their usage of this dependency.
- Throw ``TypeError`` when creating a priority tree with a ``maximum_streams``
  value that is not an integer.
- Throw ``ValueError`` when creating a priority tree with a ``maximum_streams``
  value that is not a positive integer.

1.3.0 (2017-01-27)
------------------

**API Changes**

- Throw ``PriorityLoop`` when inserting or reprioritising a stream that
  depends on itself.
- Throw ``BadWeightError`` when creating or reprioritising a stream with a
  weight that is not an integer between 1 and 256, inclusive.
- Throw ``PseudoStreamError`` when trying to reprioritise, remove, block or
  unblock stream 0.
- Add a new ``PriorityError`` parent class for the exceptions that can be
  thrown by priority.

1.2.2 (2016-11-11)
------------------

**Bugfixes**

- Allow ``insert_stream`` to be called with ``exclusive=True`` but no explicit
  ``depends_on`` value.

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
