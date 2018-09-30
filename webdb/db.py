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
from .compat import string_types, numeric_types, PY2, iteritems

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


def sqllist(lst):
    """
    Converts the arguments for use in something like a WHERE clause.
    
        >>> sqllist(['a', 'b'])
        'a, b'
        >>> sqllist('a')
        'a'
    """
    if isinstance(lst, string_types):
        return lst
    else:
        return ', '.join(lst)


def sqlwhere(data, grouping=' AND '):
    """
    Converts a two-tuple (key, value) iterable `data` to an SQL WHERE clause `SQLQuery`.
    
        >>> sqlwhere((('cust_id', 2), ('order_id',3)))
        <sql: 'cust_id = 2 AND order_id = 3'>
        >>> sqlwhere((('order_id', 3), ('cust_id', 2)), grouping=', ')
        <sql: 'order_id = 3, cust_id = 2'>
        >>> sqlwhere((('a', 'a'), ('b', 'b'))).query()
        'a = %s AND b = %s'
    """

    return SQLQuery.join([k + ' = ' + sqlparam(v) for k, v in data], grouping)


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
        return (isinstance(other, _Node) and self.type == other.type
                and self.first == other.first and self.second == other.second)

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
        return SQLQuery.join([self.eval_node(node, mapping) for node in nodes],
                             "")

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
            return self.eval_expr(node.first, mapping)[self.eval_expr(
                node.second, mapping)]
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


class Transaction:
    """Database transaction."""

    def __init__(self, ctx):
        self.ctx = ctx
        self.transaction_count = transaction_count = len(ctx.transactions)

        class transaction_engine:
            """Transaction Engine used in top level transactions."""

            def do_transact(self):
                ctx.commit(unload=False)

            def do_commit(self):
                ctx.commit()

            def do_rollback(self):
                ctx.rollback()

        class subtransaction_engine:
            """Transaction Engine used in sub transactions."""

            def query(self, q):
                db_cursor = ctx.db.cursor()
                ctx.db_execute(db_cursor, SQLQuery(q % transaction_count))

            def do_transact(self):
                self.query('SAVEPOINT webpy_sp_%s')

            def do_commit(self):
                self.query('RELEASE SAVEPOINT webpy_sp_%s')

            def do_rollback(self):
                self.query('ROLLBACK TO SAVEPOINT webpy_sp_%s')

        class dummy_engine:
            """Transaction Engine used instead of subtransaction_engine 
            when sub transactions are not supported."""
            do_transact = do_commit = do_rollback = lambda self: None

        if self.transaction_count:
            # nested transactions are not supported in some databases
            if self.ctx.get('ignore_nested_transactions'):
                self.engine = dummy_engine()
            else:
                self.engine = subtransaction_engine()
        else:
            self.engine = transaction_engine()

        self.engine.do_transact()
        self.ctx.transactions.append(self)

    def __enter__(self):
        return self

    def __exit__(self, exctype, excvalue, traceback):
        if exctype is not None:
            self.rollback()
        else:
            self.commit()

    def commit(self):
        if len(self.ctx.transactions) > self.transaction_count:
            self.engine.do_commit()
            self.ctx.transactions = self.ctx.transactions[:self.
                                                          transaction_count]

    def rollback(self):
        if len(self.ctx.transactions) > self.transaction_count:
            self.engine.do_rollback()
            self.ctx.transactions = self.ctx.transactions[:self.
                                                          transaction_count]


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

    def _where(self, where, vars):
        if isinstance(where, numeric_types):
            where = "id = " + sqlparam(where)
        #@@@ for backward-compatibility
        elif isinstance(where, (list, tuple)) and len(where) == 2:
            where = SQLQuery(where[0], where[1])
        elif isinstance(where, dict):
            where = self._where_dict(where)
        elif isinstance(where, SQLQuery):
            pass
        else:
            where = reparam(where, vars)
        return where

    def _where_dict(self, where):
        where_clauses = []

        for k, v in sorted(iteritems(where), key=lambda t: t[0]):
            where_clauses.append(k + ' = ' + sqlquote(v))
        if where_clauses:
            return SQLQuery.join(where_clauses, " AND ")
        else:
            return None

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

    def select_v2(self, tables, fields=None):
        return Select(self, tables, fields)

    def select(self,
               tables,
               vars=None,
               what='*',
               where=None,
               order=None,
               group=None,
               limit=None,
               offset=None,
               _test=False):
        """
        Selects `what` from `tables` with clauses `where`, `order`, 
        `group`, `limit`, and `offset`. Uses vars to interpolate. 
        Otherwise, each clause can be a SQLQuery.
        
            >>> db = DB(None, {})
            >>> db.select('foo', _test=True)
            <sql: 'SELECT * FROM foo'>
            >>> db.select(['foo', 'bar'], where="foo.bar_id = bar.id", limit=5, _test=True)
            <sql: 'SELECT * FROM foo, bar WHERE foo.bar_id = bar.id LIMIT 5'>
            >>> db.select('foo', where={'id': 5}, _test=True)
            <sql: 'SELECT * FROM foo WHERE id = 5'>
        """
        if vars is None: vars = {}
        sql_clauses = self.sql_clauses(what, tables, where, group, order,
                                       limit, offset)
        clauses = [
            self.gen_clause(sql, val, vars) for sql, val in sql_clauses
            if val is not None
        ]
        qout = SQLQuery.join(clauses)
        if _test: return qout
        return self.query(qout, processed=True)

    def where(self,
              table,
              what='*',
              order=None,
              group=None,
              limit=None,
              offset=None,
              _test=False,
              **kwargs):
        """
        Selects from `table` where keys are equal to values in `kwargs`.
        
            >>> db = DB(None, {})
            >>> db.where('foo', bar_id=3, _test=True)
            <sql: 'SELECT * FROM foo WHERE bar_id = 3'>
            >>> db.where('foo', source=2, crust='dewey', _test=True)
            <sql: "SELECT * FROM foo WHERE crust = 'dewey' AND source = 2">
            >>> db.where('foo', _test=True)
            <sql: 'SELECT * FROM foo'>
        """
        where = self._where_dict(kwargs)
        return self.select(
            table,
            what=what,
            order=order,
            group=group,
            limit=limit,
            offset=offset,
            _test=_test,
            where=where)

    def sql_clauses(self, what, tables, where, group, order, limit, offset):
        return (
            ('SELECT', what),
            ('FROM', sqllist(tables)),
            ('WHERE', where),
            ('GROUP BY', group),
            ('ORDER BY', order),
            # The limit and offset could be the values provided by
            # the end-user and are potentially unsafe.
            # Using them as parameters to avoid any risk.
            ('LIMIT', limit and SQLParam(limit).sqlquery()),
            ('OFFSET', offset and SQLParam(offset).sqlquery()))

    def gen_clause(self, sql, val, vars):
        if isinstance(val, numeric_types):
            if sql == 'WHERE':
                nout = 'id = ' + sqlquote(val)
            else:
                nout = SQLQuery(val)
        #@@@
        elif isinstance(val, (list, tuple)) and len(val) == 2:
            nout = SQLQuery(val[0], val[1])  # backwards-compatibility
        elif sql == 'WHERE' and isinstance(val, dict):
            nout = self._where_dict(val)
        elif isinstance(val, SQLQuery):
            nout = val
        else:
            nout = reparam(val, vars)

        def xjoin(a, b):
            if a and b: return a + ' ' + b
            else: return a or b

        return xjoin(sql, nout)

    def insert(self, tablename, seqname=None, _test=False, **values):
        """
        Inserts `values` into `tablename`. Returns current sequence ID.
        Set `seqname` to the ID if it's not the default, or to `False`
        if there isn't one.
        
            >>> db = DB(None, {})
            >>> q = db.insert('foo', name='bob', age=2, created=SQLLiteral('NOW()'), _test=True)
            >>> q
            <sql: "INSERT INTO foo (age, created, name) VALUES (2, NOW(), 'bob')">
            >>> q.query()
            'INSERT INTO foo (age, created, name) VALUES (%s, NOW(), %s)'
            >>> q.values()
            [2, 'bob']
        """

        def q(x):
            return "(" + x + ")"

        if values:
            #needed for Py3 compatibility with the above doctests
            sorted_values = sorted(values.items(), key=lambda t: t[0])

            _keys = SQLQuery.join(map(lambda t: t[0], sorted_values), ', ')
            _values = SQLQuery.join(
                [sqlparam(v) for v in map(lambda t: t[1], sorted_values)],
                ', ')
            sql_query = "INSERT INTO %s " % tablename + q(
                _keys) + ' VALUES ' + q(_values)
        else:
            sql_query = SQLQuery(
                self._get_insert_default_values_query(tablename))

        if _test: return sql_query

        db_cursor = self._db_cursor()
        if seqname is not False:
            sql_query = self._process_insert_query(sql_query, tablename,
                                                   seqname)

        if isinstance(sql_query, tuple):
            # for some databases, a separate query has to be made to find
            # the id of the inserted row.
            q1, q2 = sql_query
            self._db_execute(db_cursor, q1)
            self._db_execute(db_cursor, q2)
        else:
            self._db_execute(db_cursor, sql_query)

        try:
            out = db_cursor.fetchone()[0]
        except Exception:
            out = None

        if not self.ctx.transactions:
            self.ctx.commit()

        return out

    def _get_insert_default_values_query(self, table):
        return "INSERT INTO %s DEFAULT VALUES" % table

    def multiple_insert(self, tablename, values, seqname=None, _test=False):
        """
        Inserts multiple rows into `tablename`. The `values` must be a list of dictioanries, 
        one for each row to be inserted, each with the same set of keys.
        Returns the list of ids of the inserted rows.        
        Set `seqname` to the ID if it's not the default, or to `False`
        if there isn't one.
        
            >>> db = DB(None, {})
            >>> db.supports_multiple_insert = True
            >>> values = [{"name": "foo", "email": "foo@example.com"}, {"name": "bar", "email": "bar@example.com"}]
            >>> db.multiple_insert('person', values=values, _test=True)
            <sql: "INSERT INTO person (email, name) VALUES ('foo@example.com', 'foo'), ('bar@example.com', 'bar')">
        """
        if not values:
            return []

        if not self.supports_multiple_insert:
            out = [
                self.insert(tablename, seqname=seqname, _test=_test, **v)
                for v in values
            ]
            if seqname is False:
                return None
            else:
                return out

        keys = values[0].keys()
        #@@ make sure all keys are valid

        for v in values:
            if v.keys() != keys:
                raise ValueError('Not all rows have the same keys')

        keys = sorted(
            keys
        )  #enforce query order for the above doctest compatibility with Py3

        sql_query = SQLQuery('INSERT INTO %s (%s) VALUES ' % (tablename,
                                                              ', '.join(keys)))

        for i, row in enumerate(values):
            if i != 0:
                sql_query.append(", ")
            SQLQuery.join(
                [SQLParam(row[k]) for k in keys],
                sep=", ",
                target=sql_query,
                prefix="(",
                suffix=")")

        if _test: return sql_query

        db_cursor = self._db_cursor()
        if seqname is not False:
            sql_query = self._process_insert_query(sql_query, tablename,
                                                   seqname)

        if isinstance(sql_query, tuple):
            # for some databases, a separate query has to be made to find
            # the id of the inserted row.
            q1, q2 = sql_query
            self._db_execute(db_cursor, q1)
            self._db_execute(db_cursor, q2)
        else:
            self._db_execute(db_cursor, sql_query)

        try:
            out = db_cursor.fetchone()[0]
            out = range(out - len(values) + 1, out + 1)
        except Exception:
            out = None

        if not self.ctx.transactions:
            self.ctx.commit()
        return out

    def update(self, tables, where, vars=None, _test=False, **values):
        """
        Update `tables` with clause `where` (interpolated using `vars`)
        and setting `values`.

            >>> db = DB(None, {})
            >>> name = 'Joseph'
            >>> q = db.update('foo', where='name = $name', name='bob', age=2,
            ...     created=SQLLiteral('NOW()'), vars=locals(), _test=True)
            >>> q
            <sql: "UPDATE foo SET age = 2, created = NOW(), name = 'bob' WHERE name = 'Joseph'">
            >>> q.query()
            'UPDATE foo SET age = %s, created = NOW(), name = %s WHERE name = %s'
            >>> q.values()
            [2, 'bob', 'Joseph']
        """
        if vars is None: vars = {}
        where = self._where(where, vars)

        values = sorted(values.items(), key=lambda t: t[0])

        query = ("UPDATE " + sqllist(tables) + " SET " +
                 sqlwhere(values, ', ') + " WHERE " + where)

        if _test: return query

        db_cursor = self._db_cursor()
        self._db_execute(db_cursor, query)
        if not self.ctx.transactions:
            self.ctx.commit()
        return db_cursor.rowcount

    def delete(self, table, where, using=None, vars=None, _test=False):
        """
        Deletes from `table` with clauses `where` and `using`.

            >>> db = DB(None, {})
            >>> name = 'Joe'
            >>> db.delete('foo', where='name = $name', vars=locals(), _test=True)
            <sql: "DELETE FROM foo WHERE name = 'Joe'">
        """
        if vars is None: vars = {}
        where = self._where(where, vars)

        q = 'DELETE FROM ' + table
        if using: q += ' USING ' + sqllist(using)
        if where: q += ' WHERE ' + where

        if _test: return q

        db_cursor = self._db_cursor()
        self._db_execute(db_cursor, q)
        if not self.ctx.transactions:
            self.ctx.commit()
        return db_cursor.rowcount

    def _process_insert_query(self, query, tablename, seqname):
        return query

    def transaction(self):
        """Start a transaction."""
        return Transaction(self.ctx)


class BaseWriteQuery(object):
    pass


class Insert(BaseWriteQuery):
    pass


class Update(BaseWriteQuery):
    pass


class MetaData(object):
    def __init__(self, database, tables, _test=False):
        self.database = database
        self._tables = tables
        self._where = None
        self._what = None
        self._group = None
        self._order = None
        self._limit = None
        self._offset = None
        self._test = _test

    def _sql_clauses(self, what, tables, where, group, order, limit, offset):
        return (
            ('SELECT', what),
            ('FROM', sqllist(tables)),
            ('WHERE', where),
            ('GROUP BY', group),
            ('ORDER BY', order),
            # The limit and offset could be the values provided by
            # the end-user and are potentially unsafe.
            # Using them as parameters to avoid any risk.
            ('LIMIT', limit and SQLParam(limit).sqlquery()),
            ('OFFSET', offset and SQLParam(offset).sqlquery()))

    def _where_dict(self, where, opt="="):
        where_clauses = []
        for k, v in sorted(iteritems(where), key=lambda t: t[0]):
            where_clauses.append(k + ' {} '.format(opt) + sqlquote(v))
        if where_clauses:
            return SQLQuery.join(where_clauses, " AND ")
        else:
            return None

    def _gen_clause(self, sql, val, vars=None):
        if isinstance(val, numeric_types):
            if sql == 'WHERE':
                nout = 'id = ' + sqlquote(val)
            else:
                nout = SQLQuery(val)
        #@@@
        elif isinstance(val, (list, tuple)) and len(val) == 2:
            nout = SQLQuery(val[0], val[1])  # backwards-compatibility
        elif sql == 'WHERE' and isinstance(val, dict):
            nout = self._where_dict(val)
        elif isinstance(val, SQLQuery):
            nout = val
        else:
            nout = reparam(val, vars)

        def xjoin(a, b):
            if a and b:
                return a + ' ' + b
            else:
                return a or b

        return xjoin(sql, nout)

    def _query(self, vars=None):
        sql_clauses = self._sql_clauses(self._what, self._tables, self._where,
                                        self._group, self._order, self._limit,
                                        self._offset)
        clauses = [
            self._gen_clause(sql, val, vars) for sql, val in sql_clauses
            if val is not None
        ]
        qout = SQLQuery.join(clauses)
        if self._test:
            return qout
        return self.database.query(qout, processed=True)

    def query(self):
        return self._query()

    def first(self):
        query_result = self._query()
        return query_result[0] if query_result else None

    def all(self):
        return self._query()

    def order_by(self, order_vars, _reversed=False):
        self._order = order_vars
        return self
        #self._order = "," .join(order_vars) if isinstance(order_vars, list) else order_vars

    def limit(self, num):
        self._limit = num
        return self

    def offset(self, num):
        self._offset = num
        return self


class Select(object):
    def __init__(self, database, tables, fields=None):
        self._metadata = MetaData(database, tables)
        self._metadata._what = self._what_fields(fields)

    def _opt_where(self, opt, **kwargs):
        opt_expression = self._metadata._where_dict(kwargs,
                                                    opt) if kwargs else ""
        if opt_expression:
            if self._metadata._where:
                self._metadata._where += " AND " + opt_expression
            else:
                self._metadata._where = opt_expression
        return self

    def _what_fields(self, fields=None):
        if fields and not isinstance(fields, list):
            raise "fields must be list object."
        return ", ".join(fields) if fields else "*"

    def filter_by(self, **kwargs):
        if not kwargs:
            return
        if "where" in kwargs and kwargs.get("where"):
            self._metadata._where = kwargs.get("where")
        else:
            self._metadata._where = kwargs
        return self._metadata

    def get(self, **kwargs):
        if kwargs:
            self._metadata._where = kwargs
        if "where" in kwargs and kwargs.get("where"):
            self._metadata._where = kwargs.get("where")
        return self._metadata._query()

    def all(self):
        return self._metadata._query()

    def count(self, distinct=None, **kwargs):
        if kwargs:
            self._metadata._where = kwargs
        count_str = "COUNT(DISTINCT {})".format(
            distinct) if distinct else "COUNT(*)"
        self._metadata._what = count_str + " AS COUNT"
        query_result = self._metadata._query()
        return query_result[0]["COUNT"]

    def filter(self, **kwargs):
        if kwargs:
            self._opt_where("=", **kwargs)
        return self._metadata

    def lt(self, **kwargs):
        return self._opt_where("<", **kwargs)

    def lte(self, **kwargs):
        return self._opt_where("<=", **kwargs)

    def gt(self, **kwargs):
        return self._opt_where(">", **kwargs)

    def gte(self, **kwargs):
        return self._opt_where(">=", **kwargs)

    def eq(self, **kwargs):
        return self._opt_where("=", **kwargs)

    def between(self, **kwargs):
        where_clauses = []
        for k, v in sorted(iteritems(kwargs), key=lambda t: t[0]):
            if not isinstance(v, list) and len(v) != 2:
                raise "between and param is wrong."
            where_clauses.append(k + " BETWEEN {} AND {} ".format(
                sqlquote(v[0]), sqlquote(v[1])))
        if not where_clauses:
            return self
        between_expression = SQLQuery.join(where_clauses, " AND ")
        if self._metadata._where:
            self._metadata._where += " AND " + between_expression
        else:
            self._metadata._where = between_expression
        return self


class Table(object):
    def __init__(self, database, table_name):
        self.ctx = database
        super(Table, self).__init__(table_name)

    def bind(self, database=None):
        self.ctx = database
        return self

    def insert(self, **kwargs):
        pass

    def insert_duplicate_update(self, data, conditions, **kwargs):
        pass

    def update(self, data, conditions, **kwargs):
        pass

    def select(self, **kwargs):
        pass


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

    def _process_insert_query(self, query, tablename, seqname):
        return query, SQLQuery('SELECT last_insert_id();')

    def _get_insert_default_values_query(self, table):
        return "INSERT INTO %s () VALUES()" % table


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
