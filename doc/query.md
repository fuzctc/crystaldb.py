# Query

```
CREATE TABLE `user` (
   `id` int(11) unsigned NOT NULL AUTO_INCREMENT,
   `gender` varchar(16) DEFAULT NULL,
   `name` varchar(64) DEFAULT NULL,
   `birthday` varchar(16) NOT NULL,
   `age` int(11) unsigned NOT NULL,
    PRIMARY KEY (`id`)
  ) ENGINE=InnoDB DEFAULT CHARSET=utf8;

CREATE TABLE `user_2` (
    `id` int(11) unsigned NOT NULL DEFAULT '0',
    `gender` varchar(16) CHARACTER SET utf8 DEFAULT NULL,
    `name` varchar(64) CHARACTER SET utf8 DEFAULT NULL,
    `birthday` varchar(16) CHARACTER SET utf8 NOT NULL,
    `age` int(11) unsigned NOT NULL
   ) ENGINE=InnoDB DEFAULT CHARSET=utf8;
```
## 1. Raw Sql

Support `$` or `:` symbol.
```python
sql = """select * from user where id>=$id and gender=$gender"""
    or
sql = """select * from user where id>:id and gender=:gender"""

params = {"id": 80, "gender": "girl"}
result = db_handle.query(sql, params)
print(result)  # <crystaldb.utils.IterBetter object at 0x1115246a0>
print(result.__len__()) # count
#  result Iter object or result.list() convert to list object
for item in result:
   print(item) # <Storage {'id': 81, 'gender': 'girl', 'name': 'xiaowang2', 'birthday': '1981-08-02', 'age': 36}>
   print(item.name) # xiaowang2

# Actual execution sql expression
==> select * from user where id>80 and gender='girl';
```

## 2. Orm expression

* **get**
```python
result = db_handle.select("user").get(id=80)

# Actual execution sql expression
=> SELECT user.* FROM user WHERE user.id = 80;
```

* **get some fields**
```python
result = db_handle.select("user", ["name", "age"]).get(id=80)

# Actual execution sql expression
=> SELECT user.name, user.age FROM user WHERE user.id = 80;
```

* **filter**
```python
 result = db_handle.select("user", ["name", "age"]).filter(
            age=36, gender="girl").query()
        or
 result = db_handle.select("user", ["name", "age"]).filter(
            age=36, gender="girl").all()
 
# Actual execution sql expression
 => SELECT user.name, user.age FROM user WHERE user.age = 36 \
                    AND user.gender = 'girl';
```

* **filter with dict**
```python
condition = dict(age=36, gender="girl")
result = db_handle.select("user",      ["name","age"]).filter(**condition).query()

# Actual execution sql expression
 => SELECT user.name, user.age FROM user WHERE user.age = 36 \
                    AND user.gender = 'girl';
```

* **gt or lt or gte or lte or eq**
Support `lt`, `gt`, `lte`, `gte`, `eq` method.
```python
condition = dict(gender="girl")
result = db_handle.select("user").filter(**condition).\
lt(age=40).gt(age=35).lt(id=80).gt(id=60).query()

# Actual execution sql expression
=> SELECT user.* FROM user WHERE user.gender = 'girl' AND \
    user.age < 40 AND user.age > 35 AND user.id < 80 \
    AND user.id > 60;
```

* **between**
```python
condition = dict(gender="girl")
result = db_handle.select("user").filter(**condition). \
        between(age=[35, 40]).between(id=[60, 80]).query()

# Actual execution sql expression
=> SELECT user.* FROM user WHERE user.gender = 'girl' AND
   user.age BETWEEN 35 AND 40  AND user.id BETWEEN 60 AND 80;
```

* **count**
```python
condition = dict(gender="girl")
result = db_handle.select("user").filter(**condition).\
    between(age=[35, 40]).count() # 30

# Actual execution sql expression
=> SELECT COUNT(*) AS COUNT FROM user WHERE user.gender='girl' \
   AND user.age BETWEEN 35 AND 40;
```

* **distinct**
```python
result = dbmodule.select("user", ["name", "age"], \
        distinct=True).filter(age=36, gender="girl").query()

# Actual execution sql expression
=> SELECT DISTINCT user.name, user.age FROM user WHERE \
                    user.age = 36 AND user.gender = 'girl'
```

* **count distinct**
```python
condition = dict(gender="girl")
result = dbmodule.select("user").filter(**condition).\
    between(age=[35, 40]).count(distinct="name")

# Actual execution sql expression
=> SELECT COUNT(DISTINCT user.name) AS COUNT FROM user \
    WHERE user.gender = 'girl' AND user.age BETWEEN 35 AND 40;
```

* **first**
```python
condition = dict(gender="girl")
result = dbmodule.select("user").filter(**condition).\
    between(age=[35, 40]).first()
len(result) = 1
# Actual execution sql expression
=> SELECT user.* FROM user WHERE user.gender = 'girl' AND user.age BETWEEN 35 AND 40;
```

* **order by**
```python
condition = dict(gender="girl")
result = db_handle.select("user").filter(**condition).\
    between(age=[35, 40]).order_by("age").query()
    
# Actual execution sql expression
SELECT user.* FROM user WHERE user.gender = 'girl' AND \
      user.age BETWEEN 35 AND 40  ORDER BY user.age;
```

* **order by list**
```python
condition = dict(gender="girl")
result = dbmodule.select("user").filter(**condition).\
    between(age=[35, 40]).order_by(["age", "name"]).query()
    
=> SELECT user.* FROM user WHERE user.gender = 'girl' AND \
    user.age BETWEEN 35 AND 40  ORDER BY user.age, user.name
```

* **order by reversed**
```python
condition = dict(gender="girl")
result = dbmodule.select("user").filter(**condition).\
        between(age=[35, 40]).order_by(
                ["age", "name"], _reversed=True).query()

=> SELECT user.* FROM user WHERE user.gender = 'girl' \
AND user.age BETWEEN 35 AND 40  ORDER BY \
user.age DESC , user.name DESC;
```

* **order by complex case**
```python
condition = dict(gender="girl")
result = db_handle.select("user").filter(**condition). \
        between(age=[35, 40]).order_by("age DESC, name ASC").query()
        
=> SELECT user.* FROM user WHERE user.gender = 'girl' \
AND user.age BETWEEN 35 AND 40  ORDER BY user.age DESC, user. name ASC;
```

* **in**
```python
condition = dict(gender="girl")
result = db_handle.select("user").filter(**condition). \
        in_(age=[35, 36], id=[80, 81, 82, 85]).query()
        
=> SELECT user.* FROM user WHERE user.gender = 'girl' \
AND user.age IN (35, 36)  AND user.id IN (80, 81, 82, 85);
```

* **not in**
```python
condition = dict(gender="girl")
result = db_handle.select("user").filter(**condition). \
        in_(id=[80, 81, 82, 85]).not_in(age=[35, 36]).query()
        
=> SELECT user.* FROM user WHERE user.gender = 'girl' AND \
    user.id IN (80, 81, 82, 85)  AND user.age NOT IN (35, 36);
```

* **limit**
```python
condition = dict(gender="girl")
result = db_handle.select("user").filter(**condition). \
in_(id=[80, 81, 82, 85]).not_in(age=[35, 36]).limit(10)

=> SELECT user.* FROM user WHERE user.gender = 'girl' AND \
      user.id IN (80, 81, 82, 85)  AND user.age \
      NOT IN (35, 36)  LIMIT 10;
```

* **inner join**
```python
condition = dict(gender="girl")
result = db_handle.select("user", ["name", "age"]).filter(**condition).inner_join(
                "user_2",
                using="id",
                fields=["name as name2", "age as age2"],
                **condition).query()

=> SELECT user.name, user.age, user_2.name as name2, \
     user_2.age as age2 FROM user INNER JOIN user_2 ON \
     user_2.id = user.id  WHERE user.gender = 'girl' \
     AND user_2.gender = 'girl';
```

* **left join**
```python
 condition1 = dict(gender="girl")
 condition2 = dict(gender="girl", age=35)
 result = db_handle.select("user", ["name", "age"]).filter(**condition1).left_join(
                "user_2",
                using="id",
                fields=["name as name2", "age as age2"],
                **condition2).query()
                
 => SELECT user.name, user.age, user_2.name as name2, \
    user_2.age as age2 FROM user LEFT JOIN  user_2 ON \
    user_2.id = user.id  WHERE user.gender = 'girl' AND \
    user_2.age = 35 AND user_2.gender = 'girl';
```

* **right join**
```python
condition1 = dict(gender="girl")
condition2 = dict(gender="girl", age=35)
result = db_handle.select("user", ["name", "age"]).filter(**condition1).right_join(
                "user_2",
                using="id",
                fields=["name as name2", "age as age2"],
                **condition2).query()

=> SELECT user.name, user.age, user_2.name as name2, \
   user_2.age as age2 FROM user RIGHT JOIN   user_2 ON \
   user_2.id = user.id  WHERE user.gender = 'girl' AND \
   user_2.age = 35 AND user_2.gender = 'girl';
```
