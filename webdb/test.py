# !/usr/bin/python
# -*- coding:utf-8 -*-

# ***********************************************************************
# Author: Zhichang Fu
# Created Time: 2018-09-22 14:23:38
# Function:
#
# ***********************************************************************

import re

TOKEN = '[ \\f\\t]*(\\\\\\r?\\n[ \\f\\t]*)*(#[^\\r\\n]*)?(((\\d+[jJ]|((\\d+\\.\\d*|\\.\\d+)([eE][-+]?\\d+)?|\\d+[eE][-+]?\\d+)[jJ])|((\\d+\\.\\d*|\\.\\d+)([eE][-+]?\\d+)?|\\d+[eE][-+]?\\d+)|(0[xX][\\da-fA-F]+[lL]?|0[bB][01]+[lL]?|(0[oO][0-7]+)|(0[0-7]*)[lL]?|[1-9]\\d*[lL]?))|((\\*\\*=?|>>=?|<<=?|<>|!=|//=?|[+\\-*/%&|^=<>]=?|~)|[][(){}]|(\\r?\\n|[:;.,`@]))|([uUbB]?[rR]?\'[^\\n\'\\\\]*(?:\\\\.[^\\n\'\\\\]*)*\'|[uUbB]?[rR]?"[^\\n"\\\\]*(?:\\\\.[^\\n"\\\\]*)*")|[a-zA-Z_]\\w*)'

tokenprog = re.compile(TOKEN)


class _Node(object):
    def __init__(self, type, first, second=None):
        self.type = type
        self.first = first
        self.second = second

    def __eq__(self, other):
        return (isinstance(other, _Node) and self.type == other.type and
                self.first == other.first and self.second == other.second)

    def __repr__(self):
        return "Node(%r, %r, %r)" % (self.type, self.first, self.second)


class Parser:
    """Parser to parse string templates like "Hello $name".

    Loosely based on <http://lfw.org/python/Itpl.py> (public domain, Ka-Ping Yee)
    """
    namechars = "abcdefghijklmnopqrstuvwxyz" \
            "ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789_"

    def __init__(self):
        self.reset()

    def reset(self):
        self.pos = 0
        self.level = 0
        self.text = ""

    def parse(self, text):
        """Parses the given text and returns a parse tree.
        """
        self.reset()
        self.text = text
        return self.parse_all()

    def parse_all(self):
        while True:
            dollar = self.text.find("$", self.pos)
            if dollar < 0:
                break
            nextchar = self.text[dollar + 1]
            if nextchar in self.namechars:
                yield _Node("text", self.text[self.pos:dollar])
                self.pos = dollar + 1
                yield self.parse_expr()

            # for supporting ${x.id}, for backward compataility
            elif nextchar == '{':
                saved_pos = self.pos
                self.pos = dollar + 2  # skip "${"
                expr = self.parse_expr()
                if self.text[self.pos] == '}':
                    self.pos += 1
                    yield _Node("text", self.text[self.pos:dollar])
                    yield expr
                else:
                    self.pos = saved_pos
                    break
            else:
                yield _Node("text", self.text[self.pos:dollar + 1])
                self.pos = dollar + 1
                # $$ is used to escape $
                if nextchar == "$":
                    self.pos += 1

        if self.pos < len(self.text):
            yield _Node("text", self.text[self.pos:])

    def match(self):
        match = tokenprog.match(self.text, self.pos)
        if match is None:
            raise "error"
            #raise _ItplError(self.text, self.pos)
        return match, match.end()

    def is_literal(self, text):
        return text and text[0] in "0123456789\"'"

    def parse_expr(self):
        match, pos = self.match()
        print(pos)
        if self.is_literal(match.group()):
            expr = _Node("literal", match.group())
        else:
            expr = _Node("param", self.text[self.pos:pos])
        self.pos = pos
        while self.pos < len(self.text):
            if self.text[self.pos] == "." and \
                self.pos + 1 < len(self.text) and self.text[self.pos + 1] in self.namechars:
                self.pos += 1
                match, pos = self.match()
                attr = match.group()
                expr = _Node("getattr", expr, attr)
                self.pos = pos
            elif self.text[self.pos] == "[":
                saved_pos = self.pos
                self.pos += 1
                key = self.parse_expr()
                if self.text[self.pos] == ']':
                    self.pos += 1
                    expr = _Node("getitem", expr, key)
                else:
                    self.pos = saved_pos
                    break
            else:
                break
        return expr
