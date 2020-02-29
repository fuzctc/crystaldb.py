# !/usr/bin/python
# -*- coding:utf-8 -*-
# Author: Zhichang Fu
# Created Time: 2018-12-18 15:26:36
'''
BEGIN
function:
    Configuration
END
'''


class AttrDict(dict):
    def __getattr__(self, attr):
        try:
            return self[attr]
        except KeyError:
            raise AttributeError(attr)

    def __setattr__(self, attr, value):
        self[attr] = value

    def __iadd__(self, rhs):
        self.update(rhs)
        return self

    def __add__(self, rhs):
        d = AttrDict(self)
        d.update(rhs)
        return d


OP = AttrDict(
    AND='AND',
    OR='OR',
    EQ='=',
    LT='<',
    LTE='<=',
    GT='>',
    GTE='>=',
    NE='!=',
    IN='IN',
    NOT_IN='NOT IN',
    IS='IS',
    IS_NOT='IS NOT',
    LIKE='LIKE',
    NOT_LIKE='NOT LIKE',
    BETWEEN='BETWEEN',
    DISTINCT='DISTINCT')

JOIN = AttrDict(
    INNER_JOIN='INNER JOIN',
    LEFT_JOIN='LEFT JOIN',
    RIGHT_JOIN='RIGHT JOIN',
    FULL_JOIN='FULL JOIN')

TOKEN = '[ \\f\\t]*(\\\\\\r?\\n[ \\f\\t]*)*(#[^\\r\\n]*)?(((\\d+[jJ]|((\\d+\\.\\d*|\\.\\d+)([eE][-+]?\\d+)?|\\d+[eE][-+]?\\d+)[jJ])|((\\d+\\.\\d*|\\.\\d+)([eE][-+]?\\d+)?|\\d+[eE][-+]?\\d+)|(0[xX][\\da-fA-F]+[lL]?|0[bB][01]+[lL]?|(0[oO][0-7]+)|(0[0-7]*)[lL]?|[1-9]\\d*[lL]?))|((\\*\\*=?|>>=?|<<=?|<>|!=|//=?|[+\\-*/%&|^=<>]=?|~)|[][(){}]|(\\r?\\n|[:;.,`@]))|([uUbB]?[rR]?\'[^\\n\'\\\\]*(?:\\\\.[^\\n\'\\\\]*)*\'|[uUbB]?[rR]?"[^\\n"\\\\]*(?:\\\\.[^\\n"\\\\]*)*")|[a-zA-Z_]\\w*)'
