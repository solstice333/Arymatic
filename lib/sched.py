from lib.settings import Settings
from lib.custom_exceptions import *

import json
import os
import time
import lib.helpers as dammit

class Sched:
   @staticmethod
   def gen_sched_settings_file(
      settings_filename, taskname, run_cmd,
      working_dir, start_min, starttime, schedule):
      settings = {
         'name': taskname,
         'run_cmd': run_cmd,
         'working_dir': working_dir,
         'start_min': start_min,
         'start_time': starttime,
         'schedule': schedule
      }
      with open(settings_filename, 'w') as sched_settings:
         json.dump(settings, sched_settings, indent=4)

   @staticmethod
   def _try_again(callback, args=None, kwargs=None, max_attempts=10, interval_s=1):
      dammit.keep_fkn_trying(callback, args, kwargs, max_attempts, interval_s)

   def _create_bat(self):
      home = os.getcwd()
      os.chdir(self._batcave)
      with open("{}.bat".format(self._settings['name']), 'w') as batman:
         batman.write("@echo off\n")
         working_dir = '%~dp0' \
            if self._settings['working_dir'].strip() == '.' \
            else self._settings['working_dir']
         batman.write("cd /d {}\n".format(working_dir))
         start_min = 'start /min' if self._settings['start_min'] else ''
         batman.write("{} {}".format(
            start_min, self._settings['run_cmd']).strip() + "\n")
      os.chdir(home)

   @staticmethod
   def _create_batcave(batcave):
      os.makedirs(batcave)

   def __init__(self, settings_file, batcave):
      self._settings = Settings(settings_file,
                          {
                             'name': '*:str',
                             'run_cmd': '*:str',
                             'working_dir': '*:str',
                             'start_min': '*:bool',
                             'start_time': r'\d{2}:\d{2}:re',
                             'schedule': ['once', 'minute']
                          })
      if not os.path.isdir(batcave):
         dammit.keep_fkn_trying(self._create_batcave, [batcave])
      self._batcave = batcave

   def schedule_task(self):
      self._create_bat()

   def deschedule_task(self):
      raise NotYetImplemented()

