# Delete

```
CREATE TABLE `user` (
   `id` int(11) unsigned NOT NULL AUTO_INCREMENT,
   `gender` varchar(16) DEFAULT NULL,
   `name` varchar(64) DEFAULT NULL,
   `birthday` varchar(16) NOT NULL,
   `age` int(11) unsigned NOT NULL,
    PRIMARY KEY (`id`)
  ) ENGINE=InnoDB DEFAULT CHARSET=utf8;
```

## 1. raw sql
```python
sql = """delete from user where name=:name and gender=:gender and birthday=:birthday and age=:age"""
values = {
            'gender': 'boy',
            'name': 'xiaowang',
            'birthday': '1982-08-02',
            'age': 36
        }
result = db_handle.query(sql, values)

=> delete from user where name='xiaowang' and gender='boy' and
        birthday='1982-08-02' and age=36
```


## 2. orm
```python
where = dict(name="xiaoyu", age=27)
result = db_handle.operator("user").delete(where)
      or
result = db_handle.delete("user", where)

=> DELETE FROM user WHERE age = 27 AND name = 'xiaoyu';
```
