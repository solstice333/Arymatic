from lib.sched import Sched

import unittest
import os.path
import os
import tests.test_helpers as testhelp
import json

class SchedTest(unittest.TestCase):
   """unit tests for Sched"""

   def remove_all_json(self):
      with os.scandir() as files:
         for f in files:
            if os.path.splitext(f.name)[1] == '.json':
               os.remove(f.name)

   def test_gen_sched_settings_file(self):
      Sched.gen_sched_settings_file(
         'foo.json', 'foo', '.\\foo.py', '00:00', 'once')
      self.assertTrue(os.path.isfile('foo.json'))
      with open('foo.json', 'r') as foo:
         settings = json.load(foo)
         self.assertEqual(settings['name'], 'foo')
         self.assertEqual(settings['path_to_executable'], '.\\foo.py')
         self.assertEqual(settings['starttime'], '00:00')
         self.assertEqual(settings['schedule'], 'once')

   def tearDown(self):
      testhelp.keep_fkn_trying(self.remove_all_json)
