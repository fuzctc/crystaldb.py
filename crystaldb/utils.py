# !/usr/bin/python
# -*- coding:utf-8 -*-

# ***********************************************************************
# Author: Zhichang Fu
# Created Time: 2018-08-25 16:01:39
# ***********************************************************************

from threading import local as threadlocal
from .compat import (iteritems, iterkeys, itervalues, is_iter, imap, PY2,
                     text_type)


def safeunicode(obj, encoding='utf-8'):
    """
    Converts any given object to unicode string.

        >>> safeunicode('hello')
        u'hello'
        >>> safeunicode(2)
        u'2'
        >>> safeunicode('\xe1\x88\xb4')
        u'\u1234'
    """
    t = type(obj)
    if t is text_type:
        return obj
    elif t is bytes:
        return obj.decode(encoding)
    elif t in [int, float, bool]:
        return unicode(obj)
    else:
        return unicode(obj)


def safestr(obj, encoding='utf-8'):
    """
    Converts any given object to utf-8 encoded string.

        >>> safestr('hello')
        'hello'
        >>> safestr(2)
        '2'
    """
    if PY2 and isinstance(obj, unicode):
        return obj.encode(encoding)
    elif is_iter(obj):
        return imap(safestr, obj)
    else:
        return str(obj)


class ThreadedDict(threadlocal):
    """
    Thread local storage.
        >>> d = ThreadedDict()
        >>> d.x = 1
        >>> d.x
        1
        >>> import threading
        >>> def f(): d.x = 2
        ...
        >>> t = threading.Thread(target=f)
        >>> t.start()
        >>> t.join()
        >>> d.x
        1
    """
    _instances = set()

    def __init__(self):
        ThreadedDict._instances.add(self)

    def __del__(self):
        ThreadedDict._instances.remove(self)

    def __hash__(self):
        return id(self)

    def clear_all():
        """Clears all ThreadedDict instances.
        """
        for t in list(ThreadedDict._instances):
            t.clear()

    clear_all = staticmethod(clear_all)

    # Define all these methods to more or less fully emulate dict -- attribute access
    # is built into threading.local.

    def __getitem__(self, key):
        return self.__dict__[key]

    def __setitem__(self, key, value):
        self.__dict__[key] = value

    def __delitem__(self, key):
        del self.__dict__[key]

    def __contains__(self, key):
        return key in self.__dict__

    has_key = __contains__

    def clear(self):
        self.__dict__.clear()

    def copy(self):
        return self.__dict__.copy()

    def get(self, key, default=None):
        return self.__dict__.get(key, default)

    def items(self):
        return self.__dict__.items()

    def iteritems(self):
        return iteritems(self.__dict__)

    def keys(self):
        return self.__dict__.keys()

    def iterkeys(self):
        return iterkeys(self.__dict__)

    iter = iterkeys

    def values(self):
        return self.__dict__.values()

    def itervalues(self):
        return itervalues(self.__dict__)

    def pop(self, key, *args):
        return self.__dict__.pop(key, *args)

    def popitem(self):
        return self.__dict__.popitem()

    def setdefault(self, key, default=None):
        return self.__dict__.setdefault(key, default)

    def update(self, *args, **kwargs):
        self.__dict__.update(*args, **kwargs)

    def __repr__(self):
        return '<ThreadedDict %r>' % self.__dict__

    __str__ = __repr__


threadeddict = ThreadedDict


class Storage(dict):
    """
    A Storage object is like a dictionary except `obj.foo` can be used
    in addition to `obj['foo']`.

        >>> o = storage(a=1)
        >>> o.a
        1
        >>> o['a']
        1
        >>> o.a = 2
        >>> o['a']
        2
        >>> del o.a
        >>> o.a
        Traceback (most recent call last):
            ...
        AttributeError: 'a'

    """

    def __getattr__(self, key):
        try:
            return self[key]
        except KeyError as k:
            raise AttributeError(k)

    def __setattr__(self, key, value):
        self[key] = value

    def __delattr__(self, key):
        try:
            del self[key]
        except KeyError as k:
            raise AttributeError(k)

    def __repr__(self):
        return '<Storage ' + dict.__repr__(self) + '>'


storage = Storage


class IterBetter:
    """
    Returns an object that can be used as an iterator
    but can also be used via __getitem__ (although it
    cannot go backwards -- that is, you cannot request
    `iterbetter[0]` after requesting `iterbetter[1]`).

        >>> import itertools
        >>> c = iterbetter(itertools.count())
        >>> c[1]
        1
        >>> c[5]
        5
        >>> c[3]
        Traceback (most recent call last):
            ...
        IndexError: already passed 3

    It is also possible to get the first value of the iterator or None.

        >>> c = iterbetter(iter([3, 4, 5]))
        >>> print(c.first())
        3
        >>> c = iterbetter(iter([]))
        >>> print(c.first())
        None

    For boolean test, IterBetter peeps at first value in the itertor without effecting the iteration.

        >>> c = iterbetter(iter(range(5)))
        >>> bool(c)
        True
        >>> list(c)
        [0, 1, 2, 3, 4]
        >>> c = iterbetter(iter([]))
        >>> bool(c)
        False
        >>> list(c)
        []
    """

    def __init__(self, iterator):
        self.i, self.c = iterator, 0

    def first(self, default=None):
        """Returns the first element of the iterator or None when there are no
        elements.

        If the optional argument default is specified, that is returned instead
        of None when there are no elements.
        """
        try:
            return next(iter(self))
        except StopIteration:
            return default

    def __iter__(self):
        if hasattr(self, "_head"):
            yield self._head
        while 1:
            yield next(self.i)
            self.c += 1

    def __getitem__(self, i):
        # todo: slices
        if i < self.c:
            raise IndexError("already passed " + str(i))
        try:
            while i > self.c:
                next(self.i)
                self.c += 1
            # now self.c == i
            self.c += 1
            return next(self.i)
        except StopIteration:
            raise IndexError(str(i))

    def __nonzero__(self):
        if hasattr(self, "__len__"):
            return self.__len__() != 0
        elif hasattr(self, "_head"):
            return True
        else:
            try:
                self._head = next(self.i)
            except StopIteration:
                return False
            else:
                return True

    __bool__ = __nonzero__


iterbetter = IterBetter
