@setlocal EnableDelayedExpansion & set "ARYMATIC_DIR=%~dp0" & python -x %~f0 %* & exit /b !ERRORLEVEL!
from winreg import OpenKey, QueryValueEx, SetValueEx, \
                   HKEY_CURRENT_USER, KEY_ALL_ACCESS

import winreg
import os

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
         pythonpath += ";{}".format(arymatic_dir)
      except FileNotFoundError:
         pythonpath = arymatic_dir 

      SetValueEx(env, 'PYTHONPATH', 0, winreg.REG_SZ, pythonpath)
      input(restart_msg)

if __name__ == '__main__':
   main()
