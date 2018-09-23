# !/usr/bin/python
# -*- coding:utf-8 -*-

# ***********************************************************************
# Author: Zhichang Fu
# Created Time: 2018-08-25 11:08:53
# Function:
#
# ***********************************************************************

from __future__ import print_function
import os
import time
import datetime
import re
from .utils import (threadeddict, safestr, safeunicode, storage, iterbetter)
from .exception import UnknownParamstyle, _ItplError
from .compat import string_types, numeric_types, PY2

try:
    from urllib import parse as urlparse
    from urllib.parse import unquote
except ImportError:
    import urlparse
    from urllib import unquote

try:
    import ast
except ImportError:
    ast = None

TOKEN = '[ \\f\\t]*(\\\\\\r?\\n[ \\f\\t]*)*(#[^\\r\\n]*)?(((\\d+[jJ]|((\\d+\\.\\d*|\\.\\d+)([eE][-+]?\\d+)?|\\d+[eE][-+]?\\d+)[jJ])|((\\d+\\.\\d*|\\.\\d+)([eE][-+]?\\d+)?|\\d+[eE][-+]?\\d+)|(0[xX][\\da-fA-F]+[lL]?|0[bB][01]+[lL]?|(0[oO][0-7]+)|(0[0-7]*)[lL]?|[1-9]\\d*[lL]?))|((\\*\\*=?|>>=?|<<=?|<>|!=|//=?|[+\\-*/%&|^=<>]=?|~)|[][(){}]|(\\r?\\n|[:;.,`@]))|([uUbB]?[rR]?\'[^\\n\'\\\\]*(?:\\\\.[^\\n\'\\\\]*)*\'|[uUbB]?[rR]?"[^\\n"\\\\]*(?:\\\\.[^\\n"\\\\]*)*")|[a-zA-Z_]\\w*)'

tokenprog = re.compile(TOKEN)


def sqlify(obj):
    """
    converts `obj` to its proper SQL version

        >>> sqlify(None)
        'NULL'
        >>> sqlify(True)
        "'t'"
        >>> sqlify(3)
        '3'
    """
    # because `1 == True and hash(1) == hash(True)`
    # we have to do this the hard way...

    if obj is None:
        return 'NULL'
    elif obj is True:
        return "'t'"
    elif obj is False:
        return "'f'"
    elif isinstance(obj, numeric_types):
        return str(obj)
    elif isinstance(obj, datetime.datetime):
        return repr(obj.isoformat())
    else:
        if PY2 and isinstance(obj, unicode):
            # Strings are always UTF8 in Py3
            obj = obj.encode('utf8')

        return repr(obj)


class SQLParam(object):
    """
    Parameter in SQLQuery.
        >>> q = SQLQuery(["SELECT * FROM test WHERE name=", SQLParam("joe")])
        >>> q
        <sql: "SELECT * FROM test WHERE name='joe'">
        >>> q.query()
        'SELECT * FROM test WHERE name=%s'
        >>> q.values()
        ['joe']
    """
    __slots__ = ["value"]

    def __init__(self, value):
        self.value = value

    def get_marker(self, paramstyle='pyformat'):
        if paramstyle == 'qmark':
            return '?'
        elif paramstyle == 'numeric':
            return ':1'
        elif paramstyle is None or paramstyle in ['format', 'pyformat']:
            return '%s'
        raise UnknownParamstyle(paramstyle)

    def sqlquery(self):
        return SQLQuery([self])

    def __add__(self, other):
        return self.sqlquery() + other

    def __radd__(self, other):
        return other + self.sqlquery()

    def __str__(self):
        return str(self.value)

    def __eq__(self, other):
        return isinstance(other, SQLParam) and other.value == self.value

    def __repr__(self):
        return '<param: %s>' % repr(self.value)


sqlparam = SQLParam


class SQLQuery(object):
    """
    You can pass this sort of thing as a clause in any db function.
    Otherwise, you can pass a dictionary to the keyword argument `vars`
    and the function will call reparam for you.

    Internally, consists of `items`, which is a list of strings and
    SQLParams, which get concatenated to produce the actual query.
    """
    __slots__ = ["items"]

    # tested in sqlquote's docstring
    def __init__(self, items=None):
        """Creates a new SQLQuery.
            >>> SQLQuery("x")
            <sql: 'x'>
            >>> q = SQLQuery(['SELECT * FROM ', 'test', ' WHERE x=', SQLParam(1)])
            >>> q
            <sql: 'SELECT * FROM test WHERE x=1'>
            >>> q.query(), q.values()
            ('SELECT * FROM test WHERE x=%s', [1])
            >>> SQLQuery(SQLParam(1))
            <sql: '1'>
        """
        if items is None:
            self.items = []
        elif isinstance(items, list):
            self.items = items
        elif isinstance(items, SQLParam):
            self.items = [items]
        elif isinstance(items, SQLQuery):
            self.items = list(items.items)
        else:
            self.items = [items]

        # Take care of SQLLiterals
        for i, item in enumerate(self.items):
            if isinstance(item, SQLParam) and isinstance(
                    item.value, SQLLiteral):
                self.items[i] = item.value.v

    def append(self, value):
        self.items.append(value)

    def __add__(self, other):
        if isinstance(other, string_types):
            items = [other]
        elif isinstance(other, SQLQuery):
            items = other.items
        else:
            return NotImplemented
        return SQLQuery(self.items + items)

    def __radd__(self, other):
        if isinstance(other, string_types):
            items = [other]
        elif isinstance(other, SQLQuery):
            items = other.items
        else:
            return NotImplemented
        return SQLQuery(items + self.items)

    def __iadd__(self, other):
        if isinstance(other, (string_types, SQLParam)):
            self.items.append(other)
        elif isinstance(other, SQLQuery):
            self.items.extend(other.items)
        else:
            return NotImplemented
        return self

    def __len__(self):
        return len(self.query())

    def __eq__(self, other):
        return isinstance(other, SQLQuery) and other.items == self.items

    def query(self, paramstyle=None):
        """
        Returns the query part of the sql query.
            >>> q = SQLQuery(["SELECT * FROM test WHERE name=", SQLParam('joe')])
            >>> q.query()
            'SELECT * FROM test WHERE name=%s'
            >>> q.query(paramstyle='qmark')
            'SELECT * FROM test WHERE name=?'
        """
        s = []
        for x in self.items:
            if isinstance(x, SQLParam):
                x = x.get_marker(paramstyle)
                s.append(safestr(x))
            else:
                x = safestr(x)
                # automatically escape % characters in the query
                # For backward compatability, ignore escaping when the query looks already escaped
                if paramstyle in ['format', 'pyformat']:
                    if '%' in x and '%%' not in x:
                        x = x.replace('%', '%%')
                s.append(x)
        return "".join(s)

    def values(self):
        """
        Returns the values of the parameters used in the sql query.
            >>> q = SQLQuery(["SELECT * FROM test WHERE name=", SQLParam('joe')])
            >>> q.values()
            ['joe']
        """
        return [i.value for i in self.items if isinstance(i, SQLParam)]

    def join(items, sep=' ', prefix=None, suffix=None, target=None):
        """
        Joins multiple queries.

        >>> SQLQuery.join(['a', 'b'], ', ')
        <sql: 'a, b'>

        Optinally, prefix and suffix arguments can be provided.

        >>> SQLQuery.join(['a', 'b'], ', ', prefix='(', suffix=')')
        <sql: '(a, b)'>

        If target argument is provided, the items are appended to target instead of creating a new SQLQuery.
        """
        if target is None:
            target = SQLQuery()

        target_items = target.items

        if prefix:
            target_items.append(prefix)

        for i, item in enumerate(items):
            if i != 0 and sep != "":
                target_items.append(sep)
            if isinstance(item, SQLQuery):
                target_items.extend(item.items)
            elif item == "":  # joins with empty strings
                continue
            else:
                target_items.append(item)

        if suffix:
            target_items.append(suffix)
        return target

    join = staticmethod(join)

    def _str(self):
        try:
            return self.query() % tuple([sqlify(x) for x in self.values()])
        except (ValueError, TypeError):
            return self.query()

    def __str__(self):
        return safestr(self._str())

    def __unicode__(self):
        return safeunicode(self._str())

    def __repr__(self):
        return '<sql: %s>' % repr(str(self))


def sqlquote(a):
    """
    Ensures `a` is quoted properly for use in a SQL query.

        >>> 'WHERE x = ' + sqlquote(True) + ' AND y = ' + sqlquote(3)
        <sql: "WHERE x = 't' AND y = 3">
        >>> 'WHERE x = ' + sqlquote(True) + ' AND y IN ' + sqlquote([2, 3])
        <sql: "WHERE x = 't' AND y IN (2, 3)">
    """
    if isinstance(a, list):
        return _sqllist(a)
    else:
        return sqlparam(a).sqlquery()


class _Node(object):
    def __init__(self, type, first, second=None):
        self.type = type
        self.first = first
        self.second = second

    def __eq__(self, other):
        return (isinstance(other, _Node) and self.type == other.type and
                self.first == other.first and self.second == other.second)

    def __repr__(self):
        return "Node(%r, %r, %r)" % (self.type, self.first, self.second)


class Parser:
    """Parser to parse string templates like "Hello $name".

    Loosely based on <http://lfw.org/python/Itpl.py> (public domain, Ka-Ping Yee)
    """
    namechars = "abcdefghijklmnopqrstuvwxyz" \
            "ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789_"

    def __init__(self):
        self.reset()

    def reset(self):
        self.pos = 0
        self.level = 0
        self.text = ""
        self.format = ""

    def parse(self, text, _format="$"):
        """Parses the given text and returns a parse tree.
        """
        self.reset()
        self.text = text
        self._format = _format
        return self.parse_all()

    def parse_all(self):
        while True:
            dollar = self.text.find(self._format, self.pos)
            if dollar < 0:
                break
            nextchar = self.text[dollar + 1]
            if nextchar in self.namechars:
                yield _Node("text", self.text[self.pos:dollar])
                self.pos = dollar + 1
                yield self.parse_expr()

            # for supporting ${x.id}, for backward compataility
            elif nextchar == '{':
                saved_pos = self.pos
                self.pos = dollar + 2  # skip "${"
                expr = self.parse_expr()
                if self.text[self.pos] == '}':
                    self.pos += 1
                    yield _Node("text", self.text[self.pos:dollar])
                    yield expr
                else:
                    self.pos = saved_pos
                    break
            else:
                yield _Node("text", self.text[self.pos:dollar + 1])
                self.pos = dollar + 1
                # $$ is used to escape $
                if nextchar == self._format:
                    self.pos += 1

        if self.pos < len(self.text):
            yield _Node("text", self.text[self.pos:])

    def match(self):
        match = tokenprog.match(self.text, self.pos)
        if match is None:
            raise _ItplError(self.text, self.pos)
        return match, match.end()

    def is_literal(self, text):
        return text and text[0] in "0123456789\"'"

    def parse_expr(self):
        match, pos = self.match()
        if self.is_literal(match.group()):
            expr = _Node("literal", match.group())
        else:
            expr = _Node("param", self.text[self.pos:pos])
        self.pos = pos
        while self.pos < len(self.text):
            if self.text[self.pos] == "." and \
                self.pos + 1 < len(self.text) and \
               self.text[self.pos + 1] in self.namechars:
                self.pos += 1
                match, pos = self.match()
                attr = match.group()
                expr = _Node("getattr", expr, attr)
                self.pos = pos
            elif self.text[self.pos] == "[":
                saved_pos = self.pos
                self.pos += 1
                key = self.parse_expr()
                if self.text[self.pos] == ']':
                    self.pos += 1
                    expr = _Node("getitem", expr, key)
                else:
                    self.pos = saved_pos
                    break
            else:
                break
        return expr


class SafeEval(object):
    """Safe evaluator for binding params to db queries.
    """

    def safeeval(self, text, mapping):
        nodes = Parser().parse(text)
        return SQLQuery.join([self.eval_node(node, mapping)
                              for node in nodes], "")

    def eval_node(self, node, mapping):
        if node.type == "text":
            return node.first
        else:
            return sqlquote(self.eval_expr(node, mapping))

    def eval_expr(self, node, mapping):
        if node.type == "literal":
            return ast.literal_eval(node.first)
        elif node.type == "getattr":
            return getattr(self.eval_expr(node.first, mapping), node.second)
        elif node.type == "getitem":
            return self.eval_expr(
                node.first, mapping)[self.eval_expr(node.second, mapping)]
        elif node.type == "param":
            return mapping[node.first]


class SQLLiteral:
    """
    Protects a string from `sqlquote`.

        >>> sqlquote('NOW()')
        <sql: "'NOW()'">
        >>> sqlquote(SQLLiteral('NOW()'))
        <sql: 'NOW()'>
    """

    def __init__(self, v):
        self.v = v

    def __repr__(self):
        return "<literal: %r>" % self.v


sqlliteral = SQLLiteral


def _sqllist(values):
    """
        >>> _sqllist([1, 2, 3])
        <sql: '(1, 2, 3)'>
    """
    items = []
    items.append('(')
    for i, v in enumerate(values):
        if i != 0:
            items.append(', ')
        items.append(sqlparam(v))
    items.append(')')
    return SQLQuery(items)


def reparam(string_, dictionary):
    """
    Takes a string and a dictionary and interpolates the string
    using values from the dictionary. Returns an `SQLQuery` for the result.

        >>> reparam("s = $s", dict(s=True))
        <sql: "s = 't'">
        >>> reparam("s IN $s", dict(s=[1, 2]))
        <sql: 's IN (1, 2)'>
    """
    return SafeEval().safeeval(string_, dictionary)


class DB(object):
    """Database"""

    def __init__(self, db_module, params):
        """Create a database"""

        if 'driver' in params:
            params.pop('driver')
        self.db_module = db_module
        self.params = params

        self._ctx = threadeddict()
        # flag to enable/disable printing queries
        self.print_flag = False
        if "debug" in params:
            self.print_flag = params.get('debug')
            del params["debug"]
        else:
            self.print_flag = os.environ.get('debug', False)
        self.supports_multiple_insert = False

    def _getctx(self):
        if not self._ctx.get('db'):
            self._load_context(self._ctx)
        return self._ctx

    ctx = property(_getctx)

    def _load_context(self, ctx):
        ctx.dbq_count = 0
        ctx.transactions = []  # stack of transactions

        ctx.db = self._connect(self.params)
        ctx.db_execute = self._db_execute

        if not hasattr(ctx.db, 'commit'):
            ctx.db.commit = lambda: None

        if not hasattr(ctx.db, 'rollback'):
            ctx.db.rollback = lambda: None

        def commit():
            ctx.db.commit()

        def rollback():
            ctx.db.rollback()

        ctx.commit = commit
        ctx.rollback = rollback

    def _unload_context(self, ctx):
        del ctx.db

    def _connect(self, params):
        return self.db_module.connect(**params)

    def _db_cursor(self):
        return self.ctx.db.cursor()

    def _param_marker(self):
        """Returns parameter marker based on paramstyle attribute
        if this database."""
        style = getattr(self, 'paramstyle', 'pyformat')

        if style == 'qmark':
            return '?'
        elif style == 'numeric':
            return ':1'
        elif style in ['format', 'pyformat']:
            return '%s'
        raise UnknownParamstyle(style)

    def _db_execute(self, cur, sql_query):
        """executes an sql query"""
        self.ctx.dbq_count += 1

        try:
            start_time = time.time() * 1000
            run_time = lambda: "%.4f" % (time.time() * 1000 - start_time)
            query, params = self._process_query(sql_query)
            out = cur.execute(query, params)
        except:
            if self.print_flag:
                # print('ERR:', str(sql_query), file=debug)
                print('ERR:', str(sql_query))
            if self.ctx.transactions:
                self.ctx.transactions[-1].rollback()
            else:
                self.ctx.rollback()
            raise

        if self.print_flag:
            print("{} ({}): {}".format(run_time(), self.ctx.dbq_count,
                                       str(sql_query)))
        return out

    def _process_query(self, sql_query):
        """Takes the SQLQuery object and returns query string and parameters.
        """
        paramstyle = getattr(self, 'paramstyle', 'pyformat')
        query = sql_query.query(paramstyle)
        params = sql_query.values()
        return query, params

    def query(self, sql_query, vars=None, processed=False, _test=False):
        """
        Execute SQL query `sql_query` using dictionary `vars` to interpolate it.
        If `processed=True`, `vars` is a `reparam`-style list to use
        instead of interpolating.
            >>> db = DB(None, {})
            >>> db.query("SELECT * FROM foo", _test=True)
            <sql: 'SELECT * FROM foo'>
            >>> db.query("SELECT * FROM foo WHERE x = $x", vars=dict(x='f'), _test=True)
            <sql: "SELECT * FROM foo WHERE x = 'f'">
            >>> db.query("SELECT * FROM foo WHERE x = " + sqlquote('f'), _test=True)
            <sql: "SELECT * FROM foo WHERE x = 'f'">
        """
        if vars is None:
            vars = {}

        if not processed and not isinstance(sql_query, SQLQuery):
            sql_query = reparam(sql_query, vars)

        if _test:
            return sql_query

        db_cursor = self._db_cursor()
        self._db_execute(db_cursor, sql_query)

        if db_cursor.description:
            names = [x[0] for x in db_cursor.description]

            def iterwrapper():
                row = db_cursor.fetchone()
                while row:
                    yield storage(dict(zip(names, row)))
                    row = db_cursor.fetchone()

            out = iterbetter(iterwrapper())
            out.__len__ = lambda: int(db_cursor.rowcount)
            out.list = lambda: [storage(dict(zip(names, x)))
                                for x in db_cursor.fetchall()]
        else:
            out = db_cursor.rowcount

        if not self.ctx.transactions:
            self.ctx.commit()
        return out


class MySQLDB(DB):
    """MySQLDB"""

    def __init__(self, **params):
        db = import_driver(
            ["MySQLdb", "pymysql", "mysql.connector"],
            preferred=params.pop('driver', None))
        if db.__name__ == "pymysql" or db.__name__ == "mysql.connector":
            if 'passwd' in params:
                params['password'] = params['passwd']
                del params['passwd']
        if 'charset' not in params:
            params['charset'] = 'utf8'
        elif params['charset'] is None:
            del params['charset']

        self.paramstyle = db.paramstyle = 'pyformat'  # it's both, like psycopg
        self.dbname = "mysql"
        DB.__init__(self, db, params)
        self.supports_multiple_insert = True

    #def _process_insert_query(self, query, tablename, seqname):
    #    return query, SQLQuery('SELECT last_insert_id();')

    #def _get_insert_default_values_query(self, table):
    #    return "INSERT INTO %s () VALUES()" % table


def import_driver(drivers, preferred=None):
    """Import the first available driver or preferred driver.
    """
    if preferred:
        drivers = [preferred]

    for d in drivers:
        try:
            return __import__(d, None, None, ['x'])
        except ImportError:
            pass
    raise ImportError("Unable to import " + " or ".join(drivers))
