from lib.custom_exceptions import *
from collections.abc import Mapping

import json
import re


class Settings(Mapping):
   """class for accessing settings"""

   @staticmethod
   def _is_primitive(val):
      prims = [int, float, str, bool]
      for prim in prims:
         if isinstance(val, prim):
            return True
      return False

   @staticmethod
   def _is_list(val):
      return isinstance(val, list)

   @staticmethod
   def _is_dict(val):
      return isinstance(val, dict)

   @staticmethod
   def _is_wildcard_match(s, wildcard):
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
               raise InvalidWildcard("{} is an invalid type in {}".format(
                  m.group('type'), wildcard))
         return True
      raise InvalidWildcard(wildcard)

   @staticmethod
   def _is_regex_match(s, pat):
      return False

   @staticmethod
   def _is_in_prim(v, valid_v):
      if not isinstance(valid_v, list):
         valid_v = [valid_v]

      for pat in valid_v:
         if isinstance(pat, str):
            if '*' in pat:
               if Settings._is_wildcard_match(v, pat):
                  return True
            elif re.search(r':re$', pat):
               if Settings._is_regex_match(v, pat):
                  return True
         if v == pat:
            return True
      return False

   @staticmethod
   def get_type_to_one_of():
      return {
         'primitive': Settings._is_in_prim,
         'list': Settings._is_sublist_in_one_of_lists,
         'dict': Settings._is_dict_in_one_of_dicts
      }

   @staticmethod
   def _is_sublist_in_one_of_lists(sublist, lists):
      type_to_one_of = Settings.get_type_to_one_of()

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
      for vd in dicts:
         if Settings._is_in_dict(d, vd):
            return True
      return False

   @staticmethod
   def _is_in_list(l, valid_l):
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
   def _is_in_dict(d, valid_d):
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
               if not Settings._is_in_dict(v, valid_d[k]):
                  return False
            else:
               raise InvalidSettingError()
      return True

   @staticmethod
   def _primitive_validity_check(v, valid_v):
      if not Settings._is_in_prim(v, valid_v):
         raise InvalidSettingError()

   @staticmethod
   def _list_validity_check(l, valid_l):
      if not Settings._is_in_list(l, valid_l):
         raise InvalidSettingError()

   @staticmethod
   def _dict_validity_check(d, valid_d):
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
      file. |valid| must be a dict. |settings| represents the user settings
      where each pair is a setting name associated to a chosen setting value.
      |valid| represents all valid user settings where each pair is a setting
      name associated to a list of possible valid setting values. The first
      element in the list is considered the default value for that setting
      if that setting is not defined in |settings|. An empty list
      will raise a NoOptsError, and a setting value in |settings| that
      does not exist in the associated valid values list will raise an
      InvalidSettingError.
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
