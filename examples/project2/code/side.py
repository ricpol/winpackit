try: import a
except: print('failed to import a')
try: import b
except: print('failed to import b')
try: import foo.foo
except: print('failed to import foo.foo')
import os, sys
print('python executable:', sys.executable)
print('current directory:', os.getcwd())
print('sys.path:', sys.path)
input("\nthat's all folks! press enter to quit")
