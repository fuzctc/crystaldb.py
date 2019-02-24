# Update

```
CREATE TABLE `user` (
  `id` int(11) unsigned NOT NULL AUTO_INCREMENT,
  `gender` varchar(16) DEFAULT NULL,
  `name` varchar(16) DEFAULT NULL,
  `birthday` varchar(16) DEFAULT NULL,
  `age` int(11) unsigned DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
```
## 1. Raw Sql

Support `$` or `:` symbol.
```python
sql = """update user set age=$age, gender=$gender,
        birthday=$birthday where name=$name"""
        or
sql = """update user set age=:age, gender=:gender,
        birthday=:birthday where name=:name"""
values = {
      'gender': 'boy',
      'name': 'xiaowang',
      'birthday': '1982-08-02',
      'age': 36
    }
result = db_handle.query(sql, values)

# Actual execution sql expression
==> update user set age=36, gender='boy', \
        birthday='1982-08-02' where name='xiaowang';
```

## 2. Orm expression

* **Basic Usage:**
```python
where = dict(name="xiaoli_orm")
values = {'gender': 'boy', 'birthday': '1981-08-02', 'age': 37}
result = db_handle.operator("user").update(where, **values)
    or
result = db_handle.update("user", where, **values)

# Actual execution sql expression
==> UPDATE user SET age = 37, birthday = '1981-08-02', \
          gender = 'boy' WHERE name = 'xiaoli_orm';
```

* **Other Usage:**
```python
where = dict(name="xiaoli_orm")
result = dbmodule.operator("user").update(
      where, age=19, birthday="1981-09-02")

# Actual execution sql expression
==> UPDATE user SET age = 19, birthday = '1981-09-02' \
                    WHERE name = 'xiaoli_orm';
```

* **Insert update:**
```python
 where = dict(id=20, age=36, name="xiaoli_orm_insert_update")
 values = {
     'gender': 'girl',
     'name': 'xiaoli_orm_insert_update',
     'birthday': '1982-08-02',
     'age': 36
   }
 result = db_handle.operator("user").insert_duplicate_update(
        where, **values)
 result = dbmodule.insert_duplicate_update("user", where, **values)
 
# Actual execution sql expression
 => INSERT INTO user (age, birthday, gender, name) VALUES \
       (36, '1982-08-02', 'girl', 'xiaoli_orm_insert_update') 
        ON DUPLICATE KEY UPDATE age = 36 , id = 20 , \
        name = 'xiaoli_orm_insert_update';
```
