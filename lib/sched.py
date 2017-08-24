from lib.settings import Settings
import json
from lib.custom_exceptions import *

class Sched:
   @staticmethod
   def gen_sched_settings_file(
      settings_filename, taskname, path_to_exec, starttime, schedule):
      settings = {
         'name': taskname,
         'path_to_exec': path_to_exec,
         'starttime': starttime,
         'schedule': schedule
      }
      with open(settings_filename, 'w') as sched_settings:
         json.dump(settings, sched_settings, indent=4)

   def __init__(self, settings_file):
      self._settings = Settings(settings_file,
                          {
                             'name': '*:str',
                             'path_to_exec': '*:str',
                             'starttime': r'\d{2}:\d{2}:re',
                             'schedule': ['once', 'minute']
                          })

   def schedule_task(self):
      raise NotYetImplemented()

   def deschedule_task(self):
      raise NotYetImplemented()

