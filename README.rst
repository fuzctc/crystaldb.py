
Crystaldb
======

crystaldb is a simple and small ORM. .

* a small, expressive ORM, and no need to provide a model.
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

Query method:

.. code-block:: python
    
    tablename: 'user'  fields: 'id', 'name', 'age', 'birthday'
    db_handle.select("user").get(id=1)
    db_handle.select("user").lt(id=5).gt(id=2).all() or db_handle.select("user").lt(id=5).gt(id=2).all().list()
    db_handle.select("user").between(id=[2, 5]).all()
    db_handle.select("user").in_(id=[2, 3, 4]).all()

