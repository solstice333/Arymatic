import unittest
import lib
import os
import os.path

class LibTest(unittest.TestCase):
   def test_env(self):
      self.assertEqual(
         lib.ROOT_PATH, os.path.realpath(os.path.join(os.getcwd(), '..')))
      self.assertEqual(
         lib.LIB_PATH, os.path.realpath(os.path.join(lib.ROOT_PATH, 'lib')))
