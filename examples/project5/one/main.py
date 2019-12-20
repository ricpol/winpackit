try: import a
except: print('failed to import a')
try: import b
except: print('failed to import b')
try: import foo.foo
except: print('failed to import foo.foo')
try: import c # this is a risky import from "two" package
except: print('failed to import c')
try: import bar.d # this is a risky import from "two" package
except: print('failed to import bar.d')
import sys, os
print('python executable:', sys.executable)
print('current directory:', os.getcwd())
print('sys.path:', sys.path)
input("\nthat's all folks! press enter to quit")
