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
            debug=True,
            get_debug_queries=True)

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
    sql = """select * from user where id=$id"""
    sql = """select * from user where id>:id and gender=:gender"""
    #>> select * from user where id>5 and gender='girl'
    params = {"id": 5, "gender": "girl"}
    query_result = db_handle.query(sql, params)
    print(query_result)
    print(query_result.list())

    ### select
    print("select...........")
    query_result = db_handle.select("user").filter_by(id=2).all()
    #>>SELECT * FROM user WHERE id = 2
    query_result = db_handle.select("user").get(id=2)
    #>>SELECT * FROM user WHERE id = 2
    for item in query_result:
        print(item)
    print(db_handle.select("user", ["id", "name"]).lt(id=5).gt(id=2).all().list())
    #>>SELECT id, name FROM user WHERE id < 5 AND id > 2
    print(db_handle.select("user").lte(id=20).gte(id=2).limit(2).list())
    #>>SELECT * FROM user WHERE id <= 20 AND id >= 2 LIMIT 2
    print(db_handle.select("user").between(id=[2, 5]).count())
    #>>SELECT COUNT(*) AS COUNT FROM user WHERE id BETWEEN 2 AND 5
    print(db_handle.select("user").eq(id=2).all().list())
    #>>SELECT * FROM user WHERE id = 2
    print(db_handle.select("user").filter(gender="girl").order_by(["age", "name"], _reversed=True).all().list())
    #>>SELECT * FROM user WHERE gender = 'girl' ORDER BY age DESC , name DESC
    print(db_handle.select("user").filter(gender="girl").order_by("age").all().list())
    #>>SELECT * FROM user WHERE gender = 'girl' ORDER BY age
    print(db_handle.select("user").lt(id=10).filter(gender="girl").order_by("age DESC, name ASC", _reversed=False).all().list())
    #>>SELECT * FROM user WHERE id < 10 AND gender = 'girl' ORDER BY age DESC, name ASC
    print(
        db_handle.select("user").gt(id=2).filter(
            gender="girl").query().list())
    #>>SELECT * FROM user WHERE id > 2 AND gender = 'girl'
    print(db_handle.select("user").lt(id=5, age=25).first()) # length=1
    #>>SELECT * FROM user WHERE age < 25 AND id < 5
    print(
        db_handle.select("user").in_(
            id=[1, 2, 3, 4], gender=["girl", "boy"]).all().list())
    #>>SELECT * FROM user WHERE gender IN ('girl', 'boy')  AND id IN (1, 2, 3, 4)

    ###insert
    sql = """insert into user set age=$age, gender=$gender, birthday=$birthday, name=$name"""
    values = {'gender': 'girl', 'name': 'xiaowang2', 'birthday': '1981-08-02', 'age': 35}
    print(db_handle.query(sql, values))
    print(db_handle.operator("user").insert(ignore=True, **values))
    print(db_handle.operator("user").insert(seqname=True, **values))
     
    #db_handle.supports_multiple_insert = False
    values_list = []
    for i in range(3):
        values = {'gender': 'girl', 'name': 'xiaowang2', 'birthday': '1981-08-02', 'age': 35+i}
        values_list.append(values)
    print(db_handle.operator("user").multiple_insert(values_list, seqname=True))

    ###update
    where = dict(id=5)
    values = dict(age=20, name="xiao1")
    print(db_handle.operator("user").update(where, age=19, name="xiao2"))
    print(db_handle.operator("user").update(where, **values))

    ###delete
    where = dict(id=5)
    print(db_handle.operator("user").delete(where))


    ####insert update
    where = dict(id=4, age=20, name="xiao12", birthday="1995-08-03")
    values = dict(age=20, name="xiao1", birthday="1995-08-02", id=4, gender="girl")
    print(db_handle.operator("user").insert_duplicate_update(where, **values))

    ###get debug queries
    where = dict(id=4, age=20, name="xiao12", birthday="1995-08-03")
    values = dict(age=20, name="xiao1", birthday="1995-08-02", id=4, gender="girl")
    print(db_handle.operator("user").insert_duplicate_update(where, **values))
    print(db_handle.get_debug_queries_info)



    ###table
    #print("table...........")
    #print(crystaldb.Table(db_handle, "user").select().lt(id=5).gt(id=2).all().list())
    #print(crystaldb.Table(db_handle, "user").select(["id", "gender", "age"]).lt(id=5).gt(id=2).all().list())

