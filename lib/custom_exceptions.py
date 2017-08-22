class InvalidSettingError(Exception):
   def __init__(self):
      super().__init__()

class NotYetImplemented(Exception):
   def __init__(self):
      super().__init__("not yet implemented")

class InvalidWildcardError(Exception):
   def __init__(self, wildcard_string):
      super().__init__("invalid wildcard: \"{}\"".format(wildcard_string))

class InvalidRegexError(Exception):
   def __init__(self, regex_string):
      super().__init__("invalid regex: \"{}\"".format(regex_string))