import unittest
from lib.others import Others
from unittest.mock import MagicMock
from tests.test_helpers import MockRestore
import os


class OthersTest(unittest.TestCase):
   """unit tests for Others class"""

   def mock_query_user(self):
      """side effect method to mock yielded values of Others._query_user
      using self.mockdat
      """

      for o in self.mockdat:
         yield o

   def setUp(self):
      """instantiate an Others object and an empty mock data list"""

      self.others = Others()
      self.mockdat = []

   def test_regex(self):
      """test the regex for full matches"""

      self.assertTrue(Others._pat.fullmatch(' administrator                             2  Disc           41  7/14/2017 2:33 PM'))
      self.assertTrue(Others._pat.fullmatch('>knavero                             2  Disc           41  7/14/2017 2:33 PM'))
      self.assertTrue(Others._pat.fullmatch('>knavero               console             3  Active         40  7/13/2017 4:44 PM'))
      self.assertTrue(Others._pat.fullmatch(' knavero               console             3  Active         40  7/13/2017 4:44 PM'))
      self.assertTrue(Others._pat.fullmatch(' knavero               console             3  Active         20:40  7/13/2017 4:44 PM'))
      self.assertFalse(Others._pat.fullmatch(' knavero               console             3  Active         20:40  7/13/2017 444 PM'))

   def test_logged_on_usernames(self):
      """test the usernames tuple returned by Others.logged_on_usernames
      property
      """

      others = self.others

      self.mockdat = [
         {'username': 'administrator', 'sessionname': None, 'id': '2',
          'state': 'Disc', 'idletime': '57', 'logontime': '7/14/2017 2:33 PM'},
         {'username': 'knavero', 'sessionname': 'console', 'id': '3',
          'state': 'Active', 'idletime': '56', 'logontime': '7/13/2017 4:44 PM'},
         {'username': 'foo', 'sessionname': None, 'id': '4', 'state': 'Disc',
          'idletime': '56', 'logontime': '7/14/2017 2:37 PM'}
      ]

      with MockRestore(Others, '_query_user',
                       MagicMock(side_effect=self.mock_query_user)):
         users = others.logged_on_usernames
         self.assertIn('administrator', users)
         self.assertIn('knavero', users)
         self.assertIn('foo', users)
         self.assertEqual(len(users), 3)

   def test_is_logged_on(self):
      """test the Others.is_logged_on() method"""

      others = self.others

      self.mockdat = [
         {'username': 'administrator', 'sessionname': None, 'id': '2',
          'state': 'Disc', 'idletime': '57', 'logontime': '7/14/2017 2:33 PM'},
         {'username': "{}".format(os.environ['USERNAME'].lower()),
          'sessionname': 'console', 'id': '3', 'state': 'Active',
          'idletime': '56', 'logontime': '7/13/2017 4:44 PM'},
         {'username': 'foo', 'sessionname': None, 'id': '4', 'state': 'Disc',
          'idletime': '56', 'logontime': '7/14/2017 2:37 PM'}
      ]

      with MockRestore(Others, '_query_user',
                       MagicMock(side_effect=self.mock_query_user)):
         self.assertTrue(others.is_logged_on())
         self.assertFalse(others.is_logged_on('administrator', 'foo'))
         self.assertTrue(others.is_logged_on('administrator'))
         self.assertTrue(others.is_logged_on('foo'))

      self.mockdat = [
         {'username': "{}".format(os.environ['USERNAME'].lower()),
          'sessionname': 'console', 'id': '3', 'state': 'Active',
          'idletime': '56', 'logontime': '7/13/2017 4:44 PM'}
      ]

      with MockRestore(Others, '_query_user',
                       MagicMock(side_effect=self.mock_query_user)):
         self.assertFalse(others.is_logged_on())

if __name__ == '__main__':
   unittest.main()
   