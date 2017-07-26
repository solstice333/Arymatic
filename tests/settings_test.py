import unittest
from lib.settings import Settings
from lib.custom_exceptions import *
import json
import os
from unittest.mock import MagicMock
from tests.mock_restore import MockRestore

class SettingsTest(unittest.TestCase):
   def setUp(self):
      self.settings = Settings({'foo': 1, 'bar': 'barval'},
                               {'foo': [1], 'bar': ['barval']})
      self.empty_settings = Settings({}, {})
      self.same =  Settings({'bar':'barval','foo':1},
               {'foo':[1],'bar':['barval']})
      self.slightly_diff = Settings({'bar': 'barval', 'fooo': 1},
                           {'fooo': [1], 'bar': ['barval']})

      with open('foo_settings.json', 'w') as settings:
         json.dump({'foo': 1, 'bar': 'barval'}, settings)

   def test_ctor(self):
      s = Settings({'foo': 1}, {'foo': [0, 1]})
      self.assertIsInstance(s, Settings)
      s = Settings({'foo': 0}, {'foo': [0, 1]})
      self.assertIsInstance(s, Settings)
      s = Settings({'foo': 0, 'bar': 'barval'},
                   {'foo': [0, 1], 'bar': ['barval', 'barval2']})
      self.assertIsInstance(s, Settings)
      s = Settings({'foo': 0, 'bar': 'barval2'},
                   {'foo': [0, 1], 'bar': ['barval', 'barval2']})
      self.assertIsInstance(s, Settings)

      with self.assertRaises(InvalidSettingError):
         s = Settings({'foo': 1}, {'foo': [0, 2]})
      with self.assertRaises(InvalidSettingError):
         s = Settings({'foo': 0, 'bar': 'barval'},
                   {'foo': [0, 1], 'bar': ['barval1', 'barval2']})

      with self.assertRaises(NoOptsError):
         s = Settings({'foo':0, 'bar':'barr'}, {'foo':[1, 0], 'bar':[]})

      s = Settings({}, {'foo':[1, 0], 'bar':['barval', 'barval2']})
      self.assertEqual(s['bar'], 'barval')
      self.assertEqual(s['foo'], 1)

   def test_ctor_with_settings_file(self):
      s = Settings('foo_settings.json',
                   {'foo':[0, 1], 'bar':['barval', 'barval2']})
      with self.assertRaises(InvalidSettingError):
         Settings('foo_settings.json',
                  {'foo':[0, 2], 'bar':['barval', 'barval2']})
      with self.assertRaises(InvalidSettingError):
         Settings('foo_settings.json',
                  {'foo':[0, 1], 'bar':['barval2', 'barval3']})

   def test_getitem(self):
      s = self.settings
      self.assertEqual(s['foo'], 1)
      self.assertEqual(s['bar'], 'barval')
      with self.assertRaises(KeyError):
         s['baz']

   def test_iter(self):
      s = self.settings
      self.assertEqual(sorted(list(iter(s))), ['bar', 'foo'])
      s = self.empty_settings
      self.assertEqual(list(iter(s)), [])

   def test_len(self):
      s = self.settings
      self.assertEqual(len(s), 2)
      s = self.empty_settings
      self.assertEqual(len(s), 0)

   def test_contains(self):
      s = self.settings
      self.assertTrue('foo' in s)
      self.assertTrue('bar' in s)
      self.assertFalse('baz' in s)
      s = self.empty_settings
      self.assertFalse('foo' in s)

   def test_keys(self):
      s = self.settings
      self.assertEqual(sorted(s.keys()), ['bar', 'foo'])
      s = self.empty_settings
      self.assertEqual(list(s.keys()), [])

   def test_values(self):
      s = self.settings
      self.assertEqual(sorted([str(v) for v in s.values()]), ['1', 'barval'])
      self.assertTrue(1 in s.values())
      self.assertTrue('barval' in s.values())

   def test_get(self):
      s = self.settings
      self.assertEqual(s.get('foo'), 1)
      self.assertEqual(s.get('bar'), 'barval')
      self.assertIsNone(s.get('baz'))
      self.assertEqual(s.get('baz', 0), 0)
      s = self.empty_settings
      self.assertIsNone(s.get('foo'))

   def test_eq(self):
      s = self.settings
      s2 = self.same
      self.assertEqual(s, s2)
      self.assertIsNot(s, s2)

   def test_ne(self):
      s = self.settings
      self.assertNotEqual(s, self.slightly_diff)
      self.assertNotEqual(s, self.empty_settings)

   def tearDown(self):
      os.remove('foo_settings.json')
