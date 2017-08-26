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

   def test_create_task_once(self):
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
      s._create_task(s._create_bat())

      self.block_until_complete(next_minute.replace(second=0), 2)

      with open('batcave\\_foo.txt', 'r') as txt:
         buf = txt.readlines()
         self.assertEqual(len(buf), 1)
         self.assertEqual(
            buf[0], 'running out of {}'.format(os.path.realpath('batcave')))

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
      s._create_task(s._create_bat())

      two_mins_from_now = (next_minute + one_min).replace(second=0)
      self.block_until_complete(two_mins_from_now, 2)

      self.assertEqual(len(glob('batcave\\_foo*.txt')), 2)

      with open('batcave\\_foo.txt', 'r') as txt:
         buf = txt.readlines()
         self.assertEqual(len(buf), 1)
         self.assertEqual(
            buf[0], 'running out of {}'.format(os.path.realpath('batcave')))

      with open('batcave\\_foo1.txt', 'r') as txt:
         buf = txt.readlines()
         self.assertEqual(len(buf), 1)
         self.assertEqual(
            buf[0], 'running out of {}'.format(os.path.realpath('batcave')))

      # test 2 min modifier
      next_minute = datetime.now() + one_min

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
      s._create_task(s._create_bat())

      two_mins_from_now = (next_minute + one_min).replace(second=0)
      self.block_until_complete(two_mins_from_now, 2)

      self.assertEqual(len(glob('batcave\\_foo*.txt')), 3)

      with open('batcave\\_foo2.txt', 'r') as txt:
         buf = txt.readlines()
         self.assertEqual(len(buf), 1)
         self.assertEqual(
            buf[0], 'running out of {}'.format(os.path.realpath('batcave')))

   # TODO test_create_task_hourly
   # TODO test_create_task_daily
   # TODO test_create_task_weekly
   # TODO test_create_task_monthly
   # TODO test_create_task_onstart
   # TODO test_create_task_onlogon
   # TODO test_create_task_onidle

   def tearDown(self):
      dammit.keep_fkn_trying(self.remove_all_json)
      dammit.keep_fkn_trying(self.remove_batcave)
      dammit.keep_fkn_trying(self.remove_foo_txt)
