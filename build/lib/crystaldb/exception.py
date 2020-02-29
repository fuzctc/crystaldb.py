# !/usr/bin/python
# -*- coding:utf-8 -*-

# ***********************************************************************
# Author: Zhichang Fu
# Created Time: 2018-08-25 11:04:06
# Function:
#   Exception module
# ***********************************************************************


class UnknownDB(Exception):
    """raised for unsupported dbn"""
    pass


class UnknownParamstyle(Exception):
    """
    raised for unsupported db paramstyles

    (currently supported: qmark, numeric, format, pyformat)
    """
    pass


class _ItplError(ValueError):
    def __init__(self, text, pos):
        ValueError.__init__(self)
        self.text = text
        self.pos = pos

    def __str__(self):
        return "unfinished expression in %s at char %d" % (repr(self.text),
                                                           self.pos)
