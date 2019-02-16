



CrystalDB
======

CrystalDB is a simple and small ORM. It has few concepts, making it easy to learn and intuitive to use.

* a small, expressive ORM, and no need to provide a model, so it will not be difficult for the problem of sub-library or sub-tables. 
* python3.
* need mysql-client or pymysql or mysql.connector.
* currently only supports mysql.

Installation
============
From PyPi::

    $ pip install crysyaldb

Basic Usage
===========

* **Connect to the database:**

   ```
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
    ```

* **Create table:** (Temporarily not supported, need to be completed by yourself) 
    for example:
    
    ```python
    CREATE TABLE `user` (
      `id` int(11) unsigned NOT NULL AUTO_INCREMENT,
      `gender` varchar(16) DEFAULT NULL,
      `name` varchar(16) DEFAULT NULL,
      `birthday` varchar(16) DEFAULT NULL,
      `age` int(11) unsigned DEFAULT NULL,
      PRIMARY KEY (`id`)
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8;
    ```  
    
* **Create rows:**
    ```python
    values = {
            'gender': 'girl',
            'name': 'xiaoli_orm',
            'birthday': '1982-08-02',
            'age': 36
        }
    result = db_handle.operator("user").insert(**values)
    print(result) # ==> 1
    # If debug is True, the following log will be printed, time unit ms.
    # 0.3162 (1): INSERT INTO user (age, birthday, gender, name) VALUES (36, '1982-08-02', 'girl', 'xiaoli_orm')
    ```
    
* **Querying:**
    ```python
    result = db_handle.select("user", ["name", "age"]).filter(
            age=36, gender="girl").query()
    print(result.__len__()) # count 
    print(result) # <crystaldb.utils.IterBetter object at 0x1115246a0>
    for item in result:
        print(item)  # <Storage {'name': 'xiaowang', 'age': 36}>
        print(item.name) # xiaowang
    # If debug is True, the following log will be printed, time unit ms.
    # 0.8579 (1): SELECT user.name, user.age FROM user WHERE user.age = 36 AND user.gender = 'girl'
    ```
