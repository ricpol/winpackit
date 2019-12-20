try: import a
except: print('failed to import a')
import sys, os
print('python executable:', sys.executable)
print('current directory:', os.getcwd())
print('sys.path:', sys.path)
input("\nthat's all folks! press enter to quit")
