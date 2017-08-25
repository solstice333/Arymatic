import time

def keep_fkn_trying(
   callback, args=None, kwargs=None, max_attempts=10, interval_sec=1):
   attempts = 0
   most_recent_error = None
   while attempts < max_attempts:
      try:
         if args and kwargs:
            callback(*args, **kwargs)
         elif args:
            callback(*args)
         elif kwargs:
            callback(**kwargs)
         else:
            callback()
      except Exception as err:
         most_recent_error = err
         attempts += 1
         time.sleep(interval_sec)
         continue
      most_recent_error = None
      break

   if most_recent_error:
      raise most_recent_error
