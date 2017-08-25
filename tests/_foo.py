import time
import os

print("running out of {}".format(os.getcwd()))
for s in range(0, 5):
   time.sleep(1)
   print(s + 1)
exit(2)
