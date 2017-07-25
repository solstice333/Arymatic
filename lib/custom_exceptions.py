class InvalidSettingError(Exception):
   def __init__(self, setting, value):
      super().__init__("invalid setting: ({}:{})".format(setting, value))
