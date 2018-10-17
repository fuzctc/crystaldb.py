# !/usr/bin/python
# -*- coding:utf-8 -*-

# ***********************************************************************
# Author: Zhichang Fu
# Created Time: 2018-08-25 10:43:22
# Last Update: 2018-08-25 10:43:22
# ***********************************************************************

import os
try:
    from urllib.parse import urlparse, unquote
except ImportError:
    import urlparse
    from urllib import unquote

from .exception import UnknownDB
from .db import MySQLDB
from .db import Table

__version__ = "1.0.2"


def convert_dburl_to_dict(db_url):
    """
    Takes a URL to a database and parses it into an equivalent dictionary.
    dburl example:
        'mysql://username:password@hostname:port/dbname'
    """
    parse_result = urlparse.urlparse(unquote(db_url))
    db_params = dict(
        dbn=parse_result.scheme,
        username=parse_result.username,
        passwd=parse_result.password,
        db=parse_result.path[1:],
        host=parse_result.hostname,
        port=parse_result.port)
    return db_params


_databases = {}


def register_database(name, clazz):
    """
    Register a database.
    """
    _databases[name] = clazz


register_database('mysql', MySQLDB)

#register_database('postgres', PostgresDB)
#register_database('sqlite', SqliteDB)
#register_database('firebird', FirebirdDB)
#register_database('mssql', MSSQLDB)
#register_database('oracle', OracleDB)


def database(db_url=None, **params):
    """Creates appropriate database using params.
    """
    if not db_url and not params:
        db_url = os.environ.get('DATABASE_URL')
    if db_url:
        params = convert_dburl_to_dict(db_url)
    dbn = params.pop('dbn')
    if dbn in _databases:
        return _databases[dbn](**params)
    else:
        raise UnknownDB(dbn)
