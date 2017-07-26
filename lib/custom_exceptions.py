class InvalidSettingError(Exception):
   def __init__(self, setting, value):
      super().__init__("invalid setting: ({}:{})".format(setting, value))

class NoOptsError(Exception):
   def __init__(self, setting):
      super().__init__(
         "setting '{}' cannot have empty options".format(setting))
