# Insert

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
sql = """insert into user set age=$age, gender=$gender,
      birthday=$birthday, name=$name"""
      
      or
      
sql = """insert into user set age=:age, gender=:gender,
        birthday=:birthday, name=:name"""
values = {
            'gender': 'girl',
            'name': 'xiaowang',
            'birthday': '1981-08-02',
            'age': 37
        }
result = db_handle.query(sql, values)
print("insert result: ", result)

# Actual execution sql expression
==> insert into user set age=37, gender='girl',
        birthday='1981-08-02', name='xiaowang'
```

## 2. Orm expression

* **Basic Usage:**

```python
values = {
            'gender': 'girl',
            'name': 'xiaoli_orm',
            'birthday': '1982-08-02',
            'age': 36
        }
result = db_handle.operator("user").insert(**values)

# Can also use the Insert method directly.

result = db_handle.insert("user", **values)

# Actual execution sql expression
==> INSERT INTO user (age, birthday, gender, name) VALUES (36, '1982-08-02', 'girl', 'xiaoli_orm')
```

* **Ignore:**

If needs to be execute `insert ignore user ...`, syntax can be supported.
```python
result = db_handle.operator("user").insert(ignore=True, **values)
    or
result = db_handle.insert("user", ignore=True, **values)

# Actual execution sql expression
==> INSERT IGNORE INTO user (age, birthday, gender, name) VALUES (36, '1982-08-02', 'girl', 'xiaoli_orm')
```

* **Return latest insert id:**

```python
result = db_handle.operator("user").insert(seqname=True, **values)
    or
result = db_handle.insert("user", seqname=True, **values) => 141307

result is the latest insert id.

# Actual execution sql expression
INSERT INTO user (age, birthday, gender, name) VALUES 
     (36, '1982-08-02', 'girl', 'xiaoli_orm');
SELECT last_insert_id();
```

* **Multiple insert:**

```python
values_list = []
num = 3
for i in range(num):
 values = {
     'gender': 'girl',
     'name': 'orm_multiple_insert',
     'birthday': '1981-08-02',
     'age': 35 + i
    }
 values_list.append(values)
 result = dbmodule.operator("user").multiple_insert(
        values_list)
     or
 result = dbmodule.multiple_insert("user", values_list)
 => result = 3
 
# Actual execution sql expression
=>INSERT INTO user (age, birthday, gender, name) VALUES 
          (35, '1981-08-02', 'girl', 'orm_multiple_insert'), \
          (36, '1981-08-02', 'girl', 'orm_multiple_insert'), \
          (37, '1981-08-02', 'girl', 'orm_multiple_insert')
```

* **Multiple insert: return latest insert id:**
```python
 result = dbmodule.operator("user").multiple_insert(
        values_list, seqname=True)
 result = dbmodule.multiple_insert("user", values_list, seqname=True) \
	=> range(116, 119)
 
 result is the `Range` object.
 
 # Actual execution sql expression
 => INSERT INTO user (age, birthday, gender, name) VALUES 
          (35, '1981-08-02', 'girl', 'orm_multiple_insert'), \
          (36, '1981-08-02', 'girl', 'orm_multiple_insert'), \
          (37, '1981-08-02', 'girl', 'orm_multiple_insert')
    SELECT last_insert_id();
```
