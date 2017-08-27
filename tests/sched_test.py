from lib.sched import Sched
from lib.custom_exceptions import *
from datetime import datetime, timedelta
from glob import glob

import unittest
import os.path
import os
import tests.test_helpers as dammit
import json
import time
import shutil
import subprocess
import re


class SchedTest(unittest.TestCase):
   """unit tests for Sched"""

   def remove_all_json(self):
      with os.scandir() as files:
         for f in files:
            if os.path.splitext(f.name)[1] == '.json':
               os.remove(f.name)

   def remove_batcave(self):
      if os.path.isdir('batcave'):
         shutil.rmtree('batcave')

   def remove_foo_txt(self):
      if os.path.isfile('_foo.txt'):
         os.remove('_foo.txt')

   def block_until_complete(self, compl_dt, extra=0):
      while datetime.now() < compl_dt:
         time.sleep(1)
      for s in range(0, extra):
         time.sleep(1)

   def incr_month(self, m):
      return (m + 1)%12 or 12

   def incr_month_dt(self, dt):
      next_month = self.incr_month(dt.month)
      next_year = dt.year + 1
      return dt.replace(month=next_month, year=next_year) \
         if next_month == 1 else dt.replace(month=next_month)

   def test_gen_sched_settings_file(self):
      Sched.gen_sched_settings_file(
         'foo.json',
         name='_foo',
         run_cmd='python _foo.py',
         working_dir='.',
         start_min=True,
         start_time='00:00',
         schedule='once',
         days=['MON','TUE'],
         months=['JAN','MAR'],
         modifier=2)
      self.assertTrue(os.path.isfile('foo.json'))
      with open('foo.json', 'r') as foo:
         settings = json.load(foo)
         self.assertEqual(settings['name'], '_foo')
         self.assertEqual(settings['run_cmd'], 'python _foo.py')
         self.assertEqual(settings['working_dir'], '.')
         self.assertEqual(settings['start_min'], True)
         self.assertEqual(settings['start_time'], '00:00')
         self.assertEqual(settings['schedule'], 'once')
         self.assertEqual(settings['modifier'], 2)
         self.assertEqual(settings['days'], ['MON','TUE'])
         self.assertEqual(settings['months'], ['JAN','MAR'])

      Sched.gen_sched_settings_file(
         'foo.json',
         name='_foo',
         run_cmd='python _foo.py',
         start_time='00:00',
         schedule='once')
      self.assertTrue(os.path.isfile('foo.json'))
      with open('foo.json', 'r') as foo:
         settings = json.load(foo)
         self.assertEqual(settings['name'], '_foo')
         self.assertEqual(settings['run_cmd'], 'python _foo.py')
         self.assertEqual(settings['start_time'], '00:00')
         self.assertEqual(settings['schedule'], 'once')

   def test_ctor(self):
      next_minute = time.strftime("%H:%M", time.localtime(time.time() + 60))
      Sched.gen_sched_settings_file(
         'foo.json',
         name='_foo',
         run_cmd='python _foo.py',
         working_dir='.',
         start_min=True,
         start_time=next_minute,
         schedule='once')
      sched = Sched('foo.json', 'batcave')
      self.assertTrue(os.path.isdir('batcave'))

      sched = Sched('foo.json', 'batcave/batcave1/batcave2')
      self.assertTrue(os.path.isdir('batcave/batcave1/batcave2'))

      with self.assertRaises(InvalidSettingError):
         Sched.gen_sched_settings_file(
            'foo.json',
            name='_foo',
            run_cmd='python _foo.py',
            working_dir='.',
            start_min=False,
            start_time=next_minute,
            schedule='oncee')
         sched = Sched('foo.json', 'batcave')

   def test_create_bat(self):
      Sched.gen_sched_settings_file(
         'foo.json',
         name='_foo',
         run_cmd='python _foo.py',
         working_dir='.',
         start_min=True,
         start_time='00:00',
         schedule='once')
      s = Sched('foo.json', 'batcave')
      batpath = s._create_bat()
      self.assertEqual(
         batpath,
         os.path.realpath(os.path.join(os.getcwd(), 'batcave', '_foo.bat')))

      with open("batcave\\_foo.bat", 'r') as foobat:
         buf = [l.rstrip() for l in foobat.readlines()]
         self.assertEqual(buf[0], '@echo off')
         self.assertEqual(buf[1], 'cd /d %~dp0')
         self.assertEqual(buf[2], 'start /min python _foo.py')
         self.assertEqual(len(buf), 3)

      Sched.gen_sched_settings_file(
         'foo.json',
         name='_foo',
         run_cmd='python _foo.py',
         working_dir=os.environ['USERPROFILE'],
         start_min=False,
         start_time='00:00',
         schedule='once')
      s = Sched('foo.json', 'batcave')
      s._create_bat()

      with open("batcave/_foo.bat", 'r') as foobat:
         buf = [l.rstrip() for l in foobat.readlines()]
         self.assertEqual(buf[0], '@echo off')
         self.assertEqual(buf[1], "cd /d {}".format(os.environ['USERPROFILE']))
         self.assertEqual(buf[2], 'python _foo.py')
         self.assertEqual(len(buf), 3)

   def test_create_task_once_long(self):
      next_minute = datetime.now() + timedelta(minutes=1)

      Sched.gen_sched_settings_file(
         'foo.json',
         name='_foo',
         run_cmd='python _foo.py',
         working_dir='.',
         start_min=False,
         start_time=next_minute.strftime("%H:%M"),
         schedule='once')
      s = Sched('foo.json', 'batcave')
      shutil.copy('_foo.py', 'batcave\\_foo.py')
      s.schedule_task()

      self.block_until_complete(next_minute.replace(second=0), 2)

      self.assertEqual(len(glob('batcave\\_foo*.txt')), 1)

      with open('batcave\\_foo.txt', 'r') as txt:
         buf = txt.readlines()
         self.assertEqual(len(buf), 1)
         self.assertEqual(
            buf[0], 'running out of {}'.format(os.path.realpath('batcave')))

   def test_create_task_once_query_is_scheduled_and_deschedule(self):
      next_minute = datetime.now() + timedelta(minutes=1)

      Sched.gen_sched_settings_file(
         'foo.json',
         name='_foo',
         run_cmd='python _foo.py',
         working_dir='.',
         start_min=False,
         start_time=next_minute.strftime("%H:%M"),
         schedule='once')
      s = Sched('foo.json', 'batcave')
      shutil.copy('_foo.py', 'batcave\\_foo.py')
      s.schedule_task()

      task = s.details()
      self.assertTrue(task)
      self.assertTrue(s.is_scheduled())
      self.assertEqual(task.task_name, '\\_foo')
      self.assertEqual(task.schedule_type, 'One Time Only')
      self.assertEqual(task.repeat_every, 'Disabled')
      self.assertEqual(
         datetime.strptime(task.start_time, "%H:%M:%S %p").time(),
         next_minute.replace(second=0, microsecond=0).time())
      self.assertEqual(
         datetime.strptime(task.start_date, '%m/%d/%Y').date(),
         next_minute.date())

      self.assertTrue(s.deschedule_task())
      self.assertFalse(s.deschedule_task())
      self.assertFalse(s.details())
      self.assertFalse(s.is_scheduled())

   def test_create_task_minute(self):
      one_min = timedelta(minutes=1)
      next_minute = datetime.now() + one_min

      Sched.gen_sched_settings_file(
         'foo.json',
         name='_foo',
         run_cmd='python _foo.py',
         working_dir='.',
         start_min=True,
         start_time=next_minute.strftime("%H:%M"),
         schedule='minute')
      s = Sched('foo.json', 'batcave')
      shutil.copy('_foo.py', 'batcave\\_foo.py')
      s.schedule_task()

      task = s.details()
      self.assertTrue(task)
      self.assertTrue(s.is_scheduled())
      self.assertEqual(task.task_name, '\\_foo')
      self.assertEqual(task.schedule_type, 'One Time Only, Minute ')
      self.assertEqual(task.repeat_every, '0 Hour(s), 1 Minute(s)')
      self.assertEqual(
         datetime.strptime(task.start_time, "%H:%M:%S %p").time(),
         next_minute.replace(second=0, microsecond=0).time())
      self.assertEqual(
         datetime.strptime(task.start_date, '%m/%d/%Y').date(),
         next_minute.date())

      s.deschedule_task()

      self.assertFalse(s.details())
      self.assertFalse(s.is_scheduled())

   def test_create_task_2_minutes(self):
      next_minute = datetime.now() + timedelta(minutes=1)

      Sched.gen_sched_settings_file(
         'foo.json',
         name='_foo',
         run_cmd='python _foo.py',
         working_dir='.',
         start_min=True,
         start_time=next_minute.strftime("%H:%M"),
         schedule='minute',
         modifier=2)
      s = Sched('foo.json', 'batcave')
      shutil.copy('_foo.py', 'batcave\\_foo.py')
      s.schedule_task()

      task = s.details()
      self.assertTrue(task)
      self.assertTrue(s.is_scheduled())
      self.assertEqual(task.task_name, '\\_foo')
      self.assertEqual(task.schedule_type, 'One Time Only, Minute ')
      self.assertEqual(task.repeat_every, '0 Hour(s), 2 Minute(s)')
      self.assertEqual(
         datetime.strptime(task.start_time, "%H:%M:%S %p").time(),
         next_minute.replace(second=0, microsecond=0).time())
      self.assertEqual(
         datetime.strptime(task.start_date, '%m/%d/%Y').date(),
         next_minute.date())

      s.deschedule_task()

      self.assertFalse(s.details())
      self.assertFalse(s.is_scheduled())

   def test_query_tasks_dict(self):
      top_lv_tasks = Sched._query_tasks_dict()

      for tname, t in top_lv_tasks.items():
         self.assertTrue('\\' not in tname)
         self.assertEqual(len(t._fields), 28)
         self.assertTrue('host_name' in t._fields)
         self.assertTrue('task_name' in t._fields)
         self.assertTrue('next_run_time' in t._fields)
         self.assertTrue('status' in t._fields)
         self.assertTrue('logon_mode' in t._fields)
         self.assertTrue('last_run_time' in t._fields)
         self.assertTrue('last_result' in t._fields)
         self.assertTrue('author' in t._fields)
         self.assertTrue('task_to_run' in t._fields)
         self.assertTrue('start_in' in t._fields)
         self.assertTrue('comment' in t._fields)
         self.assertTrue('scheduled_task_state' in t._fields)
         self.assertTrue('idle_time' in t._fields)
         self.assertTrue('power_management' in t._fields)
         self.assertTrue('run_as_user' in t._fields)
         self.assertTrue('delete_task_if_not_rescheduled' in t._fields)
         self.assertTrue('stop_task_if_runs_x_hours_and_x_mins' in t._fields)
         self.assertTrue('schedule' in t._fields)
         self.assertTrue('schedule_type' in t._fields)
         self.assertTrue('start_time' in t._fields)
         self.assertTrue('start_date' in t._fields)
         self.assertTrue('end_date' in t._fields)
         self.assertTrue('days' in t._fields)
         self.assertTrue('months' in t._fields)
         self.assertTrue('repeat_every' in t._fields)
         self.assertTrue('repeat_until_time' in t._fields)
         self.assertTrue('repeat_until_duration' in t._fields)
         self.assertTrue('repeat_stop_if_still_running' in t._fields)
         self.assertTrue(t.task_name.count('\\') == 1)

      top_lv_tasks = Sched._query_tasks_dict(top_lv_only=False)

      for tname, t in top_lv_tasks.items():
         self.assertTrue('\\' not in tname)
         self.assertEqual(len(t._fields), 28)
         self.assertTrue('host_name' in t._fields)
         self.assertTrue('task_name' in t._fields)
         self.assertTrue('next_run_time' in t._fields)
         self.assertTrue('status' in t._fields)
         self.assertTrue('logon_mode' in t._fields)
         self.assertTrue('last_run_time' in t._fields)
         self.assertTrue('last_result' in t._fields)
         self.assertTrue('author' in t._fields)
         self.assertTrue('task_to_run' in t._fields)
         self.assertTrue('start_in' in t._fields)
         self.assertTrue('comment' in t._fields)
         self.assertTrue('scheduled_task_state' in t._fields)
         self.assertTrue('idle_time' in t._fields)
         self.assertTrue('power_management' in t._fields)
         self.assertTrue('run_as_user' in t._fields)
         self.assertTrue('delete_task_if_not_rescheduled' in t._fields)
         self.assertTrue('stop_task_if_runs_x_hours_and_x_mins' in t._fields)
         self.assertTrue('schedule' in t._fields)
         self.assertTrue('schedule_type' in t._fields)
         self.assertTrue('start_time' in t._fields)
         self.assertTrue('start_date' in t._fields)
         self.assertTrue('end_date' in t._fields)
         self.assertTrue('days' in t._fields)
         self.assertTrue('months' in t._fields)
         self.assertTrue('repeat_every' in t._fields)
         self.assertTrue('repeat_until_time' in t._fields)
         self.assertTrue('repeat_until_duration' in t._fields)
         self.assertTrue('repeat_stop_if_still_running' in t._fields)
         self.assertTrue(t.task_name.count('\\') >= 1)

      Sched.gen_sched_settings_file(
         'foo.json',
         name='_foo',
         run_cmd='python _foo.py',
         start_time="00:00",
         schedule='once')
      s = Sched('foo.json')
      s.schedule_task()

      task_foo_dict = Sched._query_tasks_dict('_foo')
      self.assertTrue(task_foo_dict)
      self.assertIn('_foo', task_foo_dict)
      tname, t = '_foo', task_foo_dict['_foo']
      self.assertTrue('\\' not in tname)
      self.assertEqual(len(t._fields), 28)
      self.assertTrue('host_name' in t._fields)
      self.assertTrue('task_name' in t._fields)
      self.assertTrue('next_run_time' in t._fields)
      self.assertTrue('status' in t._fields)
      self.assertTrue('logon_mode' in t._fields)
      self.assertTrue('last_run_time' in t._fields)
      self.assertTrue('last_result' in t._fields)
      self.assertTrue('author' in t._fields)
      self.assertTrue('task_to_run' in t._fields)
      self.assertTrue('start_in' in t._fields)
      self.assertTrue('comment' in t._fields)
      self.assertTrue('scheduled_task_state' in t._fields)
      self.assertTrue('idle_time' in t._fields)
      self.assertTrue('power_management' in t._fields)
      self.assertTrue('run_as_user' in t._fields)
      self.assertTrue('delete_task_if_not_rescheduled' in t._fields)
      self.assertTrue('stop_task_if_runs_x_hours_and_x_mins' in t._fields)
      self.assertTrue('schedule' in t._fields)
      self.assertTrue('schedule_type' in t._fields)
      self.assertTrue('start_time' in t._fields)
      self.assertTrue('start_date' in t._fields)
      self.assertTrue('end_date' in t._fields)
      self.assertTrue('days' in t._fields)
      self.assertTrue('months' in t._fields)
      self.assertTrue('repeat_every' in t._fields)
      self.assertTrue('repeat_until_time' in t._fields)
      self.assertTrue('repeat_until_duration' in t._fields)
      self.assertTrue('repeat_stop_if_still_running' in t._fields)
      self.assertTrue(t.task_name.count('\\') >= 1)

      s.deschedule_task()
      with self.assertRaises(subprocess.CalledProcessError):
         try:
            s._query_tasks_dict('_foo')
         except subprocess.CalledProcessError as cpe:
            self.assertEqual(cpe.returncode, 1)
            self.assertTrue(
               re.search(r'cannot.*find.*file.*specified', cpe.output, re.I))
            raise cpe

   def test_create_task_monthly(self):
      Sched.gen_sched_settings_file(
         'foo.json',
         name='_foo',
         run_cmd='python _foo.py',
         schedule='monthly')
      s = Sched('foo.json')
      now = datetime.now()
      s.schedule_task()

      task = s.details()
      self.assertTrue(task)
      self.assertTrue(s.is_scheduled())
      self.assertEqual(task.task_name, '\\_foo')
      self.assertEqual(task.schedule_type, 'Monthly')
      self.assertEqual(task.repeat_every, 'Disabled')
      self.assertEqual(
         datetime.strptime(task.start_time, "%H:%M:%S %p").time(),
         now.replace(second=0, microsecond=0).time())
      self.assertEqual(
         datetime.strptime(task.start_date, '%m/%d/%Y').date(),
         datetime.now().date())
      self.assertEqual(
         datetime.strptime(task.next_run_time, "%m/%d/%Y %H:%M:%S %p"),
         self.incr_month_dt(
            datetime.now().replace(day=1, second=0, microsecond=0)))

      s.deschedule_task()

      self.assertFalse(s.details())
      self.assertFalse(s.is_scheduled())

   def tearDown(self):
      dammit.keep_fkn_trying(self.remove_all_json)
      dammit.keep_fkn_trying(self.remove_batcave)
      dammit.keep_fkn_trying(self.remove_foo_txt)
      try:
         Sched.deschedule_task_with_taskname('_foo')
      except subprocess.CalledProcessError as cpe:
         if cpe.returncode == 1:
            pass
