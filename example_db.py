#!/bin/env python
# -*- coding: UTF-8 -*-

import webdb


class TestDB():
    db_instance = None
    db_host = '127.0.0.1'
    db_port = 3306
    db_user = 'root'
    db_pass = 'meitu123'
    db_database = 'webdb'

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
    #sql = """select * from ab_user_01 where id=$id"""
    #params = {"id": 1}
    #query_result = db_handle.query(sql, params)
    #print(query_result)
    #print(query_result.list())
    #print(db_handle.select_v2("ab_user_01").get(id=1).list())
    #print(db_handle.select_v2("ab_user_01").count(id=1))
    print(db_handle.select_v2("user").lt(id=5).gt(id=2).all().list())
    print(db_handle.select_v2("user").lte(id=5).gte(id=2).all().list())
    print(db_handle.select_v2("user").between(id=[2, 5]).all().list())
    print(db_handle.select_v2("user").eq(id=2).all().list())
    print(db_handle.select_v2("user").gt(id=2).filter(gender="girl").query().list())
    print(db_handle.select_v2("user").lt(id=5, age=25).all().list())
