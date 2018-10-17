
Crystaldb
======

crystaldb is a simple and small ORM, support native sql and orm. .

csystaldb是简单轻量级的mysql查询包，支持原生sql和orm.

* a small, expressive ORM, and no need to provide a model.
  支持orm, 不需要写MODEL.
* python 3.4+
* supports mysql(developed with others)


Examples
--------

Install:

.. code-block:: python

    pip install crystaldb


Connect to the database:

.. code-block:: python

    import crystaldb

    db_host = '127.0.0.1'
    db_port = 3306
    db_user = 'root'
    db_pass = '123'
    db_database = 'testdb'

    db_handle = crystaldb.database(
        dbn='mysql',
        host=db_host,
        port=db_port,
        user=db_user,
        passwd=db_pass,
        db=db_database,
        debug=True)


Create table: (Temporarily not supported)

暂时不支持创建表，需要去mysql先创建表。
   
.. code-block:: python

    CREATE TABLE `user` (
      `id` int(11) unsigned NOT NULL AUTO_INCREMENT,
      `gender` varchar(16) DEFAULT NULL,
      `name` varchar(16) DEFAULT NULL,
      `birthday` varchar(16) DEFAULT NULL,
      `age` int(11) unsigned DEFAULT NULL,
      PRIMARY KEY (`id`)
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8


Query Syntax:

查询语法:


* native sql, support '$' or ':' symbol.

.. code-block:: python
        
    # native sql, support '$' or ':' symbol.
    sql = """select * from user where id=$id"""
    sql = """select * from user where id>:id and gender=:gender"""
    # -->> select * from user where id>5 and gender='girl'
    params = {"id": 5, "gender": "girl"}
    db_handle.query(sql, params)


* get or filter_by syntax

.. code-block:: python

    query_result = db_handle.select("user").filter_by(id=2).all() # iterable object
    query_result.list() # list object
    # -->>SELECT * FROM user WHERE id = 2
    query_result = db_handle.select("user").get(id=2)
    # -->>SELECT * FROM user WHERE id = 2
    for item in query_result:
        print(item)


* lt or lte or gt or gte or eq syntax

.. code-block:: python

    db_handle.select("user", ["id", "name"]).lt(id=5).gt(id=2).all().list()
    #-->>SELECT id, name FROM user WHERE id < 5 AND id > 2
    db_handle.select("user").lte(id=20).gte(id=2).limit(2).list()
    #-->>SELECT * FROM user WHERE id <= 20 AND id >= 2 LIMIT 2
    db_handle.select("user").eq(id=2).all().list()
    #-->>SELECT * FROM user WHERE id = 2


* between syntax, also support count syntax

.. code-block:: python

    db_handle.select("user").between(id=[2, 5]).count()
    #-->>SELECT COUNT(*) AS COUNT FROM user WHERE id BETWEEN 2 AND 5


* filter syntax and order by syntax.

.. code-block:: python

    db_handle.select("user").filter(gender="girl").order_by(["age", "name"], _reversed=True).all().list()
    #-->>SELECT * FROM user WHERE gender = 'girl' ORDER BY age DESC , name DESC
    db_handle.select("user").filter(gender="girl").order_by("age").all().list()
    #-->>SELECT * FROM user WHERE gender = 'girl' ORDER BY age
    db_handle.select("user").lt(id=10).filter(gender="girl").order_by("age DESC, name ASC", _reversed=False).all().list() # reversed need be False.
    #-->>SELECT * FROM user WHERE id < 10 AND gender = 'girl' ORDER BY age DESC, name ASC


* The difference between filter and filter_by is that filter requires query syntax to return results.

.. code-block:: python

    db_handle.select("user").gt(id=2).filter(gender="girl").query().list()
    #-->>SELECT * FROM user WHERE id > 2 AND gender = 'girl'


* first syntax

.. code-block:: python

    db_handle.select("user").lt(id=5, age=25).first() # length=1
    #-->>SELECT * FROM user WHERE age < 25 AND id < 5

* in syntax

.. code-block:: python

    db_handle.select("user").in_(id=[1, 2, 3, 4], gender=["girl", "boy"]).all().list()
    #-->>SELECT * FROM user WHERE gender IN ('girl', 'boy')  AND id IN (1, 2, 3, 4)


Insert Syntax: support native sql and orm.

插入语法:

* native sql.

.. code-block:: python

    sql = """insert into user set age=$age, gender=$gender, birthday=$birthday, name=$name"""
    values = {'gender': 'girl', 'name': 'xiaowang2', 'birthday': '1981-08-02', 'age': 35}
    # -->>insert into user set age=35, gender='girl', birthday='1981-08-02', name='xiaowang2'
    result = db_handle.query(sql, values) # return row count


* orm.

.. code-block:: python

    values = {'gender': 'girl', 'name': 'xiaowang2', 'birthday': '1981-08-02', 'age': 35}
    result = db_handle.operator("user").insert(ignore=True, **values) # return row sql
    # -->>INSERT IGNORE INTO user (age, birthday, gender, name) VALUES (35, '1981-08-02', 'girl', 'xiaowang2')

    result = db_handle.operator("user").insert(seqname=True, **values) # return lastest insert id.
    # -->>INSERT INTO user (age, birthday, gender, name) VALUES (35, '1981-08-02', 'girl', 'xiaowang2');
    # -->>SELECT last_insert_id();

    # multiple insert
    values_list = []
    for i in range(3):
        values = {'gender': 'girl', 'name': 'xiaowang2', 'birthday': '1981-08-02', 'age': 35+i}
        values_list.append(values)
    result = db_handle.operator("user").multiple_insert(values_list, seqname=True) # return range(lastest insert id)
    # -->> INSERT INTO user (age, birthday, gender, name) VALUES (35, '1981-08-02', 'girl', 'xiaowang2'), (36, '1981-08-02', 'girl', 'xiaowang2'), (37, '1981-08-02', 'girl', 'xiaowang2')
    # -->> SELECT last_insert_id();
    # -->> returns:  range(48, 51)


Update Syntax: support native sql and orm.

更新语法:

.. code-block:: python

    where = dict(id=5)
    result = db_handle.operator("user").update(where, age=19, name="xiao2"))
    # -->>UPDATE user SET age = 19, name = 'xiao2' WHERE id = 5

    debug_sql = db_handle.debug_queries # dict object.
    # -->>{'run_time': '0.2793', 'sql': "UPDATE user SET age = 20, name = 'xiao1' WHERE id = 5"}

    values = dict(age=20, name="xiao1")
    result = db_handle.operator("user").update(where, **values))
    # -->>UPDATE user SET age = 20, name = 'xiao1' WHERE id = 5


Insert Duplicate Update Syntax: support native sql and orm.

.. code-block:: python

    where = dict(id=4, age=20, name="xiao12", birthday="1995-08-03")
    values = dict(age=20, name="xiao1", birthday="1995-08-02", id=4, gender="girl")
    result = db_handle.operator("user").insert_duplicate_update(where, **values)
    # -->>INSERT INTO user (age, birthday, gender, id, name) VALUES (20, '1995-08-02', 'girl', 4, 'xiao1') ON DUPLICATE KEY UPDATE age = 20 , birthday = '1995-08-03' , id = 4 , name = 'xiao12'


Delete Syntax: support native sql and orm.

删除语法:

.. code-block:: python

    where = dict(id=5)
    result = db_handle.operator("user").delete(where)
    # -->> DELETE FROM user WHERE id = 5



Get Debug Queries.

.. code-block:: python

    db_handle = crystaldb.database(
        dbn='mysql',
        host=db_host,
        port=db_port,
        user=db_user,
        passwd=db_pass,
        db=db_database,
        get_debug_queries=True)

    where = dict(id=4, age=20, name="xiao12", birthday="1995-08-03")
    values = dict(age=20, name="xiao1", birthday="1995-08-02", id=4, gender="girl")
    result = db_handle.operator("user").insert_duplicate_update(where, **values)
    debug_queries_info = db_handle.get_debug_queries_info
    # -->>{'run_time': '0.2749', 'sql': "INSERT INTO user (age, birthday, gender, id, name) VALUES (20, '1995-08-02', 'girl', 4, 'xiao1') ON DUPLICATE KEY UPDATE age = 20 , birthday = '1995-08-03' , id = 4 , name = 'xiao12'"}  # run_time: unit ms
    


