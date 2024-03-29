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

from dataflake.fakeldap.tests.base import FakeLDAPTests


class FakeLDAPModifyTests(FakeLDAPTests):

    def test_modify_wrongbase(self):
        import ldap
        conn = self._makeOne()
        self.assertRaises( ldap.NO_SUCH_OBJECT
                         , conn.modify_s
                         , 'cn=foo,o=base'
                         , []
                         )

    def test_modify_wrongrecord(self):
        import ldap
        conn = self._makeOne()
        self._addUser('foo')

        self.assertRaises( ldap.NO_SUCH_OBJECT
                         , conn.modify_s
                         , 'cn=bar,ou=users,dc=localhost'
                         , []
                         )

    def test_modify_success(self):
        import copy
        from ldap.modlist import modifyModlist
        conn = self._makeOne()
        self._addUser('foo')

        foo = conn.search_s('ou=users,dc=localhost', query='(cn=foo)')
        old_values = foo[0][1]
        self.assertEquals(old_values['objectClass'], ['top', 'person'])
        self.failIf(old_values.get('mail'))
        new_values = copy.deepcopy(old_values)
        new_values['objectClass'] = ['top', 'inetOrgPerson']
        new_values['mail'] = ['foo@email.com']

        modlist = modifyModlist(old_values, new_values)
        conn.modify_s('cn=foo,ou=users,dc=localhost', modlist)
        foo = conn.search_s('ou=users,dc=localhost', query='(cn=foo)')
        self.assertEquals( foo[0][1]['objectClass']
                         , ['top', 'inetOrgPerson']
                         )
        self.assertEquals( foo[0][1]['mail']
                         , ['foo@email.com']
                         )

    def test_modify_replace(self):
        import ldap

        conn = self._makeOne()
        self._addUser('foo', mail='foo@bar.com')

        foo = conn.search_s('ou=users,dc=localhost', query='(cn=foo)')
        old_values = foo[0][1]
        self.assertEqual(old_values['mail'], ['foo@bar.com'])

        modlist = [(ldap.MOD_REPLACE, 'mail', ['foo@email.com'])]
        conn.modify_s('cn=foo,ou=users,dc=localhost', modlist)
        foo = conn.search_s('ou=users,dc=localhost', query='(cn=foo)')
        self.assertEquals(foo[0][1]['mail'], ['foo@email.com'])

    def test_modify_add(self):
        import ldap

        conn = self._makeOne()
        self._addUser('foo', mail='foo@bar.com')

        foo = conn.search_s('ou=users,dc=localhost', query='(cn=foo)')
        old_values = foo[0][1]
        self.assertEqual(old_values['mail'], ['foo@bar.com'])

        modlist = [(ldap.MOD_ADD, 'mail', ['foo@email.com'])]
        conn.modify_s('cn=foo,ou=users,dc=localhost', modlist)
        foo = conn.search_s('ou=users,dc=localhost', query='(cn=foo)')
        self.assertEquals( set(foo[0][1]['mail'])
                         , set(['foo@email.com', 'foo@bar.com'])
                         )

    def test_modrdn_wrongbase(self):
        import ldap
        conn = self._makeOne()
        self.assertRaises( ldap.NO_SUCH_OBJECT
                         , conn.modrdn_s
                         , 'cn=foo,o=base'
                         , 'cn=bar'
                         )

    def test_modrdn_wrongrecord(self):
        import ldap
        conn = self._makeOne()
        self._addUser('foo')

        self.assertRaises( ldap.NO_SUCH_OBJECT
                         , conn.modrdn_s
                         , 'cn=bar,ou=users,dc=localhost'
                         , 'cn=baz'
                         )

    def test_modrdn_existing_clash(self):
        import ldap
        conn = self._makeOne()
        self._addUser('foo')
        self._addUser('bar')

        self.assertRaises( ldap.ALREADY_EXISTS
                         , conn.modrdn_s
                         , 'cn=foo,ou=users,dc=localhost'
                         , 'cn=bar'
                         )

    def test_modrdn_success(self):
        import ldap
        conn = self._makeOne()
        self._addUser('foo')

        foo = conn.search_s( 'cn=foo,ou=users,dc=localhost'
                           , scope=ldap.SCOPE_BASE
                           , query='(objectClass=*)'
                           )
        self.failUnless(foo)
        self.assertRaises( ldap.NO_SUCH_OBJECT
                         , conn.search_s
                         , 'cn=bar,ou=users,dc=localhost'
                         , scope=ldap.SCOPE_BASE
                         , query='(objectClass=*)'
                         )

        conn.modrdn_s('cn=foo,ou=users,dc=localhost', 'cn=bar')
        self.assertRaises( ldap.NO_SUCH_OBJECT
                         , conn.search_s
                         , 'cn=foo,ou=users,dc=localhost'
                         , scope=ldap.SCOPE_BASE
                         , query='(objectClass=*)'
                         )
        bar = conn.search_s( 'cn=bar,ou=users,dc=localhost'
                           , scope=ldap.SCOPE_BASE
                           , query='(objectClass=*)'
                           )
        self.failUnless(bar)

