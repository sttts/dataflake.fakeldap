##############################################################################
#
# Copyright (c) 2008-2012 Jens Vagelpohl and Contributors. All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.1 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#
##############################################################################

import unittest

from dataflake.fakeldap.tests.base import FakeLDAPTests

class FakeLDAPModifyTests(FakeLDAPTests):

    def test_add_wrongbase(self):
        import ldap
        conn = self._makeOne()
        self.assertRaises( ldap.NO_SUCH_OBJECT
                         , conn.add_s
                         , 'cn=foo,o=base'
                         , []
                         )

    def test_add_existing_clash(self):
        import ldap
        conn = self._makeOne()
        self._addUser('foo')

        self.assertRaises( ldap.ALREADY_EXISTS
                         , conn.add_s
                         , 'cn=foo,ou=users,dc=localhost'
                         , []
                         )

    def test_add_success(self):
        import copy
        from ldap.modlist import addModlist
        conn = self._makeOne()
        self._addUser('foo')

        foo = conn.search_s('ou=users,dc=localhost', query='(cn=foo)')
        bar_values = copy.deepcopy(foo[0][1])
        bar_values['cn'] = ['bar']
        modlist = addModlist(bar_values)

        self.failIf(conn.search_s('ou=users,dc=localhost', query='(cn=bar)'))
        conn.add_s('cn=bar,ou=users,dc=localhost', modlist)
        self.failUnless(conn.search_s('ou=users,dc=localhost', query='(cn=bar)'))

    def test_delete_wrongbase(self):
        import ldap
        conn = self._makeOne()
        self.assertRaises(ldap.NO_SUCH_OBJECT, conn.delete_s, 'cn=foo,o=base')

    def test_modrdn_wrongrecord(self):
        import ldap
        conn = self._makeOne()
        self._addUser('foo')

        self.assertRaises( ldap.NO_SUCH_OBJECT
                         , conn.delete_s
                         , 'cn=bar,ou=users,dc=localhost'
                         )

    def test_delete_success(self):
        import ldap
        conn = self._makeOne()
        self._addUser('foo')

        foo = conn.search_s('ou=users,dc=localhost', query='(cn=foo)')
        self.failUnless(foo)
        conn.delete_s('cn=foo,ou=users,dc=localhost')
        foo = conn.search_s('ou=users,dc=localhost', query='(cn=foo)')
        self.failIf(foo)

