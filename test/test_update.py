# !/usr/bin/python
# -*- coding:utf-8 -*-
# Author: Zhichang Fu
# Created Time: 2019-01-29 21:33:24

import pytest
from .dbmodule import TestDB


class TestUpdate(object):
    """
    Table:
        CREATE TABLE `user` (
          `id` int(11) unsigned NOT NULL AUTO_INCREMENT,
          `gender` varchar(16) DEFAULT NULL,
          `name` varchar(64) DEFAULT NULL,
          `birthday` varchar(16) NOT NULL,
          `age` int(11) unsigned NOT NULL,
          PRIMARY KEY (`id`)
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8;
    """

    @pytest.fixture(scope="module")
    def dbmodule(self):
        return TestDB.db_handle()

    def test_row_sql(self, dbmodule):
        """
        SQL:
            update user set age=36, gender='boy', \
        birthday='1982-08-02' where name='xiaowang';
        """
        sql = """update user set age=$age, gender=$gender,
        birthday=$birthday where name=$name"""
        sql = """update user set age=:age, gender=:gender,
        birthday=:birthday where name=:name"""
        values = {
            'gender': 'boy',
            'name': 'xiaowang',
            'birthday': '1982-08-02',
            'age': 36
        }
        result = dbmodule.query(sql, values)
        assert result > 0
        print("insert result: ", result)

    def test_orm(self, dbmodule):
        """
        SQL:
            UPDATE user SET age = 37, birthday = '1981-08-02', \
                    gender = 'boy' WHERE name = 'xiaoli_orm';
        """
        where = dict(name="xiaoli_orm")
        values = {'gender': 'boy', 'birthday': '1981-08-02', 'age': 37}
        result = dbmodule.operator("user").update(where, **values)
        assert result > 0
        print("insert result: ", result)

    def test_orm_2(self, dbmodule):
        """
        SQL:
            UPDATE user SET age = 19, birthday = '1981-09-02' \
                    WHERE name = 'xiaoli_orm';
        """
        where = dict(name="xiaoli_orm")
        result = dbmodule.operator("user").update(
            where, age=19, birthday="1981-09-02")
        assert result > 0
        print("insert result: ", result)

    where = dict(id=4, age=20, name="xiao12", birthday="1995-08-03")
    values = dict(
        age=20, name="xiao1", birthday="1995-08-02", id=4, gender="girl")

    def test_orm_insert_update(self, dbmodule):
        """
        SQL:
            INSERT INTO user (age, birthday, gender, name) VALUES \
                    (36, '1982-08-02', 'girl', 'xiaoli_orm_insert_update') \
                    ON DUPLICATE KEY UPDATE age = 36 , id = 20 , \
                    name = 'xiaoli_orm_insert_update';
        """
        where = dict(id=20, age=36, name="xiaoli_orm_insert_update")
        values = {
            'gender': 'girl',
            'name': 'xiaoli_orm_insert_update',
            'birthday': '1982-08-02',
            'age': 36
        }
        result = dbmodule.operator("user").insert_duplicate_update(
            where, **values)
        assert result > 0
        print("insert result: ", result)
