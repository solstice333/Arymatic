import unittest
from lib.settings import Settings
from lib.custom_exceptions import *
import json
import os
from unittest.mock import MagicMock
from tests.mock_restore import MockRestore

class SettingsTest(unittest.TestCase):

   def test_is_in_prim(self):
      self.assertTrue(Settings._is_in_prim('z', ['x', 'y', 'z']))
      self.assertTrue(Settings._is_in_prim('x', ['x', 'y', 'z']))
      self.assertTrue(Settings._is_in_prim('y', ['x', 'y', 'z']))
      self.assertFalse(Settings._is_in_prim('a', ['x', 'y', 'z']))

   def test_is_in_list(self):
      self.assertTrue(Settings._is_in_list(['x','y'], ['a','y','c','x']))
      self.assertTrue(Settings._is_in_list([['x']], [['z'], ['x','y']]))
      self.assertTrue(Settings._is_in_list([['x']], [['z'], ['x','a']]))
      self.assertFalse(Settings._is_in_list([['x']], [['z'], ['b','a']]))
      self.assertTrue(Settings._is_in_list([['x']], [['z'], ['b','a'], ['y','x']]))
      self.assertTrue(Settings._is_in_list([['y']], [['z'], ['b','a'], ['y','x']]))
      self.assertFalse(Settings._is_in_list([['c']], [['z'], ['b','a'], ['y','x']]))
      self.assertFalse(Settings._is_in_list([['c','x']], [['z'], ['b','a'], ['y','x']]))
      self.assertFalse(Settings._is_in_list([['c','x']], [['z'], ['b','c','a'], ['y','x']]))
      self.assertTrue(Settings._is_in_list([['c','x']], [['z'], ['b','c','a'], ['y','x','z','c','f']]))
      self.assertTrue(Settings._is_in_list([['c','x','z']], [['z'], ['b','c','a'], ['y','x','z','c','f']]))
      self.assertFalse(Settings._is_in_list([['c','x','b']], [['z'], ['b','c','a'], ['y','x','z','c','f']]))
      self.assertTrue(Settings._is_in_list([[[[['a'], ['y']]]]], [[[[['a', 'b', 'c', 'y', 'z']]]]]))
      self.assertFalse(Settings._is_in_list([[[['a'], ['y']]]], [[[[['a', 'b', 'c', 'y', 'z']]]]]))
      self.assertTrue(Settings._is_in_list([[[[['a','c'], ['y']]]]], [[[[['y', 'z'], ['a', 'b', 'c']]]]]))
      self.assertFalse(Settings._is_in_list([[[['a','c'], ['y']]]], [[[[['y','z'],['a', 'b', 'c']]]]]))
      self.assertFalse(Settings._is_in_list([[[[['a','y'], ['c']]]]], [[[[['y', 'z'], ['a', 'b', 'c']]]]]))

   def test_is_in_dict(self):
      self.assertTrue(Settings._is_in_dict({'a':'b'}, {'c':['d'],'a':['b']}))
      self.assertFalse(Settings._is_in_dict({'a':'b'}, {'c':['d'],'a':['c']}))
      self.assertTrue(Settings._is_in_dict({'a':['b','c']}, {'d':['e','f'],'a':['x','c','g','b','h']}))
      self.assertFalse(Settings._is_in_dict({'a':['b','c']}, {'d':['e','f'],'a':['x','c','g','i','h']}))
      self.assertTrue(Settings._is_in_dict({'a':{'b':'c'}}, {'d':['e'],'a':{'f':['g'],'b':['h','c']}}))
      self.assertFalse(Settings._is_in_dict({'a':{'b':'c'}}, {'d':['e'],'a':{'f':['g'],'b':['h','i']}}))

      self.assertTrue(Settings._is_in_dict(
         {'a': ['b', ['c']]},
         {'d': ['e', 'f'], 'a': ['x', ['c', 'g'], 'b', 'h']}))
      self.assertFalse(Settings._is_in_dict(
         {'a': ['b', ['c']]},
         {'d': ['e', 'f'], 'a': ['x', 'c', ['g', 'i'], 'h', 'b']}))
      self.assertFalse(Settings._is_in_dict(
         {'a': ['b', ['c']]},
         {'d': ['e', 'f'], 'a': ['x', ['c', 'g', 'i'], 'h']}))

   def test_list_with_dict(self):
      self.assertTrue(Settings._is_in_list(
         [{'a':'d'}],
         [{'a':['d']}]))
      self.assertTrue(Settings._is_in_list(
         [{'a':{'c': 'd'}}],
         [{'e':['f'],'a':{'h':['i'],'c':['d']}}]))
      self.assertTrue(Settings._is_in_list(
         [['y'],[{'f':'g'}]],
         [['y', 'z'],[{'j':['k'],'f':['g']}]]))
      self.assertTrue(Settings._is_in_list(
         [[[[['b', {'a': {'c': 'd'}}], ['y'], [{'f': 'g'}]]]]],
         [[[[['y', 'z'], [{'e': ['f'], 'a': {'h': ['i'], 'c': ['d']}}, 'a', 'b', 'c'], [{'j': ['k'], 'f': ['g']}]]]]]))
      self.assertFalse(Settings._is_in_list(
         [[[[['f', {'a': {'c': 'd'}}], ['y'], [{'f': 'g'}]]]]],
         [[[[['y', 'z'], [{'e': ['f'], 'a': {'h': ['i'], 'c': ['d']}}, 'a', 'b', 'c'], [{'j': ['k'], 'f': ['g']}]]]]]))
      self.assertFalse(Settings._is_in_list(
         [[[[[{'a': {'c': 'd'}}], ['yy'], [{'f': 'g'}]]]]],
         [[[[['y', 'z'], [{'e': ['f'], 'a': {'h': ['i'], 'c': ['d']}}, 'a', 'b', 'c'], [{'j': ['k'], 'f': ['g']}]]]]]))
      self.assertFalse(Settings._is_in_list(
         [[[[[{'a': {'c': 'd'}}], ['y'], [{'f': 'h'}]]]]],
         [[[[['y', 'z'], [{'e': ['f'], 'a': {'h': ['i'], 'c': ['d']}}, 'a', 'b', 'c'], [{'j': ['k'], 'f': ['g']}]]]]]))
      self.assertFalse(Settings._is_in_list(
         [[[{'a': {'c': 'e'}}]]],
         [[[{'e': ['f'], 'a': {'h': ['i'], 'c': ['d']}}, 'a', 'b', 'c']]]))
      self.assertFalse(Settings._is_in_list(
         [[[[[{'a': {'c': 'e'}}], ['y'], [{'f': 'g'}]]]]],
         [[[[['y', 'z'], [{'e': ['f'], 'a': {'h': ['i'], 'c': ['d']}}, 'a', 'b', 'c'], [{'j': ['k'], 'f': ['g']}]]]]]))

   def test_default_injection(self):
      self.assertEqual(
         Settings._inject_defaults({}, None),
         {})

      self.assertEqual(
         Settings._inject_defaults({}, {'foo': 'foov'}),
         {'foo': 'foov'})
      self.assertEqual(
         Settings._inject_defaults({'foo': 'bar'}, {'foo': 'foov'}),
         {'foo': 'bar'})
      self.assertEqual(
         Settings._inject_defaults({'foo': None}, {'foo': 'foov'}),
         {'foo': 'foov'})
      self.assertEqual(
         Settings._inject_defaults(
            {'foo':'foov','bar':None},
            {'foo':'foo_default','bar':'bar_default','baz':'baz_default'}),
         {'foo':'foov','bar':'bar_default','baz':'baz_default'}
      )

      self.assertEqual(
         Settings._inject_defaults({'foo':{}}, {'foo':{'bar':'baz'}}),
         {'foo':{'bar':'baz'}}
      )
      self.assertEqual(
         Settings._inject_defaults({'foo':{'bar':'barv'}}, {'foo':{'bar':'barv','baz':'bazv'}}),
         {'foo':{'bar':'barv','baz':'bazv'}}
      )

   def test_primitive_validity(self):
      Settings._primitive_validity_check('x', ['x','y','z'])
      Settings._primitive_validity_check('z', ['x','y','z'])

      with self.assertRaises(InvalidSettingError):
         Settings._primitive_validity_check('a', ['x','y','z'])

   def test_list_validity(self):
      Settings._list_validity_check(['x','y'], ['x','y','z'])
      Settings._list_validity_check(['x','y'], ['x','y','z'])
      with self.assertRaises(InvalidSettingError):
         Settings._list_validity_check(['a','y'], ['x','y','z'])
      Settings._list_validity_check([['x','y'],['a']], [['b','a'],['x','y','z']])
      with self.assertRaises(InvalidSettingError):
         Settings._list_validity_check([['x','y'],['c']], [['b','a'],['x','y','z']])

   def test_dict_validity(self):
      Settings._dict_validity_check({'foo':'foov'},{'foo':['foov']})
      with self.assertRaises(InvalidSettingError):
         Settings._dict_validity_check({'foo':'foov'},{'foo':['foovv']})
      Settings._dict_validity_check({'foo':{'bar':'barv'}},{'foo':{'baz':['bazv'],'bar':['barvv','barv']}})
      Settings._dict_validity_check({'foo':{'bar':'barv'}},{'foo':{'baz':['bazv'],'bar':'barv'}})
      with self.assertRaises(InvalidSettingError):
         Settings._dict_validity_check({'foo':{'bar':'barv'}},{'foo':{'baz':['bazv'],'bar':'barvv'}})

   def test_wildcard_validity(self):
      self.assertTrue(Settings._is_wildcard_match('foo', '*'))
      self.assertTrue(Settings._is_wildcard_match(3, '*'))
      self.assertTrue(Settings._is_wildcard_match(False, '*'))
      self.assertTrue(Settings._is_wildcard_match(3.5, '*'))

      self.assertTrue(Settings._is_wildcard_match('foo', '*:str'))
      self.assertFalse(Settings._is_wildcard_match('foo', '*:bool'))
      self.assertTrue(Settings._is_wildcard_match(True, '*:bool'))
      self.assertFalse(Settings._is_wildcard_match(3, '*:bool'))
      self.assertTrue(Settings._is_wildcard_match(3, '*:int'))
      self.assertFalse(Settings._is_wildcard_match(3.5, '*:int'))
      self.assertTrue(Settings._is_wildcard_match(3.5, '*:float'))
      self.assertFalse(Settings._is_wildcard_match('foo', '*:float'))

      with self.assertRaises(InvalidWildcard):
         Settings._is_wildcard_match(3.5, '*:foo')

      self.assertTrue(Settings._is_in_prim('foo', '*'))
      self.assertTrue(Settings._is_in_prim('foo', '*:str'))
      self.assertFalse(Settings._is_in_prim('foo', '*:bool'))

      Settings._validity_check({'foo':'bar'}, {'foo':'*'})
      Settings._validity_check({'foo':'bar'}, {'foo':'*:str'})
      with self.assertRaises(InvalidSettingError):
         Settings._validity_check({'foo':'bar'}, {'foo':'*:bool'})

   def test_is_regex_match(self):
      self.assertTrue(Settings._is_regex_match('foo', r'\w+:re'))
      self.assertTrue(Settings._is_regex_match('foo', r'F\w:re:I'))
      self.assertFalse(Settings._is_regex_match('foo', r'F\w$:re:I'))
      self.assertTrue(Settings._is_regex_match('foo', r'F\w+:re:I '))
      with self.assertRaises(InvalidRegex):
         self.assertTrue(Settings._is_regex_match('foo', r'F\w+:re:I Z'))
      with self.assertRaises(InvalidRegex):
         self.assertTrue(Settings._is_regex_match('foo', r'F\w+:re:i'))
      self.assertFalse(Settings._is_regex_match("f\no", r'...:re'))
      self.assertTrue(Settings._is_regex_match("f\no", r'...:re:S'))
      self.assertFalse(Settings._is_regex_match("f\no", r'F..:re:S'))
      self.assertFalse(Settings._is_regex_match("f\no", r'F..:re:I'))
      self.assertTrue(Settings._is_regex_match("f\no", r'F..:re:IS'))
      self.assertTrue(Settings._is_regex_match("f\no", r'F..:re:SI'))

      with self.assertRaises(InvalidSettingError):
         Settings._validity_check({'foo': 'bar'}, {'foo': r'B\w+:re'})
      Settings._validity_check({'foo': 'bar'}, {'foo': r'B\w:re:I'})
      Settings._validity_check({'foo': 'b\nr'}, {'foo': r'B.\w:re:IS'})
      with self.assertRaises(InvalidSettingError):
         Settings._validity_check({'foo': 'b\nr'}, {'foo': r'B.\w:re:I'})
      Settings._validity_check({'foo':{'baz':'b\nr'}}, {'foo':{'baz':r'B.\w:re:IS'}})

   def test_ctor(self):
      s = Settings({'foo': 0}, {'foo': [0, 1]})
      s = Settings({'foo': 1}, {'foo': [0, 1]})
      s = Settings({'foo': 0, 'bar': 'barval'},
                   {'foo': [0, 1], 'bar': ['barval', 'barval2']})
      s = Settings({'foo': 0, 'bar': 'barval2'},
                   {'foo': [0, 1], 'bar': ['barval', 'barval2']})

      # with self.assertRaises(InvalidSettingError):
      #    s = Settings({'foo': 1}, {'foo': [0, 2]})
      # with self.assertRaises(InvalidSettingError):
      #    s = Settings({'foo': 0, 'bar': 'barval'},
      #                 {'foo': [0, 1], 'bar': ['barval1', 'barval2']})
      #
      # with self.assertRaises(NoOptsError):
      #    s = Settings({'foo': 0, 'bar': 'barr'}, {'foo': [1, 0], 'bar': []})
      #
      # # TODO: implement multiple values in list validation
      # s = Settings({'foo': ['a', 'b']}, {'foo': ['a', 'b', 'c']})
      #
      # # TODO: implement dicts contained in list validation
      # s = Settings(
      #    {'foo': [{'bar': 3}, {'baz': 4}]},
      #    {'foo': [
      #       {'bar': [4, 3]},
      #       {'baz': [4, 5]},
      #       {'mu': [6, 7]}
      #    ]})
      #
      # # TODO implment nested dict validation
      # s = Settings(
      #    {'foo': {'bar': 'baz'}},
      #    {'foo': [
      #       {'bar': ['mu', 'baz']},
      #       {'gar': ['gu', 'gaz']}
      #    ]})

         # def setUp(self):
   #    self.settings = Settings({'foo': 1, 'bar': 'barval'},
   #                             {'foo': [1], 'bar': ['barval']})
   #    self.empty_settings = Settings({}, {})
   #    self.same =  Settings({'bar':'barval','foo':1},
   #             {'foo':[1],'bar':['barval']})
   #    self.slightly_diff = Settings({'bar': 'barval', 'fooo': 1},
   #                         {'fooo': [1], 'bar': ['barval']})
   #
   #    with open('foo_settings.json', 'w') as settings:
   #       json.dump({'foo': 1, 'bar': 'barval'}, settings)
   #

   # def test_defaults(self):
   #    s = Settings({}, {'foo': [1, 0], 'bar': ['barval', 'barval2']})
   #    self.assertEqual(s['bar'], 'barval')
   #    self.assertEqual(s['foo'], 1)
   #
   # def test_ctor_with_settings_file(self):
   #    s = Settings('foo_settings.json',
   #                 {'foo':[0, 1], 'bar':['barval', 'barval2']})
   #    with self.assertRaises(InvalidSettingError):
   #       Settings('foo_settings.json',
   #                {'foo':[0, 2], 'bar':['barval', 'barval2']})
   #    with self.assertRaises(InvalidSettingError):
   #       Settings('foo_settings.json',
   #                {'foo':[0, 1], 'bar':['barval2', 'barval3']})
   #
   #
   #
   # def test_wildcard(self):
   #    # TODO: implement '*' wildcard with type specifier for instance, '*:str' meaning any string
   #    s = Settings({'foo': 1}, {'foo': '*'})
   #    s = Settings({'foo': 'val'}, {'foo': '*:str'})
   #    s = Settings({'foo': 'val'}, {'foo': '*:int,str'})
   #    s = Settings({'foo': 2.4}, {'foo': '*:float'})
   #    s = Settings({'foo': True}, {'foo': '*:bool'})
   #
   #    with self.assertRaises(InvalidSettingError):
   #       s = Settings({'foo': 'val'}, {'foo': '*:int'})
   #    with self.assertRaises(InvalidSettingError):
   #       s = Settings({'foo': 'val'}, {'foo': '*:bool'})
   #    with self.assertRaises(InvalidSettingError):
   #       s = Settings({'foo': 'val'}, {'foo': '*:float'})
   #    with self.assertRaises(InvalidSettingError):
   #       s = Settings({'foo': True}, {'foo': '*:str'})
   #
   # def test_getitem(self):
   #    s = self.settings
   #    self.assertEqual(s['foo'], 1)
   #    self.assertEqual(s['bar'], 'barval')
   #    with self.assertRaises(KeyError):
   #       s['baz']
   #
   # def test_iter(self):
   #    s = self.settings
   #    self.assertEqual(sorted(list(iter(s))), ['bar', 'foo'])
   #    s = self.empty_settings
   #    self.assertEqual(list(iter(s)), [])
   #
   # def test_len(self):
   #    s = self.settings
   #    self.assertEqual(len(s), 2)
   #    s = self.empty_settings
   #    self.assertEqual(len(s), 0)
   #
   # def test_contains(self):
   #    s = self.settings
   #    self.assertTrue('foo' in s)
   #    self.assertTrue('bar' in s)
   #    self.assertFalse('baz' in s)
   #    s = self.empty_settings
   #    self.assertFalse('foo' in s)
   #
   # def test_keys(self):
   #    s = self.settings
   #    self.assertEqual(sorted(s.keys()), ['bar', 'foo'])
   #    s = self.empty_settings
   #    self.assertEqual(list(s.keys()), [])
   #
   # def test_values(self):
   #    s = self.settings
   #    self.assertEqual(sorted([str(v) for v in s.values()]), ['1', 'barval'])
   #    self.assertTrue(1 in s.values())
   #    self.assertTrue('barval' in s.values())
   #
   # def test_get(self):
   #    s = self.settings
   #    self.assertEqual(s.get('foo'), 1)
   #    self.assertEqual(s.get('bar'), 'barval')
   #    self.assertIsNone(s.get('baz'))
   #    self.assertEqual(s.get('baz', 0), 0)
   #    s = self.empty_settings
   #    self.assertIsNone(s.get('foo'))
   #
   # def test_eq(self):
   #    s = self.settings
   #    s2 = self.same
   #    self.assertEqual(s, s2)
   #    self.assertIsNot(s, s2)
   #
   # def test_ne(self):
   #    s = self.settings
   #    self.assertNotEqual(s, self.slightly_diff)
   #    self.assertNotEqual(s, self.empty_settings)
   #
   # def tearDown(self):
   #    os.remove('foo_settings.json')
