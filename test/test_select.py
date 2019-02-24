# !/usr/bin/python
# -*- coding:utf-8 -*-
# Author: Zhichang Fu
# Created Time: 2019-01-29 21:33:24

import pytest
from .dbmodule import TestDB


class TestSelect(object):
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

        CREATE TABLE `user_2` (
          `id` int(11) unsigned NOT NULL DEFAULT '0',
          `gender` varchar(16) CHARACTER SET utf8 DEFAULT NULL,
          `name` varchar(64) CHARACTER SET utf8 DEFAULT NULL,
          `birthday` varchar(16) CHARACTER SET utf8 NOT NULL,
          `age` int(11) unsigned NOT NULL
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8;
    """

    @pytest.fixture(scope="module")
    def dbmodule(self):
        return TestDB.db_handle()

    @pytest.mark.skipif(False, reason="skipped")
    def test_row_sql(self, dbmodule):
        """
        SQL:
            select * from user where id>80 and gender='girl';
        """
        sql = """select * from user where id>=$id and gender=:gender """
        sql = """select * from user where id>:id and gender=:gender"""
        params = {"id": 80, "gender": "girl"}
        result = dbmodule.query(sql, params)
        print(result)
        print(result.__len__())
        #  result Iter object or result.list() convert to list object
        for item in result:
            print(item)
        assert result.__len__() > 0
        #print(result.list())

    @pytest.mark.skipif(False, reason="skipped")
    def test_orm_get(self, dbmodule):
        """
        SQL:
            SELECT user.* FROM user WHERE user.id = 80;
        """
        result = dbmodule.select("user").get(id=80)
        print(result)
        print(result.__len__())
        #  result Iter object or result.list() convert to list object
        for item in result:
            print(item)
        assert result.__len__() > 0
        #print(result.list())

    @pytest.mark.skipif(False, reason="skipped")
    def test_orm_get_some_field(self, dbmodule):
        """
        SQL:
            SELECT user.name, user.age FROM user WHERE user.id = 80;
        """
        result = dbmodule.select("user", ["name", "age"]).get(id=80)
        print(result)
        print(result.__len__())
        #  result Iter object or result.list() convert to list object
        for item in result:
            print(item)
        assert result.__len__() > 0
        #print(result.list())

    @pytest.mark.skipif(False, reason="skipped")
    def test_orm_filter(self, dbmodule):
        """
        SQL:
            SELECT user.name, user.age FROM user WHERE user.age = 36 \
                    AND user.gender = 'girl';
        """
        result = dbmodule.select("user", ["name", "age"]).filter(
            age=36, gender="girl").query()  # query or all method
        #result = dbmodule.select("user", ["name", "age"]).filter(
        #    age=36, gender="girl").all()
        print(result)
        print(result.__len__())
        #  result Iter object or result.list() convert to list object
        for item in result:
            print(item)
        assert result.__len__() > 0
        print(dbmodule.get_debug_queries_info)
        #print(result.list())

    @pytest.mark.skipif(False, reason="skipped")
    def test_orm_distinct(self, dbmodule):
        """
        SQL:
            SELECT DISTINCT user.name, user.age FROM user WHERE \
                    user.age = 36 AND user.gender = 'girl'
        """
        result = dbmodule.select(
            "user", ["name", "age"], distinct=True).filter(
                age=36, gender="girl").query()  # query or all method
        #result = dbmodule.select("user", ["name", "age"], distinct=True).filter(
        #    age=36, gender="girl").all()
        print(result)
        print(result.__len__())
        #  result Iter object or result.list() convert to list object
        for item in result:
            print(item)
        assert result.__len__() > 0
        print(dbmodule.get_debug_queries_info)
        #print(result.list())

    @pytest.mark.skipif(False, reason="skipped")
    def test_orm_filter_dict(self, dbmodule):
        """
        SQL:
            SELECT user.name, user.age FROM user WHERE user.age = 36 \
                    AND user.gender = 'girl';
        """
        condition = dict(age=36, gender="girl")
        result = dbmodule.select("user",
                                 ["name", "age"]).filter(**condition).query()
        print(result)
        print(result.__len__())
        #  result Iter object or result.list() convert to list object
        for item in result:
            print(item)
        assert result.__len__() > 0
        #print(result.list())

    @pytest.mark.skipif(False, reason="skipped")
    def test_orm_filter_lt_or_gt(self, dbmodule):
        """
        SQL:
            SELECT user.* FROM user WHERE user.gender = 'girl' AND \
                    user.age < 40 AND user.age > 35 AND user.id < 80 \
                    AND user.id > 60;
        Grammar:
            Support `lt`, `gt`, `lte`, `gte`, `eq` method.
        """
        condition = dict(gender="girl")
        result = dbmodule.select("user").filter(**condition).lt(age=40).gt(
            age=35).lt(id=80).gt(id=60).query()
        print(result)
        print(result.__len__())
        #  result Iter object or result.list() convert to list object
        for item in result:
            print(item)
        assert result.__len__() > 0
        #print(result.list())

    @pytest.mark.skipif(False, reason="skipped")
    def test_orm_filter_between(self, dbmodule):
        """
        SQL:
            SELECT user.* FROM user WHERE user.gender = 'girl' AND user.age \
                    BETWEEN 35 AND 40  AND user.id BETWEEN 60 AND 80;
        """
        condition = dict(gender="girl")
        result = dbmodule.select("user").filter(**condition).between(
            age=[35, 40]).between(id=[60, 80]).query()
        print(result)
        print(result.__len__())
        #  result Iter object or result.list() convert to list object
        for item in result:
            print(item)
        assert result.__len__() > 0
        #print(result.list())

    @pytest.mark.skipif(False, reason="skipped")
    def test_orm_count(self, dbmodule):
        """
        SQL:
            SELECT COUNT(*) AS COUNT FROM user WHERE user.gender = 'girl' \
                    AND user.age BETWEEN 35 AND 40;
        """
        condition = dict(gender="girl")
        result = dbmodule.select("user").filter(**condition).between(
            age=[35, 40]).count()
        assert result > 0
        print(result)

    @pytest.mark.skipif(False, reason="skipped")
    def test_orm_distinct_count(self, dbmodule):
        """
        SQL:
            SELECT COUNT(DISTINCT user.name) AS COUNT FROM user \
                    WHERE user.gender = 'girl' AND user.age BETWEEN 35 AND 40;
        """
        condition = dict(gender="girl")
        result = dbmodule.select("user").filter(**condition).between(
            age=[35, 40]).count(distinct="name")
        assert result > 0
        print(result)

    @pytest.mark.skipif(False, reason="skipped")
    def test_orm_first(self, dbmodule):
        """
        SQL:
            SELECT user.* FROM user WHERE user.gender = 'girl' AND user.age \
                    BETWEEN 35 AND 40;
        """
        condition = dict(gender="girl")
        result = dbmodule.select("user").filter(**condition).between(
            age=[35, 40]).first()
        assert isinstance(result, dict)
        print(result)

    @pytest.mark.skipif(False, reason="skipped")
    def test_orm_order_by(self, dbmodule):
        """
        SQL:
            SELECT user.* FROM user WHERE user.gender = 'girl' AND \
                    user.age BETWEEN 35 AND 40  ORDER BY user.age;
        """
        condition = dict(gender="girl")
        result = dbmodule.select("user").filter(**condition).between(
            age=[35, 40]).order_by("age").query()
        print(result)
        print(result.__len__())
        #  result Iter object or result.list() convert to list object
        for item in result:
            print(item)
        assert result.__len__() > 0
        #print(result.list())

    @pytest.mark.skipif(True, reason="skipped")
    def test_orm_order_by_list(self, dbmodule):
        """
        SQL:
            SELECT user.* FROM user WHERE user.gender = 'girl' AND \
                    user.age BETWEEN 35 AND 40  ORDER BY user.age, user.name;
        """
        condition = dict(gender="girl")
        result = dbmodule.select("user").filter(**condition).between(
            age=[35, 40]).order_by(["age", "name"]).query()
        print(result)
        print(result.__len__())
        #  result Iter object or result.list() convert to list object
        for item in result:
            print(item)
        assert result.__len__() > 0
        #print(result.list())

    @pytest.mark.skipif(False, reason="skipped")
    def test_orm_order_by_list_reversed(self, dbmodule):
        """
        SQL:
            SELECT user.* FROM user WHERE user.gender = 'girl' AND user.age \
                    BETWEEN 35 AND 40  ORDER BY user.age DESC , user.name DESC;
        """
        condition = dict(gender="girl")
        result = dbmodule.select("user").filter(**condition).between(
            age=[35, 40]).order_by(
                ["age", "name"], _reversed=True).query()
        print(result)
        print(result.__len__())
        #  result Iter object or result.list() convert to list object
        for item in result:
            print(item)
        assert result.__len__() > 0
        #print(result.list())

    @pytest.mark.skipif(False, reason="skipped")
    def test_orm_order_by_list_complex(self, dbmodule):
        """
        SQL:
            SELECT user.* FROM user WHERE user.gender = 'girl' AND user.age \
                    BETWEEN 35 AND 40  ORDER BY user.age DESC, user. name ASC;
        """
        condition = dict(gender="girl")
        result = dbmodule.select("user").filter(**condition).between(
            age=[35, 40]).order_by("age DESC, name ASC").query()
        print(result)
        print(result.__len__())
        #  result Iter object or result.list() convert to list object
        for item in result:
            print(item)
        assert result.__len__() > 0
        #print(result.list())

    @pytest.mark.skipif(False, reason="skipped")
    def test_orm_in(self, dbmodule):
        """
        SQL:
            SELECT user.* FROM user WHERE user.gender = 'girl' AND user.age \
                    IN (35, 36)  AND user.id IN (80, 81, 82, 85);
        """
        condition = dict(gender="girl")
        result = dbmodule.select("user").filter(**condition).in_(
            age=[35, 36], id=[80, 81, 82, 85]).query()
        print(result)
        print(result.__len__())
        #  result Iter object or result.list() convert to list object
        for item in result:
            print(item)
        assert result.__len__() > 0
        #print(result.list())

    @pytest.mark.skipif(False, reason="skipped")
    def test_orm_not_in(self, dbmodule):
        """
        SQL:
            SELECT user.* FROM user WHERE user.gender = 'girl' AND \
                    user.id IN (80, 81, 82, 85)  AND user.age NOT IN (35, 36);
        """
        condition = dict(gender="girl")
        result = dbmodule.select("user").filter(**condition).in_(
            id=[80, 81, 82, 85]).not_in(age=[35, 36]).query()
        print(result)
        print(result.__len__())
        #  result Iter object or result.list() convert to list object
        for item in result:
            print(item)
        assert result.__len__() > 0
        #print(result.list())

    @pytest.mark.skipif(False, reason="skipped")
    def test_orm_limit(self, dbmodule):
        """
        SQL:
            SELECT user.* FROM user WHERE user.gender = 'girl' AND \
                    user.id IN (80, 81, 82, 85)  AND user.age \
                    NOT IN (35, 36)  LIMIT 10;
        """
        condition = dict(gender="girl")
        result = dbmodule.select("user").filter(**condition).in_(
            id=[80, 81, 82, 85]).not_in(age=[35, 36]).limit(10)
        print(result)
        print(result.__len__())
        #  result Iter object or result.list() convert to list object
        for item in result:
            print(item)
        assert result.__len__() > 0
        #print(result.list())

    @pytest.mark.skipif(False, reason="skipped")
    def test_orm_inner_join(self, dbmodule):
        """
        SQL:
            SELECT user.name, user.age, user_2.name as name2, \
                    user_2.age as age2 FROM user INNER JOIN user_2 ON \
                    user_2.id = user.id  WHERE user.gender = 'girl' \
                    AND user_2.gender = 'girl';
        """
        condition = dict(gender="girl")
        result = dbmodule.select(
            "user", ["name", "age"]).filter(**condition).inner_join(
                "user_2",
                using="id",
                fields=["name as name2", "age as age2"],
                **condition).query()
        print(result)
        print(result.__len__())
        #  result Iter object or result.list() convert to list object
        for item in result:
            print(item)
        assert result.__len__() > 0
        #print(result.list())

    @pytest.mark.skipif(False, reason="skipped")
    def test_orm_left_join(self, dbmodule):
        """
        SQL:
            SELECT user.name, user.age, user_2.name as name2, \
                    user_2.age as age2 FROM user LEFT JOIN  user_2 ON \
                    user_2.id = user.id  WHERE user.gender = 'girl' AND \
                    user_2.age = 35 AND user_2.gender = 'girl';
        """
        condition1 = dict(gender="girl")
        condition2 = dict(gender="girl", age=35)
        result = dbmodule.select(
            "user", ["name", "age"]).filter(**condition1).left_join(
                "user_2",
                using="id",
                fields=["name as name2", "age as age2"],
                **condition2).query()
        print(result)
        print(result.__len__())
        #  result Iter object or result.list() convert to list object
        for item in result:
            print(item)
        assert result.__len__() > 0
        #print(result.list())

    @pytest.mark.skipif(False, reason="skipped")
    def test_orm_right_join(self, dbmodule):
        """
        SQL:
            SELECT user.name, user.age, user_2.name as name2, \
                    user_2.age as age2 FROM user RIGHT JOIN   user_2 ON \
                    user_2.id = user.id  WHERE user.gender = 'girl' AND \
                    user_2.age = 35 AND user_2.gender = 'girl';
        """
        condition1 = dict(gender="girl")
        condition2 = dict(gender="girl", age=35)
        result = dbmodule.select(
            "user", ["name", "age"]).filter(**condition1).right_join(
                "user_2",
                using="id",
                fields=["name as name2", "age as age2"],
                **condition2).query()
        print(result)
        print(result.__len__())
        #  result Iter object or result.list() convert to list object
        for item in result:
            print(item)
        assert result.__len__() > 0
        print(dbmodule.get_debug_queries_info)
        #print(result.list())
