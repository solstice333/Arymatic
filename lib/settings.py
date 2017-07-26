import json
from lib.custom_exceptions import *
from collections.abc import Mapping

class Settings(Mapping):
   """class for accessing settings"""

   @staticmethod
   def _validity_check(settings, valid):
      """error check |settings| and |valid|. Both are dict types. |settings|
      represents the user settings where each pair is a setting name associated
      to a chosen setting value. |valid| represents all valid user settings
      where each pair is a setting name associated to a list of possible valid
      setting values. An empty list value will raise a NoOptsError, and a
      setting value in |settings| that does not exist in the associated valid
      values list will raise an InvalidSettingError.
      """

      for setting, opts in valid.items():
         if len(opts) == 0:
            raise NoOptsError(setting)
      for setting, option in settings.items():
         if setting not in valid or option not in valid[setting]:
            raise InvalidSettingError(setting, option)

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
