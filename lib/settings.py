import json
from lib.custom_exceptions import *
from collections.abc import Mapping

class Settings(Mapping):
   @staticmethod
   def _validity_check(settings, valid):
      for setting, option in settings.items():
         if setting not in valid or option not in valid[setting]:
            raise InvalidSettingError(setting, option)

   def __init__(self, settings, valid):
      try:
         with open(settings, 'r') as settings_file:
            self.settings = json.load(settings_file)
      except TypeError:
         self.settings = dict(settings)
      Settings._validity_check(self.settings, valid)

   def __getitem__(self, item):
      return self.settings[item]

   def __iter__(self):
      return iter(self.settings)

   def __len__(self):
      return len(self.settings)

