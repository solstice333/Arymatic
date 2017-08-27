from lib.settings import Settings
from lib.custom_exceptions import *
from collections import namedtuple

import json
import os
import subprocess
import lib.helpers as dammit
import re
import csv

class Sched:
   @staticmethod
   def _gen_sched_settings_file(settings_filename, settings):
      with open(settings_filename, 'w') as sched_settings:
         json.dump(settings, sched_settings, indent=4)

   @staticmethod
   def gen_sched_settings_file(settings_filename, **settings):
      Sched._try_again(
         Sched._gen_sched_settings_file, [settings_filename, settings])

   @staticmethod
   def _try_again(
      callback, args=None, kwargs=None, max_attempts=10, interval_s=1):
      dammit.keep_fkn_trying(callback, args, kwargs, max_attempts, interval_s)

   @staticmethod
   def _create_batcave(batcave):
      os.makedirs(batcave)

   @staticmethod
   def _schtasks(*args):
      return subprocess.run(
         ' '.join([tok for tok in ['schtasks', *args] if tok]),
         stdout=subprocess.PIPE, stderr=subprocess.STDOUT, check=True,
         universal_newlines=True)

   @staticmethod
   def _camel_to_snake(s):
      s = re.sub(r'\s+', '_', s)
      s = re.sub(r'\W+', '', s)
      s = s[0].lower() + re.sub(r'[A-Z]', '_\g<0>', s[1:])
      s = re.sub(r'_+', '_', s)
      return s.lower()

   @staticmethod
   def _query_task(taskname):
      raise NotYetImplemented()

   @staticmethod
   def _filter_out_headers(headers_csv, tasks_csv):
      return [t for t in tasks_csv if t != headers_csv]

   @staticmethod
   def _filter_out_non_top_lv(tasks_csv):
      return [t for t in tasks_csv if len(t[1].split('\\')) <= 2]

   @staticmethod
   def _convert_to_task_tuples(headers_csv, tasks_csv):
      Task = namedtuple('Task', headers_csv)
      return [Task(*t) for t in tasks_csv]

   @staticmethod
   def _create_task_dict_from(tasklist):
      return {os.path.basename(t.task_name):t for t in tasklist}

   @staticmethod
   def _format_tasks_to_dict(raw_tasks, top_lv_only=True):
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
   def _query_tasks(top_lv_only=True):
      tasks = Sched._schtasks('/query', '/fo csv', '/v')
      tasks = Sched._format_tasks_to_dict(tasks, top_lv_only)
      return tasks

   def _create_task(self, batpath):
      Sched._schtasks(
         '/create', '/f',
         '/tr', "\"{}\"".format(batpath),
         '/st', self._settings['start_time'],
         '/sc', self._settings['schedule'],
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
         '/tn', self._settings['name'])

   def _create_bat(self):
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

   def _delete_task(self, taskname):
      raise NotYetImplemented()

   def __init__(self, settings_file, batcave):
      self._settings = Settings(
         settings_file,
         valid={
            'name': '*:str',
            'run_cmd': '*:str',
            'working_dir': '*:str',
            'start_min': '*:bool',
            'start_time': r'\d{2}:\d{2}:re',
            'schedule': ['once', 'minute'],
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
      self._create_task(self._create_bat())

   def deschedule_task(self):
      self._delete_task(self._settings['name'])
