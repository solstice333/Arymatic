from lib.settings import Settings
from collections import namedtuple

import json
import os
import subprocess
import lib.helpers as dammit
import re
import csv


class Sched:
   """class to manage scheduling tasks"""

   @staticmethod
   def _gen_sched_settings_file(settings_filename, settings):
      """generate a settings file for this Sched class. |settings_filename| is
      the settings filename and |settings| is the dictionary of settings.
      """

      with open(settings_filename, 'w') as sched_settings:
         json.dump(settings, sched_settings, indent=4)

   @staticmethod
   def gen_sched_settings_file(settings_filename, **settings):
      """generate a settings file for this Sched class. |settings_filename| is
      the settings filename and |**settings| represents variadic keyword
      arguments that are needed as settings to configure the scheduler. This
      method attempts to write to the json settings file a maximum of 10 times
      every second interval for every time it fails.
      """

      Sched._try_again(
         Sched._gen_sched_settings_file, [settings_filename, settings])

   @staticmethod
   def _try_again(
      callback, args=None, kwargs=None, max_attempts=10, interval_s=1):
      """try integer |max_attempts| attempts at integer |interval_s| seconds
      to do function object |callback|. And pass in list |args| and dictionary
      |kwargs| too. Default |max_attempts| is 10. Default |interval_s| is 1.
      """

      dammit.keep_fkn_trying(callback, args, kwargs, max_attempts, interval_s)

   @staticmethod
   def _create_batcave(batcave):
      """create the subdirectory where this scheduler's batch scripts
      are located i.e. |batcave|
      """

      os.makedirs(batcave)

   @staticmethod
   def _schtasks(*args):
      """run schtasks on the command line with |*args| which is a
      variadic list of schtasks arguments. subprocess.CalledProcessError is
      raised on any error.
      """

      return subprocess.run(
         ' '.join([tok for tok in ['schtasks', *args] if tok]),
         stdout=subprocess.PIPE, stderr=subprocess.STDOUT, check=True,
         universal_newlines=True)

   @staticmethod
   def _camel_to_snake(s):
      """return string |s| converted from camel case to snake case"""

      s = re.sub(r'\s+', '_', s)
      s = re.sub(r'\W+', '', s)
      s = s[0].lower() + re.sub(r'[A-Z]', '_\g<0>', s[1:])
      s = re.sub(r'_+', '_', s)
      return s.lower()

   @staticmethod
   def _filter_out_headers(headers_csv, tasks_csv):
      """filter out all csv sublists in list |tasks_csv| of any sublist
      that is equal to list |headers_csv|
      """

      return [t for t in tasks_csv if t != headers_csv]

   @staticmethod
   def _filter_out_non_top_lv(tasks_csv):
      """filter out all sublists in list |tasks_csv| whose second element
      has more than one backslash in the string. The second element in
      schtasks context is the taskname. More than one backslash means
      that the task file is not in the root folder. Return the new list
      of tasks that exist in the root.
      """

      return [t for t in tasks_csv if len(t[1].split('\\')) <= 2]

   @staticmethod
   def _convert_to_task_tuples(headers_csv, tasks_csv):
      """convert the task sublists in list |tasks_csv| to Task named
      tuples with property names defined in |headers_csv| and return it
      """

      Task = namedtuple('Task', headers_csv)
      return [Task(*t) for t in tasks_csv]

   @staticmethod
   def _create_task_dict_from(tasklist):
      """return a dictionary of task names to Task named tuples based
      on the list of Task named tuples |tasklist|
      """

      return {os.path.basename(t.task_name):t for t in tasklist}

   @staticmethod
   def _format_tasks_to_dict(raw_tasks, top_lv_only=True):
      """takes csv output structured like `schtasks /fo csv ...` |raw_tasks|
      and converts it to a dictionary of task names to Task named tuples.
      If |top_lv_only| is True, then return only the tasks at the root,
      otherwise return all tasks. |top_lv_only| is True by default.
      """

      tasks = raw_tasks.stdout.splitlines()
      tasks = list(csv.reader(tasks))

      orig_headers = tasks[0]
      tasks = tasks[1:]
      headers = [Sched._camel_to_snake(name) for name in orig_headers]
      tasks = Sched._filter_out_headers(orig_headers, tasks)
      if top_lv_only:
         tasks = Sched._filter_out_non_top_lv(tasks)

      tasks = Sched._convert_to_task_tuples(headers, tasks)
      return Sched._create_task_dict_from(tasks)

   @staticmethod
   def _query_tasks_dict(taskname=None, top_lv_only=True):
      """return a dictionary of task names to Task named tuples representing
      the content from `schtasks /fo csv /v ...`. If |taskname| is set to
      a non-empty string, '/tn |taskname|' is added to the command invocation.
      By default, |taskname| is None/falsy which will result in all root tasks
      to be fetched if |top_lv_only| is True. If |top_lv_only| is False and
      |taskname| is a non-empty string, then all tasks are fetched.
      """

      tasks = Sched._schtasks(
         '/query', '/fo csv', '/v', "/tn {}".format(taskname) if taskname else '')
      tasks = Sched._format_tasks_to_dict(tasks, top_lv_only)
      return tasks

   @staticmethod
   def _delete_task(taskname):
      """delete task whose name is |taskname|. Return true on success, false
      if the task name is not found. Raise subprocess.CalledProcessError on
      any other error.
      """

      try:
         Sched._schtasks('/delete', "/tn {}".format(taskname), '/f')
      except subprocess.CalledProcessError as cpe:
         if re.search(r'cannot.*find.*file.*specified', cpe.output, re.I) and \
            cpe.returncode == 1:
            return False
         else:
            raise cpe
      return True

   def _create_task(self, batpath):
      """create a task with schtasks given the path to the batch script
      |batpath|. |batpath| should be the absolute path.
      subprocess.CalledProcessError is raised on error.
      """

      Sched._schtasks(
         '/create', '/f',
         "/tr \"{}\"".format(batpath),
         "/st {}".format(self._settings['start_time'])
            if self._settings['start_time'] else '',
         "/sc {}".format(self._settings['schedule']),
         "/mo {}".format(self._settings['modifier'])
            if self._settings['schedule'].lower() in
               ['minute', 'hourly', 'daily', 'weekly', 'monthly'] and
               self._settings['modifier'] else '',
         "/d {}".format(','.join(self._settings['days']))
            if self._settings['schedule'].lower() == 'weekly' and
               self._settings['days'] else '',
         "/m {}".format(','.join(self._settings['months']))
            if self._settings['schedule'].lower() == 'monthly' and
               self._settings['months'] else '',
         "/i {}".format(self._settings['idle_time'])
            if self._settings['schedule'].lower() == 'onidle' and
               self._settings['idle_time'] else ''
         "/sd {}".format(self._settings['start_date'])
            if self._settings['schedule'].lower() in
               ['minute', 'hourly', 'daily', 'weekly', 'monthly', 'once'] and
               self._settings['start_date'] else '',
         "/ed {}".format(self._settings['end_date'])
            if self._settings['schedule'].lower() in
               ['minute', 'hourly', 'daily', 'weekly', 'monthly'] and
               self._settings['end_date'] else '',
         "/tn {}".format(self._settings['name']))

   def _create_bat(self):
      """create a wrapper batch script from the _settings property. This
      is needed to control working directory programatically, and to
      control starting a program minimized if possible. This makes it a
      lot easier than directly invoking the desired program with /tr
      flag of schtasks
      """

      batpath = os.path.realpath(
         "{}\\{}.bat".format(self._batcave, self._settings['name']))
      with open(batpath, 'w') as batman:
         batman.write("@echo off\n")
         working_dir = '%~dp0' \
            if self._settings['working_dir'].strip() == '.' \
            else self._settings['working_dir']
         batman.write("cd /d {}\n".format(working_dir))
         start_min = 'start /min' if self._settings['start_min'] else ''
         batman.write("{} {}".format(
            start_min, self._settings['run_cmd']).strip() + "\n")
      return batpath

   @staticmethod
   def details_for(taskname):
      """return a Task named tuple associated to |taskname|. If not task
      with the name |taskname| exists, then return an empty tuple. If
      any other error occurs, raise subprocess.CalledProcessError.
      """

      try:
         return Sched._query_tasks_dict(taskname)[taskname]
      except subprocess.CalledProcessError as cpe:
         if re.search(r'cannot.*find.*file.*specified', cpe.output, re.I) and \
            cpe.returncode == 1:
            return ()
         else:
            raise cpe

   @staticmethod
   def is_task_scheduled(taskname):
      """return True if |taskname| is already scheduled, False otherwise"""

      return bool(Sched.details_for(taskname))

   @staticmethod
   def deschedule_task_with_taskname(taskname):
      """deschedule the task named |taskname|. Return True on success, False
      if no task exists with the name |taskname|. Raise
      subprocess.CalledProcessError for any other error.
      """

      return Sched._delete_task(taskname)

   @staticmethod
   def _inject_translation_settings(settings_file):
      """inject any settings into the JSON configuration read from
      |settings_file| and return the updated dictionary. Right now
      this checks if a 'quarterly' schedule was specified and
      translates it to every 92 days."""

      with open(settings_file, 'r') as shandle:
         settings = json.load(shandle)

         if settings['schedule'] == 'quarterly':
            settings.update({
               'schedule': 'daily',
               'modifier': 92
            })

      return settings

   def __init__(self, settings_file, batcave='batcave'):
      """create a Sched handle object with configuration based on the JSON
      |settings_file| which is the path to the settings file. |batcave|
      is where all the batch scripts generated by this Sched object are
      stored. This is 'batcave' by default, but can be any path. Refer
      to the valid dictionary in the code below to know what the required
      JSON structure should be for a valid settings file. Refer to the
      defaults dictionary in the code below to know what the optional
      settings are.

      valid={
         'name': '*:str',
         'run_cmd': '*:str',
         'working_dir': '*:str',
         'start_min': '*:bool',
         'start_time': [r'\d{2}:\d{2}:re', ''],
         'schedule': ['once', 'minute', 'hourly', 'daily', 'quarterly',
                      'weekly', 'monthly', 'onstart', 'onlogon', 'onidle'],
         'days': ['MON', 'TUE', 'WED', 'THU',
                  'FRI', 'SAT', 'SUN'],
         'months': ['JAN', 'FEB', 'MAR', 'APR', 'MAY', 'JUN',
                    'JUL', 'AUG', 'SEP', 'OCT', 'NOV', 'DEC'],
         'modifier': ['*:int',
                      'FIRST', 'SECOND', 'THIRD', 'FOURTH',
                      'LAST', 'LASTDAY', ''],
         'start_date': [r'\d{2}\\\d{2}\\\d{4}:re', ''],
         'end_date': [r'\d{2}\\\d{2}\\\d{4}:re', '']
      }
      defaults={
         'working_dir': '.',
         'start_min': True,
         'start_time': '',
         'days': [],
         'months': [],
         'modifier': '',
         'start_date': '',
         'end_date': ''
      }
      """

      self._settings = Settings(
         Sched._inject_translation_settings(settings_file),
         valid={
            'name': '*:str',
            'run_cmd': '*:str',
            'working_dir': '*:str',
            'start_min': '*:bool',
            'start_time': [r'\d{2}:\d{2}:re', ''],
            'schedule': ['once', 'minute', 'hourly', 'daily', 'quarterly',
                         'weekly', 'monthly', 'onstart', 'onlogon', 'onidle'],
            'days': ['MON', 'TUE', 'WED', 'THU',
                     'FRI', 'SAT', 'SUN'],
            'months': ['JAN', 'FEB', 'MAR', 'APR', 'MAY', 'JUN',
                       'JUL', 'AUG', 'SEP', 'OCT', 'NOV', 'DEC'],
            'modifier': ['*:int',
                         'FIRST', 'SECOND', 'THIRD', 'FOURTH',
                         'LAST', 'LASTDAY', ''],
            'start_date': [r'\d{2}\\\d{2}\\\d{4}:re', ''],
            'end_date': [r'\d{2}\\\d{2}\\\d{4}:re', '']
         },
         defaults={
            'working_dir': '.',
            'start_min': True,
            'start_time': '',
            'days': [],
            'months': [],
            'modifier': '',
            'start_date': '',
            'end_date': ''
         })

      if not os.path.isdir(batcave):
         dammit.keep_fkn_trying(self._create_batcave, [batcave])
      self._batcave = batcave

   def schedule_task(self):
      """schedule the task that is bound to this Sched handle object and
      defined by the settings file
      """

      self._create_task(self._create_bat())

   def deschedule_task(self):
      """deschedule the task that is bound to this Sched handle object and
      defined by the settings file. Return True on success, False
      if the task has not been scheduled yet. Raise
      subprocess.CalledProcessError on any other error
      """

      return Sched.deschedule_task_with_taskname(self._settings['name'])

   def details(self):
      """return a Task named tuple containing schedule details of
      the task that is bound to this Sched handle object and defined
      by the settings file if the task has been scheduled. If the
      task has not been scheduled, then return an empty tuple. Raise
      subprocess.CalledProcessError on any other error
      """

      return Sched.details_for(self._settings['name'])

   def is_scheduled(self):
      """return True if scheduled, False otherwise.
      subprocess.CalledProcessError is raised on any error
      """

      return Sched.is_task_scheduled(self._settings['name'])
