# !/usr/bin/python
# -*- coding:utf-8 -*-
# Author: Zhichang Fu
# Created Time: 2019-01-29 21:33:24

import pytest
from .dbmodule import TestDB


class TestDelete(object):
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
            delete from user where name='xiaowang' and gender='boy' and
        birthday='1982-08-02' and age=36
        """
        sql = """delete from user where name=:name and gender=:gender and 
        birthday=:birthday and age=:age"""
        values = {
            'gender': 'boy',
            'name': 'xiaowang',
            'birthday': '1982-08-02',
            'age': 36
        }
        result = dbmodule.query(sql, values)
        assert result > 0
        print("delete result: ", result)

    def test_orm(self, dbmodule):
        """
        SQL:
            DELETE FROM user WHERE age = 36 AND name = 'xiaoli_orm';
            DELETE FROM user WHERE age = 28 AND name = 'xiaoming';
            DELETE FROM user WHERE age = 27 AND name = 'xiaoyu';
        """
        where = dict(name="xiaoyu", age=27)
        #result = dbmodule.operator("user").delete(where)
        result = dbmodule.delete("user", where)
        assert result > 0
        print("delete result: ", result)
