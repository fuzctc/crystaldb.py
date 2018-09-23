#!/bin/env python
# -*- coding: UTF-8 -*-

import webdb


class TestDB():
    db_instance = None
    db_host = '127.0.0.1'
    db_port = 3306
    db_user = 'root'
    db_pass = 'fuzc'
    db_database = 'meitu'

    def __init__(self):
        pass

    @staticmethod
    def new_db_handle():
        return webdb.database(
            dbn='mysql',
            host=TestDB.db_host,
            port=TestDB.db_port,
            user=TestDB.db_user,
            passwd=TestDB.db_pass,
            db=TestDB.db_database,
            debug=True)

    @staticmethod
    def db_handle():
        if not TestDB.db_instance:
            try_cnt = 3
            while try_cnt > 0:
                TestDB.db_instance = TestDB.new_db_handle()
                if TestDB.db_instance:
                    return TestDB.db_instance
                try_cnt = try_cnt - 1
        else:
            return TestDB.db_instance


if __name__ == "__main__":
    db_handle = TestDB.db_handle()
    print(db_handle)
    sql = """select * from test_user where id=$id"""
    params = {"id": 1}
    query_result = db_handle.query(sql, params)
    print(query_result)
    print(query_result.list())
