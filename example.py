#!/bin/env python
# -*- coding: UTF-8 -*-

import crystaldb


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
        return crystaldb.database(
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
    #print(db_handle)
    #sql = """select * from ab_user_01 where id=$id"""
    #params = {"id": 1}
    #query_result = db_handle.query(sql, params)
    #print(query_result)
    #print(query_result.list())
    #print(db_handle.select_v2("ab_user_01").get(id=1).list())
    #print(db_handle.select_v2("ab_user_01").count(id=1))

    ### select
    print("select...........")
    print(db_handle.select("user").lt(id=5).gt(id=2).all().list())
    #print(db_handle.select("user").lte(id=5).gte(id=2).all().list())
    #print(db_handle.select("user").between(id=[2, 5]).all().list())
    #print(db_handle.select("user").eq(id=2).all().list())
    #print(
    #    db_handle.select("user").gt(id=2).filter(
    #        gender="girl").query().list())
    #print(db_handle.select("user").lt(id=5, age=25).all().list())
    #print(db_handle.select("user").in_(id=[2, 3, 4]).all().list())
    #print(
    #    db_handle.select("user").in_(
    #        id=[1, 2, 3, 4], gender=["girl", "boy"]).all().list())
    #print(
    #    db_handle.select("user", ["id", "gender"]).in_(
    #        id=[1, 2, 3, 4], gender=["girl", "boy"]).filter().limit(1).list())

    ###insert
    #values = {'gender': 'girl', 'name': 'xiaowang2', 'birthday': '1981-08-02', 'age': 35}
    #print(db_handle.operator("user").insert(ignore=True, **values))
    #print(db_handle.operator("user").insert(seqname=True, **values))
    #values_list = []
    #for i in range(3):
    #    values = {'gender': 'girl', 'name': 'xiaowang2', 'birthday': '1981-08-02', 'age': 35+i}
    #    values_list.append(values)
    #print(db_handle.operator("user").multiple_insert(values_list, seqname=True))

    ###update
    #where = dict(id=5)
    #values = dict(age=20, name="xiao1")
    ##print(db_handle.operator("user").update(where, age=19, name="xiao2"))
    #print(db_handle.operator("user").update(where, **values))

    ###delete
    #where = dict(id=5)
    #print(db_handle.operator("user").delete(where))


    ####insert update
    #where = dict(id=4, age=20, name="xiao12", birthday="1995-08-03")
    #values = dict(age=20, name="xiao1", birthday="1995-08-02", id=4, gender="girl")
    #print(db_handle.operator("user").insert_duplicate_update(where, **values))


    ###table
    #print("table...........")
    #print(crystaldb.Table(db_handle, "user").select().lt(id=5).gt(id=2).all().list())
    #print(crystaldb.Table(db_handle, "user").select(["id", "gender", "age"]).lt(id=5).gt(id=2).all().list())

