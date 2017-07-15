import subprocess
import re
import os

class Others:
   """class for detecting if other users are logged on"""


   _pat = re.compile(r'(?:\s|>)(?P<username>\w+)\s+' +
                    r'(?P<sessionname>[a-z]+)?\s+' +
                    r'(?P<id>\d+)\s+' +
                    r'(?P<state>[a-z]+)\s+' +
                    r'(?P<idletime>(?:\d+:)?\d+)\s+'
                    r'(?P<logontime>\d+/\d+/\d+ \d+:\d+ \w{2})', re.I)

   @staticmethod
   def _query_user():
      with subprocess.Popen('query user', stdout=subprocess.PIPE, shell=True,
                            universal_newlines=True) as proc:

         proc.stdout.readline()
         for line in proc.stdout:
            m = Others._pat.match(line)
            if m:
               yield {
                  'username': m['username'],
                  'sessionname': m['sessionname'],
                  'id': m['id'],
                  'state': m['state'],
                  'idletime': m['idletime'],
                  'logontime': m['logontime']}

   @property
   def logged_on_usernames(self):
      """return all usernames currently logged on as a tuple"""

      logged_on_users = set()
      for o in Others._query_user():
         logged_on_users.add(o['username'])
      return tuple(logged_on_users)

   def is_logged_on(self, *ignore):
      """return true if others are logged on, false otherwise. |ignore|
      is optional and represents variadic arguments which are usernames
      as strings to ignore; i.e. treat those usernames the same as
      yourself. All names in |ignore| are case insensitive.
      """

      ignore = set([u.lower() for u in ignore]) if ignore else set()
      ignore.add(os.environ['USERNAME'].lower())
      return bool(set(self.logged_on_usernames) - ignore)
