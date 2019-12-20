try: import a
except: print('failed to import a')
try: import b
except: print('failed to import b')
try: import foo.foo
except: print('failed to import foo.foo')
import sys, os
try:
    import arrow
    print('Arrow imported')
except:
    print('failed to import Arrow!')
    print('(this might be ok, if you did not include Arrow as a dependency)')
print('python executable:', sys.executable)
print('current directory:', os.getcwd())
print('sys.path:', sys.path)
input("\nthat's all folks! press enter to quit")
