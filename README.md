# Arymatic

## Description:

A way to automate things the Arya way. In general, this is a layer on top of schtasks that allows the user to define how to schedule tasks by defining a simple JSON file then scheduling it using the `lib.sched.Sched.schedule_task()` method.

## Usage:

### Run unit tests:

```
$ cd <repo_root>
$ set PYTHONPATH=%PYTHONPATH%;%CD%
$ cd tests
$ python -m unittest discover -v -p *_test.py
```

### Installation

```
$ cd <repo_root>
$ setup.bat
$ shutdown /r /t 0
```

After reboot,

```
$ cd <repo_root>\tests
$ python -m unittest discover -v -p *_test.py
```

### API Usage Examples:

**TODO**

See tests/settings_test.py for now

## API
```
Help on module lib.others in lib:

NAME
    lib.others

CLASSES
    builtins.object
        Others

    class Others(builtins.object)
     |  class for detecting if other users are logged on
     |
     |  Methods defined here:
     |
     |  is_logged_on(self, *ignore)
     |      return true if others are logged on, false otherwise. |ignore|
     |      is optional and represents variadic arguments which are usernames
     |      as strings to ignore; i.e. treat those usernames the same as
     |      yourself. All names in |ignore| are case insensitive. Your
     |      username is ignored implicitly.
     |
     |  ----------------------------------------------------------------------
     |  Data descriptors defined here:
     |
     |  __dict__
     |      dictionary for instance variables (if defined)
     |
     |  __weakref__
     |      list of weak references to the object (if defined)
     |
     |  logged_on_usernames
     |      return all usernames currently logged on as a tuple

```

```
Help on module lib.settings in lib:

NAME
    lib.settings

CLASSES
    collections.abc.Mapping(collections.abc.Collection)
        Settings

    class Settings(collections.abc.Mapping)
     |  class for accessing settings
     |
     |  Method resolution order:
     |      Settings
     |      collections.abc.Mapping
     |      collections.abc.Collection
     |      collections.abc.Sized
     |      collections.abc.Iterable
     |      collections.abc.Container
     |      builtins.object
     |
     |  Methods defined here:
     |
     |  __getitem__(self, name)
     |      return the value associated to setting name |name|. Raise KeyError
     |      if not in Settings
     |
     |  __init__(self, settings, valid, defaults=None)
     |      create a Settings object. |settings| can be a dict or path to json
     |      file. If a dict, then values in |settings| must be a primitive
     |      (int, float, bool, str), list, or dict. |valid| must be a dict.
     |      |settings| represents the user settings where each pair is a setting
     |      name associated to a chosen setting value. |valid| represents all valid
     |      user settings where each pair is a setting name associated to possible
     |      legal setting values. Here's some examples,
     |
     |      # value associated to 'foo' must be either 'b' or 'a'
     |      Settings({'foo':'b'}, {'foo':['b','a']}
     |
     |      # value associated to 'foo' can be a list of either 'a','b','c', and/or 'd'
     |      Settings({'foo':['a','b']}, {'foo':[['c', 'b', 'd', 'a']]}
     |
     |      # value associated to 'foo' can be a list of either 'a','b','c', and/or 'd'
     |      Settings({'foo':['a','b']}, {'foo':[['c', 'b', 'd', 'a']]}
     |
     |      # value associated to 'foo' can be a list of lists where each nested
     |      # list can be one or more combinations of
     |      # ['a'], ['b'], ['c'], ['d'], ['c', 'd'], ['b', 'a']
     |      # where order doesn't matter. In other words, each user sublist must
     |      # contain 0 or more elements from any individual valid sublist.
     |      # A sublist cannot contain a mix of items from two or more valid
     |      # sublists.
     |      Settings({'foo':[['a','b']]}, {'foo':[['c', 'd'], ['b', 'a']]}
     |
     |      # Associating to the example above, this would raise an InvalidSettingError
     |      Settings({'foo':[['b','d']]}, {'foo':[['c', 'd'], ['b', 'a']]}
     |
     |      # value associated to 'foo' must have a valid nested dict where 'bar'
     |      # is the only key accepting values of 'b' or 'a'
     |      Settings({'foo':{'bar':'a'}}, {'foo':{'bar':['b','a']}})
     |
     |      # value associated to 'foo' must be one of the valid nested dicts
     |      Settings({'foo':{'bar':'a'}}, {'foo':[{'baz':['c','d']},{'bar':['b','a']}]})
     |      Settings({'foo':{'bar':'a','mu':'e'}}, {'foo':[{'baz':['c','d']},{'bar':['b','a'],'mu':['e','f']}]})
     |      Settings({'foo':{'baz':'d'}}, {'foo':[{'baz':['c','d']},{'bar':['b','a'],'mu':['e','f']}]})
     |
     |      Finally, the |defaults| dictionary is optional, and specifies any
     |      default values for any key in the user settings that's nonexistent
     |      or has an associating value of None. The entries in |defaults| are
     |      injected into |settings| before the validity check is done. If the
     |      validity check fails, an InvalidSettingError is raised.
     |
     |  __iter__(self)
     |      return an iterator over the names of the Settings
     |
     |  __len__(self)
     |      return the number of settings
     |
     |  ----------------------------------------------------------------------
     |  Data descriptors defined here:
     |
     |  __dict__
     |      dictionary for instance variables (if defined)
     |
     |  __weakref__
     |      list of weak references to the object (if defined)
     |
     |  ----------------------------------------------------------------------
     |  Data and other attributes defined here:
     |
     |  __abstractmethods__ = frozenset()
     |
     |  ----------------------------------------------------------------------
     |  Methods inherited from collections.abc.Mapping:
     |
     |  __contains__(self, key)
     |
     |  __eq__(self, other)
     |      Return self==value.
     |
     |  get(self, key, default=None)
     |      D.get(k[,d]) -> D[k] if k in D, else d.  d defaults to None.
     |
     |  items(self)
     |      D.items() -> a set-like object providing a view on D's items
     |
     |  keys(self)
     |      D.keys() -> a set-like object providing a view on D's keys
     |
     |  values(self)
     |      D.values() -> an object providing a view on D's values
     |
     |  ----------------------------------------------------------------------
     |  Data and other attributes inherited from collections.abc.Mapping:
     |
     |  __hash__ = None
     |
     |  __reversed__ = None
     |
     |  ----------------------------------------------------------------------
     |  Class methods inherited from collections.abc.Collection:
     |
     |  __subclasshook__(C) from abc.ABCMeta
     |      Abstract classes can override this to customize issubclass().
     |
     |      This is invoked early on by abc.ABCMeta.__subclasscheck__().
     |      It should return True, False or NotImplemented.  If it returns
     |      NotImplemented, the normal algorithm is used.  Otherwise, it
     |      overrides the normal algorithm (and the outcome is cached).

```

```
Help on module lib.sched in lib:

NAME
    lib.sched

CLASSES
    builtins.object
        Sched

    class Sched(builtins.object)
     |  class to manage scheduling tasks
     |
     |  Methods defined here:
     |
     |  __init__(self, settings_file, batcave='batcave')
     |      create a Sched handle object with configuration based on the JSON
     |      |settings_file| which is the path to the settings file. |batcave|
     |      is where all the batch scripts generated by this Sched object are
     |      stored. This is 'batcave' by default, but can be any path. Refer
     |      to the valid dictionary in the code below to know what the required
     |      JSON structure should be for a valid settings file. Refer to the
     |      defaults dictionary in the code below to know what the optional
     |      settings are.
     |
     |  deschedule_task(self)
     |      deschedule the task that is bound to this Sched handle object and
     |      defined by the settings file. Return True on success, False
     |      if the task has not been scheduled yet. Raise
     |      subprocess.CalledProcessError on any other error
     |
     |  details(self)
     |      return a Task named tuple containing schedule details of
     |      the task that is bound to this Sched handle object and defined
     |      by the settings file if the task has been scheduled. If the
     |      task has not been scheduled, then return an empty tuple. Raise
     |      subprocess.CalledProcessError on any other error
     |
     |  is_scheduled(self)
     |      return True if scheduled, False otherwise.
     |      subprocess.CalledProcessError is raised on any error
     |
     |  schedule_task(self)
     |      schedule the task that is bound to this Sched handle object and
     |      defined by the settings file
     |
     |  ----------------------------------------------------------------------
     |  Static methods defined here:
     |
     |  deschedule_task_with_taskname(taskname)
     |      deschedule the task named |taskname|. Return True on success, False
     |      if no task exists with the name |taskname|. Raise
     |      subprocess.CalledProcessError for any other error.
     |
     |  details_for(taskname)
     |      return a Task named tuple associated to |taskname|. If not task
     |      with the name |taskname| exists, then return an empty tuple. If
     |      any other error occurs, raise subprocess.CalledProcessError.
     |
     |  gen_sched_settings_file(settings_filename, **settings)
     |      generate a settings file for this Sched class. |settings_filename| is
     |      the settings filename and |**settings| represents variadic keyword
     |      arguments that are needed as settings to configure the scheduler. This
     |      method attempts to write to the json settings file a maximum of 10 times
     |      every second interval for every time it fails.
     |
     |  is_task_scheduled(taskname)
     |      return True if |taskname| is already scheduled, False otherwise
     |
     |  ----------------------------------------------------------------------
     |  Data descriptors defined here:
     |
     |  __dict__
     |      dictionary for instance variables (if defined)
     |
     |  __weakref__
     |      list of weak references to the object (if defined)

```
