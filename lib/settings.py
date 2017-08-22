from lib.custom_exceptions import *
from collections.abc import Mapping

import json
import re


class Settings(Mapping):
   """class for accessing settings"""

   _REPAT = r'(?P<pat>.*?):re(:(?P<flag>[AILMSX]+))?$'

   @staticmethod
   def _get_type_to_one_of():
      """return a dict of string types to one of method"""

      return {
         'primitive': Settings._is_in_prim,
         'list': Settings._is_sublist_in_one_of_lists,
         'dict': Settings._is_dict_in_one_of_dicts
      }

   @staticmethod
   def _is_primitive(val):
      """return True if |val| is a JSON primitive, False otherwise"""

      prims = [int, float, str, bool]
      for prim in prims:
         if isinstance(val, prim):
            return True
      return False

   @staticmethod
   def _is_list(val):
      """return True if |val| is an instance of list, False otherwise"""

      return isinstance(val, list)

   @staticmethod
   def _is_dict(val):
      """return True if |val| is an instance of dict, False otherwise"""

      return isinstance(val, dict)

   @staticmethod
   def _is_wildcard_match(s, wildcard):
      """return True if |wildcard| string matches |s| string. A valid wildcard
      string is in the format of '*[:<type>]`. For instance, '*', '*:str' are
      both valid. Any leading or trailing whitespace in |wildcard| is
      automatically removed. If |wildcard| is invalid, then an
      InvalidWildcardError is raised
      """

      wildcard = wildcard.strip()
      glob_pat = re.compile(r'\*(:(?P<type>\w+))?$')
      m = glob_pat.match(wildcard)
      if m:
         if m.group('type'):
            type_to_meth = globals()['__builtins__']
            type_to_meth = {k:v for k,v in type_to_meth.items()
                        if k in ['str','int','float','bool']}
            try:
               return isinstance(s, type_to_meth[m.group('type')])
            except KeyError:
               raise InvalidWildcardError("{} is an invalid type in {}".format(
                  m.group('type'), wildcard))
         return True
      raise InvalidWildcardError(wildcard)

   @staticmethod
   def _is_regex_match(s, pat):
      """return True if regex pattern string |pat| matches string |s|. A valid
      wildcard string is in the format of '<regex pat>:re[:<flag>[<flag>...]]'.
      For instance, r'\d+:re' or r'h[i]:re:I' are valid. Flags can be stacked
      and valid flags are the same as the single character flags that the
      Python re module uses, i.e. AILMSX. For instance, r'h.i:re:IS' would be
      valid. Trailing whitespace is stripped. If a regex pattern is invalid,
      and InvalidRegexError is raised.
      """

      pat = pat.rstrip()
      m = re.search(Settings._REPAT, pat)
      if m:
         flags_combined = 0
         if m.group('flag'):
            char_to_flag = {
               'A':re.A, 'I':re.I, 'L':re.L, 'M':re.M, 'S':re.S, 'X':re.X}
            for flag in list(m.group('flag')):
               flags_combined |= char_to_flag[flag]
         return bool(re.search(m.group('pat'), s, flags_combined))
      raise InvalidRegexError(pat)

   @staticmethod
   def _is_in_prim(v, valid_v):
      """return True if |v| is in |valid_v|. |v| should be a primitive of
      either int, float, str, or bool. |valid_v| should be a list of any
      possible legal primitive, wildcard, or regex values. |valid_v| can also
      be a single primitive value, which will implicitly be converted to a list
      containing one element. Return False otherwise.
      """

      if not isinstance(valid_v, list):
         valid_v = [valid_v]

      for pat in valid_v:
         if isinstance(pat, str):
            if '*' in pat:
               if Settings._is_wildcard_match(v, pat):
                  return True
            elif re.search(Settings._REPAT, pat):
               if Settings._is_regex_match(str(v), pat):
                  return True
         if v == pat:
            return True
      return False

   @staticmethod
   def _is_sublist_in_one_of_lists(sublist, lists):
      """return True if every element in list |sublist| is in one of the lists
      contained in |lists|, False otherwise. Legal elements in |sublist| or the
      lists in |lists| are any primitive (int, float, str, bool), list, or
      dict. If an illegal element exists in |sublist|, an InvalidSettingError
      is raised
      """

      type_to_one_of = Settings._get_type_to_one_of()

      for vl in lists:
         next_vl = False
         for e in sublist:
            if Settings._is_primitive(e):
               t = 'primitive'
            elif Settings._is_list(e):
               vl = [l for l in vl if isinstance(l, list)]
               t = 'list'
            elif Settings._is_dict(e):
               vl = [d for d in vl if isinstance(d, dict)]
               t = 'dict'
            else:
               raise InvalidSettingError()

            if not type_to_one_of[t](e, vl):
               next_vl = True
               break

         if next_vl:
            continue
         return True
      return False

   @staticmethod
   def _is_dict_in_one_of_dicts(d, dicts):
      """return True if dict |d| is in one of the dicts in |dicts|, False
      otherwise. |dicts| is obviously just a list of dictionaries. Legal
      elements in the dictionaries are the typical primitives (int, float,
      bool, str), lists, and dicts.
      """

      for vd in dicts:
         if Settings._is_in_dict(d, vd):
            return True
      return False

   @staticmethod
   def _is_in_list(l, valid_l):
      """return True if all elements in list |l| is in one of the lists
      contained in |valid_l|, False otherwise. Legal elements in the lists are
      the typical primitives (int, float, bool, str), lists, and dicts.
      """

      for elem in l:
         if Settings._is_primitive(elem):
            if not Settings._is_in_prim(elem, valid_l):
               return False
         elif Settings._is_list(elem):
            valid_lists = [l for l in valid_l if isinstance(l, list)]
            if not Settings._is_sublist_in_one_of_lists(elem, valid_lists):
               return False
         elif Settings._is_dict(elem):
            valid_dicts = [d for d in valid_l if isinstance(d, dict)]
            if not Settings._is_dict_in_one_of_dicts(elem, valid_dicts):
               return False
         else:
            raise InvalidSettingError()
      return True

   @staticmethod
   def _has_all_keys_from(d, valid_d):
      """return True if dict |d| has all keys in dict |valid_d|. False
      otherwise.
      """

      for k, v in valid_d.items():
         if k not in d:
            return False
      return True

   @staticmethod
   def _is_in_dict(d, valid_d):
      """return True if all dict |d| keys are in dict |valid_d|, values in |d|
      are legal values with respect to the valid values defined in |valid_d|,
      and all |valid_d| keys are in |d|. Values in |d| are
      determined legal based on Settings._is_in_prim(), Settings._is_list(), or
      recursively Settings._is_in_dict(). False otherwise.
      """

      for k, v in d.items():
         if k not in valid_d:
            return False
         else:
            if Settings._is_primitive(v):
               if not Settings._is_in_prim(v, valid_d[k]):
                  return False
            elif Settings._is_list(v):
               if not Settings._is_in_list(v, valid_d[k]):
                  return False
            elif Settings._is_dict(v):
               if isinstance(valid_d[k], dict):
                  if not Settings._is_in_dict(v, valid_d[k]):
                     return False
               elif isinstance(valid_d[k], list):
                  if not Settings._is_dict_in_one_of_dicts(v, valid_d[k]):
                     return False
               else:
                  raise InvalidSettingError()
            else:
               raise InvalidSettingError()
      return Settings._has_all_keys_from(d, valid_d)

   @staticmethod
   def _primitive_validity_check(v, valid_v):
      """raise InvalidSettingError if primitive (int, float, bool, str) value
      |v| is not in list |valid_v|
      """

      if not Settings._is_in_prim(v, valid_v):
         raise InvalidSettingError()

   @staticmethod
   def _list_validity_check(l, valid_l):
      """raise InvalidSettingError if list |l| is not in list |valid_l| where
      \"in\" semantics are aligned with Settings._is_in_list(), so see the doc
      for that
      """

      if not Settings._is_in_list(l, valid_l):
         raise InvalidSettingError()

   @staticmethod
   def _dict_validity_check(d, valid_d):
      """raise InvalidSettingError if dict |d| is not in dict |valid_d| where
      \"in\" semantics are aligned with Settings._is_in_dict(), so see the doc
      for that
      """

      if not Settings._is_in_dict(d, valid_d):
         raise InvalidSettingError()

   @staticmethod
   def _validity_check(settings, valid):
      """error check |settings| and |valid|. Both are dict types. |settings|
      represents the user settings where each pair is a setting name associated
      to a chosen setting value. |valid| represents all valid user settings
      where each pair is a setting name associated to legal valid
      setting values.
      """

      Settings._dict_validity_check(settings, valid)

   @staticmethod
   def _inject_defaults(settings, defaults):
      """inject any defaults specified in |defaults| into settings. Default
      values will only be applied if a key exists in |defaults| and doesn't
      exist in |settings|, or if a key in |settings| has an associating value
      of None. If |defaults| is None, |settings| is returned as is.
      """
      new_settings = {}

      if defaults is None:
         return settings
      elif settings is None or len(settings) == 0:
         new_settings = defaults
      else:
         for k, v in settings.items():
            if isinstance(v, dict) or v is None:
               new_settings[k] = Settings._inject_defaults(v, defaults[k])
            else:
               new_settings[k] = settings[k]

         for k, v in defaults.items():
            if k not in settings:
               new_settings[k] = defaults[k]
      return new_settings

   def __init__(self, settings, valid, defaults=None):
      """create a Settings object. |settings| can be a dict or path to json
      file. If a dict, then values in |settings| must be a primitive
      (int, float, bool, str), list, or dict. |valid| must be a dict.
      |settings| represents the user settings where each pair is a setting
      name associated to a chosen setting value. |valid| represents all valid
      user settings where each pair is a setting name associated to possible
      legal setting values. Here's some examples,

      # value associated to 'foo' must be either 'b' or 'a'
      Settings({'foo':'b'}, {'foo':['b','a']}

      # value associated to 'foo' can be a list of either 'a','b','c', and/or 'd'
      Settings({'foo':['a','b']}, {'foo':[['c', 'b', 'd', 'a']]}

      # value associated to 'foo' can be a list of either 'a','b','c', and/or 'd'
      Settings({'foo':['a','b']}, {'foo':[['c', 'b', 'd', 'a']]}

      # value associated to 'foo' can be a list of lists where each nested
      # list can be one or more combinations of
      # ['a'], ['b'], ['c'], ['d'], ['c', 'd'], ['b', 'a']
      # where order doesn't matter. In other words, each user sublist must
      # contain 0 or more elements from any individual valid sublist.
      # A sublist cannot contain a mix of items from two or more valid
      # sublists.
      Settings({'foo':[['a','b']]}, {'foo':[['c', 'd'], ['b', 'a']]}

      # Associating to the example above, this would raise an InvalidSettingError
      Settings({'foo':[['b','d']]}, {'foo':[['c', 'd'], ['b', 'a']]}

      # value associated to 'foo' must have a valid nested dict where 'bar'
      # is the only key accepting values of 'b' or 'a'
      Settings({'foo':{'bar':'a'}}, {'foo':{'bar':['b','a']}})

      # value associated to 'foo' must be one of the valid nested dicts
      Settings({'foo':{'bar':'a'}}, {'foo':[{'baz':['c','d']},{'bar':['b','a']}]})
      Settings({'foo':{'bar':'a','mu':'e'}}, {'foo':[{'baz':['c','d']},{'bar':['b','a'],'mu':['e','f']}]})
      Settings({'foo':{'baz':'d'}}, {'foo':[{'baz':['c','d']},{'bar':['b','a'],'mu':['e','f']}]})

      Finally, the |defaults| dictionary is optional, and specifies any
      default values for any key in the user settings that's nonexistent
      or has an associating value of None. The entries in |defaults| are
      injected into |settings| before the validity check is done. If the
      validity check fails, an InvalidSettingError is raised.
      """

      try:
         with open(settings, 'r') as settings_file:
            self._settings = json.load(settings_file)
      except TypeError:
         self._settings = dict(settings)
      self._settings = Settings._inject_defaults(self._settings, defaults)
      Settings._validity_check(self._settings, valid)

   def __getitem__(self, name):
      """return the value associated to setting name |name|. Raise KeyError
      if not in Settings"""

      return self._settings[name]

   def __iter__(self):
      """return an iterator over the names of the Settings"""

      return iter(self._settings)

   def __len__(self):
      """return the number of settings"""

      return len(self._settings)

   """__contains__(self, item) 
   return True if |item| exists, False otherwise"""

   """keys(self)
   return a new view of the setting names"""

   """items(self)
   return a new view of the setting (name, value) pairs"""

   """get(self, key, default=None)
   return the value for |key| if |key| is a valid setting, else |default|. 
   |default| defaults to None so this method never raises a KeyError"""

   """__eq__(self, other)
   return True if self is equal to |other|, False otherwise"""

   """__ne__(self, other)
   return True if self is not equal to |other|, False otherwise"""
