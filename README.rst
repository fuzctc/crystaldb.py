
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
        #>> select * from user where id>5 and gender='girl'
        params = {"id": 5, "gender": "girl"}
        db_handle.query(sql, params)


* get or filter_by syntax

    .. code-block:: python

        query_result = db_handle.select("user").filter_by(id=2).all() #>>iterable object
        query_result.list() #>> list object
        #>>SELECT * FROM user WHERE id = 2
        query_result = db_handle.select("user").get(id=2)
        #>>SELECT * FROM user WHERE id = 2
        for item in query_result:
            print(item)

    * lt or lte or gt or gte or eq syntax

    .. code-block:: python

        db_handle.select("user", ["id", "name"]).lt(id=5).gt(id=2).all().list()
        #>>SELECT id, name FROM user WHERE id < 5 AND id > 2
        db_handle.select("user").lte(id=20).gte(id=2).limit(2).list()
        #>>SELECT * FROM user WHERE id <= 20 AND id >= 2 LIMIT 2
        db_handle.select("user").eq(id=2).all().list()
        #>>SELECT * FROM user WHERE id = 2

        # between syntax, also support count syntax
        db_handle.select("user").between(id=[2, 5]).count()
        #>>SELECT COUNT(*) AS COUNT FROM user WHERE id BETWEEN 2 AND 5

        # filter syntax and order by syntax.
        db_handle.select("user").filter(gender="girl").order_by(["age", "name"], _reversed=True).all().list()
        #>>SELECT * FROM user WHERE gender = 'girl' ORDER BY age DESC , name DESC
        db_handle.select("user").filter(gender="girl").order_by("age").all().list()
        #>>SELECT * FROM user WHERE gender = 'girl' ORDER BY age
        db_handle.select("user").lt(id=10).filter(gender="girl").order_by("age DESC, name ASC", _reversed=False).all().list() ##> reversed need be False.
        #>>SELECT * FROM user WHERE id < 10 AND gender = 'girl' ORDER BY age DESC, name ASC

        # The difference between filter and filter_by is that filter requires query syntax to return results.
        db_handle.select("user").gt(id=2).filter(gender="girl").query().list()
        #>>SELECT * FROM user WHERE id > 2 AND gender = 'girl'

        # first syntax
        db_handle.select("user").lt(id=5, age=25).first() # length=1
        #>>SELECT * FROM user WHERE age < 25 AND id < 5

        # in syntax
        db_handle.select("user").in_(id=[1, 2, 3, 4], gender=["girl", "boy"]).all().list()
        #>>SELECT * FROM user WHERE gender IN ('girl', 'boy')  AND id IN (1, 2, 3, 4)

