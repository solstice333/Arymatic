import os.path

def get_filename(basename):
   new_filename = basename
   cnt = 0
   while os.path.isfile(new_filename):
      cnt += 1
      parts = list(os.path.splitext(basename))
      parts.insert(1, str(cnt))
      new_filename = ''.join(parts)
   return new_filename

with open(get_filename('_foo.txt'), 'w') as output:
   output.write("running out of {}".format(os.getcwd()))
