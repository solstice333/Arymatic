@setlocal EnableDelayedExpansion & set "ARYMATIC_DIR=%~dp0" & python -x %~f0 %* & exit /b !ERRORLEVEL!
from winreg import OpenKey, QueryValueEx, SetValueEx, \
                   HKEY_CURRENT_USER, KEY_ALL_ACCESS

import winreg
import os
import os.path
import sys

def run_unit_tests():
   home = os.getcwd()
   initial_pythonpath = os.environ.get('PYTHONPATH')

   os.environ['PYTHONPATH'] = os.environ['ARYMATIC_DIR']
   os.chdir(os.path.join(os.environ['ARYMATIC_DIR'], 'tests'))
   exst = os.system('python -m unittest discover -v -p *_test.py')

   if initial_pythonpath:
      os.environ['PYTHONPATH'] = initial_pythonpath
   else:
      del os.environ['PYTHONPATH']

   os.chdir(home)
   return exst

def main():
   arymatic_dir = os.environ['ARYMATIC_DIR']
   restart_msg = "Please restart your computer " + \
      "for the changes to take effect.\n" + \
      "Hit Enter to continue"

   with OpenKey(
      HKEY_CURRENT_USER, 'Environment', access=KEY_ALL_ACCESS) as env:

      pythonpath = ''
      try:
         pythonpath = QueryValueEx(env, 'PYTHONPATH')[0]
         if arymatic_dir in pythonpath:
            try:
               if arymatic_dir in os.environ['PYTHONPATH']:
                  pass
               else:
                  input(restart_msg)
            except KeyError:
               input(restart_msg)
            exit(0)
         pythonpath = "{};{}".format(arymatic_dir, pythonpath)
      except FileNotFoundError:
         pythonpath = arymatic_dir 

      if run_unit_tests():
         sys.stderr.write("Error: tests failed. Backing out of setup\n") 
      else:
         SetValueEx(env, 'PYTHONPATH', 0, winreg.REG_SZ, pythonpath)
         input(restart_msg)

if __name__ == '__main__':
   main()
