from lib.sched import Sched
from lib.custom_exceptions import *

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

   def test_gen_sched_settings_file(self):
      Sched.gen_sched_settings_file(
         'foo.json', 'foo', 'python _foo.py', '.', True, '00:00', 'once')
      self.assertTrue(os.path.isfile('foo.json'))
      with open('foo.json', 'r') as foo:
         settings = json.load(foo)
         self.assertEqual(settings['name'], 'foo')
         self.assertEqual(settings['run_cmd'], 'python _foo.py')
         self.assertEqual(settings['working_dir'], '.')
         self.assertEqual(settings['start_min'], True)
         self.assertEqual(settings['start_time'], '00:00')
         self.assertEqual(settings['schedule'], 'once')

   def test_ctor(self):
      next_minute = time.strftime("%H:%M", time.localtime(time.time() + 60))
      Sched.gen_sched_settings_file(
         'foo.json', 'foo', 'python _foo.py', '.', True, next_minute, 'once')
      sched = Sched('foo.json', 'batcave')
      self.assertTrue(os.path.isdir('batcave'))

      sched = Sched('foo.json', 'batcave/batcave1/batcave2')
      self.assertTrue(os.path.isdir('batcave/batcave1/batcave2'))

      with self.assertRaises(InvalidSettingError):
         Sched.gen_sched_settings_file(
            'foo.json', 'foo', 'python _foo.py', ',', False, next_minute, 'oncee')
         sched = Sched('foo.json', 'batcave')

   def test_create_bat(self):
      Sched.gen_sched_settings_file(
         'foo.json', 'foo', 'python _foo.py', '.', True, '00:00', 'once')
      s = Sched('foo.json', 'batcave')
      s._create_bat()

      with open("batcave/foo.bat", 'r') as foobat:
         buf = [l.rstrip() for l in foobat.readlines()]
         self.assertEqual(buf[0], '@echo off')
         self.assertEqual(buf[1], 'cd /d %~dp0')
         self.assertEqual(buf[2], 'start /min python _foo.py')
         self.assertEqual(len(buf), 3)

      Sched.gen_sched_settings_file(
         'foo.json', 'foo', 'python _foo.py',
         os.environ['USERPROFILE'], False, '00:00', 'once')
      s = Sched('foo.json', 'batcave')
      s._create_bat()

      with open("batcave/foo.bat", 'r') as foobat:
         buf = [l.rstrip() for l in foobat.readlines()]
         self.assertEqual(buf[0], '@echo off')
         self.assertEqual(buf[1], "cd /d {}".format(os.environ['USERPROFILE']))
         self.assertEqual(buf[2], 'python _foo.py')
         self.assertEqual(len(buf), 3)

   def tearDown(self):
      dammit.keep_fkn_trying(self.remove_all_json)
      dammit.keep_fkn_trying(self.remove_batcave)
