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
   def _wildcard_validity_check(key, val):
      # TODO
      # glob_pat = re.compile(r'\*(:(?P<type>\w+))?')
      # for s in val[setting]:
      #    m = glob_pat.match(s)
      #    if m:
      #       m.group('type')
      pass

   @staticmethod
   def _is_in_prim(v, valid_v):
      return v in valid_v

   @staticmethod
   def get_type_to_is_in():
      return {
         'primitive': Settings._is_in_prim,
         'list': Settings._is_in_list,
         'dict': Settings._is_in_dict
      }

   @staticmethod
   def _is_sublist_in_one_of_lists(sublist, lists):
      type_to_is_in = Settings.get_type_to_is_in()

      for vl in lists:
         next_vl = False
         for e in sublist:
            if Settings._is_primitive(e):
               t = 'primitive'
            elif Settings._is_list(e):
               e = [e]
               t = 'list'
            elif Settings._is_dict(e):
               t = 'dict'
            else:
               raise InvalidSettingError()

            if not type_to_is_in[t](e, vl):
               next_vl = True
               break

         if next_vl:
            continue
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
            if not Settings._is_in_dict(elem, valid_l):
               return False
      return True

   @staticmethod
   def _is_in_dict():
      pass

   @staticmethod
   def _primitive_validity_check(v, valid_v):
      if not Settings._is_in_prim(v, valid_v):
         raise InvalidSettingError()

   @staticmethod
   def _list_validity_check(l, valid_l):
      idx = 0
      for elem in l:
         if Settings._is_primitive(elem):
            Settings._primitive_validity_check(elem, valid_l[idx])
         idx += 1

   @staticmethod
   def _dict_validity_check(d, valid_d):
      for k, v in d.items():
         if Settings._is_primitive(v):
            Settings._primitive_validity_check(v, valid_d[k])
         elif isinstance(v, list):
            Settings._list_validity_check(v, valid_d[k])
         elif isinstance(v, dict):
            Settings._dict_validity_check(v, valid_d[k])

   @staticmethod
   def _validity_check(settings, valid):
      """error check |settings| and |valid|. Both are dict types. |settings|
      represents the user settings where each pair is a setting name associated
      to a chosen setting value. |valid| represents all valid user settings
      where each pair is a setting name associated to legal valid
      setting values.
      """

      Settings._dict_validity_check(settings, dict)

   @staticmethod
   def _init_defaults(settings, valid):
      """initialize any setting in |settings| dict to its default if the
      setting exists in the |valid| dict, but does not exist in the |settings|
      dict. The default is the first element in the valid list. The |settings|
      dict gets updated.
      """

      for setting, opts in valid.items():
         if setting not in settings:
            settings[setting] = opts[0]

   def __init__(self, settings, valid):
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
      Settings._validity_check(self._settings, valid)
      Settings._init_defaults(self._settings, valid)

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
