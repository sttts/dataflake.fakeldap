##############################################################################
#
# Copyright (c) 2012 Jens Vagelpohl and Contributors. All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.1 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#
##############################################################################

import doctest
import unittest


class ParserTests(unittest.TestCase):

    def _getTargetClass(self):
        from dataflake.fakeldap.queryparser import Parser
        return Parser

    def _makeOne(self):
        klass = self._getTargetClass()
        return klass()

    def test_parse(self):
        parser = self._makeOne()

        query = '(cn=jhunter*)'
        parsed = parser.parse_query(query)
        self.assertEqual( repr(parsed)
                        , "(Filter('cn', '=', 'jhunter*'),)"
                        )

    def test_parse_chained(self):
        parser = self._makeOne()

        query = '(&(objectclass=person)(cn=jhunter*))'
        parsed = parser.parse_query(query)
        self.assertEqual( repr(parsed)
                        , "(Op('&'), (Filter('objectclass', '=', 'person'), Filter('cn', '=', 'jhunter*')))"
                        )

    def test_parse_nestedchain(self):
        parser = self._makeOne()

        query = '(&(objectclass=person)(|(cn=Jeff Hunter)(cn=mhunter*)))'
        parsed = parser.parse_query(query)
        self.assertEqual( repr(parsed)
                        , "(Op('&'), (Filter('objectclass', '=', 'person'), (Op('|'), (Filter('cn', '=', 'Jeff Hunter'), Filter('cn', '=', 'mhunter*')))))"
                        )

    def test_parse_chainwithnegation(self):
        parser = self._makeOne()

        query = '(&(l=USA)(!(sn=patel)))'
        parsed = parser.parse_query(query)
        self.assertEqual( repr(parsed)
                        , "(Op('&'), (Filter('l', '=', 'USA'), (Op('!'), (Filter('sn', '=', 'patel'),))))"
                        )

    def test_parse_negatedchain(self):
        parser = self._makeOne()

        query = '(!(&(drink=beer)(description=good)))'
        parsed = parser.parse_query(query)
        self.assertEqual( repr(parsed)
                        , "(Op('!'), (Op('&'), (Filter('drink', '=', 'beer'), Filter('description', '=', 'good'))))"
                        )

    def test_parse_chainwithdn(self):
        parser = self._makeOne()

        query = '(&(objectclass=person)(dn=cn=jhunter,dc=dataflake,dc=org))'
        parsed = parser.parse_query(query)
        self.assertEqual( repr(parsed)
                        , "(Op('&'), (Filter('objectclass', '=', 'person'), Filter('dn', '=', 'cn=jhunter,dc=dataflake,dc=org')))"
                        )

    def test_parse_convoluted(self):
        parser = self._makeOne()

        query = '(|(&(objectClass=group)(member=cn=test,ou=people,dc=dataflake,dc=org))(&(objectClass=groupOfNames)(member=cn=test,ou=people,dc=dataflake,dc=org))(&(objectClass=groupOfUniqueNames)(uniqueMember=cn=test,ou=people,dc=dataflake,dc=org))(&(objectClass=accessGroup)(member=cn=test,ou=people,dc=dataflake,dc=org)))'
        parsed = parser.parse_query(query)
        self.assertEqual( repr(parsed)
                        , "(Op('|'), (Op('&'), (Filter('objectClass', '=', 'group'), Filter('member', '=', 'cn=test,ou=people,dc=dataflake,dc=org')), Op('&'), (Filter('objectClass', '=', 'groupOfNames'), Filter('member', '=', 'cn=test,ou=people,dc=dataflake,dc=org')), Op('&'), (Filter('objectClass', '=', 'groupOfUniqueNames'), Filter('uniqueMember', '=', 'cn=test,ou=people,dc=dataflake,dc=org')), Op('&'), (Filter('objectClass', '=', 'accessGroup'), Filter('member', '=', 'cn=test,ou=people,dc=dataflake,dc=org'))))"
                        )

    def test_flatten(self):
        from dataflake.fakeldap.op import Op
        from dataflake.fakeldap.queryfilter import Filter

        parser = self._makeOne()
        query = '(&(objectclass=person)(|(cn=Jeff Hunter)(cn=mhunter*)))'
        parsed = parser.parse_query(query)

        self.assertEqual( repr(parser.flatten_query(parsed, klass=Filter))
                        , "(Filter('objectclass', '=', 'person'), Filter('cn', '=', 'Jeff Hunter'), Filter('cn', '=', 'mhunter*'))"
                        )
        self.assertEqual( repr(parser.flatten_query(parsed, klass=Op))
                        , "(Op('&'), Op('|'))"
                        )

def test_suite():
    from dataflake.fakeldap import queryparser
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(ParserTests))
    suite.addTest(doctest.DocTestSuite(queryparser))
    return suite
