# !/usr/bin/python
# -*- coding:utf-8 -*-

# ***********************************************************************
# Author: Zhichang Fu
# Created Time: 2018-08-25 11:08:53
# Function:
#
# ***********************************************************************

import os
from .utils import (threadeddict)


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
        self.print_flag = params.get('debug', os.environ.get('debug', False))
        self.supports_multiple_insert = False

    def _getctx(self):
        if not self._ctx.get('db'):
            self._load_context(self._ctx)
        return self._ctx

    ctx = property(_getctx)

    def _load_context(self, ctx):
        ctx.dbq_count = 0
        ctx.transactions = []  # stack of transactions

        ctx.db = self._connect(self.keywords)
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
            a = time.time()
            query, params = self._process_query(sql_query)
            out = cur.execute(query, params)
            b = time.time()
        except:
            if self.printing:
                print('ERR:', str(sql_query), file=debug)
            if self.ctx.transactions:
                self.ctx.transactions[-1].rollback()
            else:
                self.ctx.rollback()
            raise

        if self.printing:
            print(
                '%s (%s): %s' % (round(b - a, 2), self.ctx.dbq_count,
                                 str(sql_query)),
                file=debug)
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
        super(DB, self).__init__(self, db, params)
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
