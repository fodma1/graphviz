# tools.py

import os
import sys

from . import _compat

__all__ = ['attach', 'mkdirs', 'mapping_items']

PY2 = sys.version_info[0] == 2


def attach(object, name):
    """Return a decorator doing setattr(object, name) with its argument.

    >>> spam = type('Spam', (object,), {})()
    >>> @attach(spam, 'eggs')
    ... def func():
    ...     pass
    >>> spam.eggs  # doctest: +ELLIPSIS
    <function func at 0x...>
    """
    def decorator(func):
        setattr(object, name, func)
        return func
    return decorator


def mkdirs(filename, mode=0o777):
    """Recursively create directories up to the path of filename as needed."""
    dirname = os.path.dirname(filename)
    if not dirname:
        return
    _compat.makedirs(dirname, mode=mode, exist_ok=True)


def mapping_items(mapping, _iteritems=_compat.iteritems):
    """Return an iterator over the mapping items, sort if it's a plain dict.

    >>> list(mapping_items({'spam': 0, 'ham': 1, 'eggs': 2}))
    [('eggs', 2), ('ham', 1), ('spam', 0)]

    >>> from collections import OrderedDict
    >>> list(mapping_items(OrderedDict(enumerate(['spam', 'ham', 'eggs']))))
    [(0, 'spam'), (1, 'ham'), (2, 'eggs')]
    """
    if type(mapping) is dict:
        return iter(sorted(_iteritems(mapping)))
    return _iteritems(mapping)


def is_iterator(obj):
    """
    Check if the object is an iterator.
    For example, lists are considered iterators
    but not strings or datetime objects.
    Parameters
    ----------
    obj : The object to check.
    Returns
    -------
    is_iter : bool
        Whether `obj` is an iterator.
    Examples
    --------
    >>> is_iterator([1, 2, 3])
    True
    >>> is_iterator(datetime(2017, 1, 1))
    False
    >>> is_iterator("foo")
    False
    >>> is_iterator(1)
    False
    """

    if not hasattr(obj, '__iter__'):
        return False

    if PY2:
        return hasattr(obj, 'next')
    else:
        # Python 3 generators have
        # __next__ instead of next
        return hasattr(obj, '__next__')


def is_file_like(obj):
    """
    Check if the object is a file-like object.
    For objects to be considered file-like, they must
    be an iterator AND have either a `read` and/or `write`
    method as an attribute.
    Note: file-like objects must be iterable, but
    iterable objects need not be file-like.
    .. versionadded:: 0.20.0
    Parameters
    ----------
    obj : The object to check.
    Returns
    -------
    is_file_like : bool
        Whether `obj` has file-like properties.
    Examples
    --------
    >>> buffer(StringIO("data"))
    >>> is_file_like(buffer)
    True
    >>> is_file_like([1, 2, 3])
    False
    """

    if not (hasattr(obj, 'read') or hasattr(obj, 'write')):
        return False

    if not is_iterator(obj):
        return False

    return True
