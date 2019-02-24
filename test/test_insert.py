# !/usr/bin/python
# -*- coding:utf-8 -*-
# Author: Zhichang Fu
# Created Time: 2019-01-29 21:33:24

import pytest
from .dbmodule import TestDB


class TestInsert(object):
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
            insert into user set age=37, gender='girl',
        birthday='1981-08-02', name='xiaowang'
        """
        sql = """insert into user set age=$age, gender=$gender,
        birthday=$birthday, name=$name"""
        sql = """insert into user set age=:age, gender=:gender,
        birthday=:birthday, name=:name"""
        values = {
            'gender': 'girl',
            'name': 'xiaowang',
            'birthday': '1981-08-02',
            'age': 37
        }
        result = dbmodule.query(sql, values)
        assert result == 1
        print("insert result: ", result)

    def test_orm(self, dbmodule):
        """
        SQL:
            INSERT INTO user (age, birthday, gender, name) VALUES \
                    (36, '1982-08-02', 'girl', 'xiaoli_orm')
        """
        values = {
            'gender': 'girl',
            'name': 'xiaoli_orm',
            'birthday': '1982-08-02',
            'age': 36
        }
        #result = dbmodule.operator("user").insert(**values)
        result = dbmodule.insert("user", **values)
        assert result == 1
        print("insert result: ", result)

    def test_orm_ignore(self, dbmodule):
        """
        SQL:
            INSERT IGNORE INTO user (age, birthday, gender, name) VALUES \
                    (36, '1982-08-02', 'girl', 'xiaoli_orm')
        """
        values = {
            'gender': 'girl',
            'name': 'xiaoli_orm_ignore',
            'birthday': '1982-08-02',
            'age': 36
        }
        #result = dbmodule.operator("user").insert(ignore=True, **values)
        result = dbmodule.insert("user", ignore=True, **values)
        assert result == 1
        print("insert result: ", result)

    def test_orm_return_lastest_insert_id(self, dbmodule):
        """
        SQL:
            INSERT INTO user (age, birthday, gender, name) VALUES \
                    (36, '1982-08-02', 'girl', 'orm_return_id');
            SELECT last_insert_id();
        """
        values = {
            'gender': 'girl',
            'name': 'orm_return_id',
            'birthday': '1982-08-02',
            'age': 36
        }
        #result = dbmodule.operator("user").insert(seqname=True, **values)
        result = dbmodule.insert("user", seqname=True, **values)
        assert result > 0
        print("insert result: ", result)

    def test_orm_multiple_insert(self, dbmodule):
        """
        SQL:
            INSERT INTO user (age, birthday, gender, name) VALUES \
                    (35, '1981-08-02', 'girl', 'orm_multiple_insert'), \
                    (36, '1981-08-02', 'girl', 'orm_multiple_insert'), \
                    (37, '1981-08-02', 'girl', 'orm_multiple_insert')
        """
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
        #result = dbmodule.operator("user").multiple_insert(values_list)
        result = dbmodule.multiple_insert("user", values_list)
        assert result == 3
        print("insert result: ", result)

    def test_orm_multiple_insert_return_ids(self, dbmodule):
        """
        SQL:
            INSERT INTO user (age, birthday, gender, name) VALUES \
                (35, '1981-08-02', 'girl', 'orm_multiple_insert_return_ids'), \
                (36, '1981-08-02', 'girl', 'orm_multiple_insert_return_ids'), \
                (37, '1981-08-02', 'girl', 'orm_multiple_insert_return_ids')
            SELECT last_insert_id();

        result:  range(116, 119)
        """
        values_list = []
        num = 3
        for i in range(num):
            values = {
                'gender': 'girl',
                'name': 'orm_multiple_insert_return_ids',
                'birthday': '1981-08-02',
                'age': 35 + i
            }
            values_list.append(values)
        #result = dbmodule.operator("user").multiple_insert(
        #    values_list, seqname=True)
        result = dbmodule.multiple_insert("user", values_list, seqname=True)
        assert isinstance(result, range)
        print("insert result: ", result)
