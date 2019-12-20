import sys, os
errors = []
try:
    import arrow
except:
    errors.append('arrow')
try:
    import requests
except:
    errors.append('requests')
try:
    import wx
except:
    errors.append('wxpython')
try:
    import numpy
except:
    errors.append('numpy')
if errors:
    print('problems importing', ', '.join(errors))
print('python executable:', sys.executable)
print('current directory:', os.getcwd())
print('sys.path:', sys.path)
input("that's all folks! press enter to quit")
