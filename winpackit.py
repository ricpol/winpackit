# -*- coding: utf-8 -*-

"""
This is the WinPackIt script - the quick and dirty Python packager for Windows.

Copyright 2019, Riccardo Polignieri
License: MIT - https://opensource.org/licenses/MIT

Usage: 
- `pip install winpackit`;
- run `python -m winpackit my_runner.py`;
- this will produce a `my_runner.py` runner module in your *current* directory: 
  open it and customize its settings to your liking;
- execute the runner module (`python my_runner.py`);
- this will produce a "build" folder ready to be distributed to the final user.

How does it work:
- this script will download and unpack a Python embeddable package;
- will download and install Pip into it;
- will download and install any needed external dependency;
- will copy your project files;
- optionally, will compile your file to `pyc`;
- will leave a friendly `install.bat` file for the final user to run.
- You may then distribute the resulting "build" folder to your users;
- all they have to do, is to put this folder anywhere on their Windows boxes... 
- ... open it and double-clic on the `install.bat` file;
- this in turn will generate Windows shortcut(s) to the entry-point(s) 
  of your app, tailored for their machine. 

Requirements:
- This script will run on Python 3.6+ with no external dependency needed;
- This script is intended for Windows usage. However, it should be possible 
  to run it from a Linux box too, with a few caveats (see docs for details).

Target requirements:
- This script can generate builds targeted to Python 3.5+: prior to this 
  version there are no Python embeddable packages available;
- you may package any external dependency that is pip-installable in your 
  specific *target* Python.

See examples folder for a few kind of projects you can build with this script.
*** SEE README AND DOCS FOR MORE DETAILS. ***
"""

__all__ = ['BOOTSTRAP_PY_SCRIPT', 'PACKIT_CONFIG_SCRIPT', 'GETPIP_URL', 'PY_URL',
           'LOG_ALWAYS', 'LOG_DEBUG', 'LOG_VERBOSE', 
           'MAX_MAJOR_VERSION', 'MAX_MICRO_VERSIONS', 'MAX_MINOR_VERSIONS', 
           'MIN_TARGET_VERSION', 'Packit', 'make_runner_script', 'version']

import sys
import os
import shutil
import zipfile
import time
import subprocess

from pathlib import Path
from hashlib import md5
from urllib.request import urlretrieve

version = '0.7.0'

# Python version book-keeping
MAX_MICRO_VERSIONS = {(3, 5): 4, (3, 6): 8, (3, 7): 9, (3, 8): 10, 
                      (3, 9): 7, (3, 10): 0}
MAX_MINOR_VERSIONS = {3: 10}
MAX_MAJOR_VERSION = 3          # this won't change for... a while
MIN_TARGET_VERSION = (3, 5, 0) # this won't change, ever

# download urls, md5 sum for embeddable Pythons
PY_URL = {
    (3,10,0,64): ('https://www.python.org/ftp/python/3.10.0/python-3.10.0-embed-amd64.zip', '340408540eeff359d5eaf93139ab90fd'),
    (3,10,0,32): ('https://www.python.org/ftp/python/3.10.0/python-3.10.0-embed-win32.zip', 'dc9d1abc644dd78f5e48edae38c7bc6b'),

    (3,9,7,64): ('https://www.python.org/ftp/python/3.9.7/python-3.9.7-embed-amd64.zip', '67e19ff32b3ef62a40bccd50e33b0f53'),
    (3,9,7,32): ('https://www.python.org/ftp/python/3.9.7/python-3.9.7-embed-win32.zip', '6d12e3e0f942830de8466a83d30a45fb'),
    (3,9,6,64): ('https://www.python.org/ftp/python/3.9.6/python-3.9.6-embed-amd64.zip', '89980d3e54160c10554b01f2b9f0a03b'),
    (3,9,6,32): ('https://www.python.org/ftp/python/3.9.6/python-3.9.6-embed-win32.zip', '5b9693f74979e86a9d463cf73bf0c2ab'),
    (3,9,5,64): ('https://www.python.org/ftp/python/3.9.5/python-3.9.5-embed-amd64.zip', '0b3a4a9ae9d319885eade3ac5aca7d17'),
    (3,9,5,32): ('https://www.python.org/ftp/python/3.9.5/python-3.9.5-embed-win32.zip', 'cacf28418ae39704743fa790d404e6bb'),
    (3,9,4,64): ('https://www.python.org/ftp/python/3.9.4/python-3.9.4-embed-amd64.zip', '5c34eb7e79cfe8a92bf56b5168a459f4'),
    (3,9,4,32): ('https://www.python.org/ftp/python/3.9.4/python-3.9.4-embed-win32.zip', 'b4bd8ec0891891158000c6844222014d'),
    # there is NO 3.9.3: https://bugs.python.org/issue43710
    (3,9,2,64): ('https://www.python.org/ftp/python/3.9.2/python-3.9.2-embed-amd64.zip', 'bd4903eb930cf1747be01e6b8dcdd28a'),
    (3,9,2,32): ('https://www.python.org/ftp/python/3.9.2/python-3.9.2-embed-win32.zip', 'cde7d9bfd87b7777d7f0ba4b0cd4506d'),
    (3,9,1,64): ('https://www.python.org/ftp/python/3.9.1/python-3.9.1-embed-amd64.zip', 'e70e5c22432d8f57a497cde5ec2e5ce2'),
    (3,9,1,32): ('https://www.python.org/ftp/python/3.9.1/python-3.9.1-embed-win32.zip', '96c6fa81fe8b650e68c3dd41258ae317'),
    (3,9,0,64): ('https://www.python.org/ftp/python/3.9.0/python-3.9.0-embed-amd64.zip', '60d0d94337ef657c2cca1d3d9a6dd94b'),
    (3,9,0,32): ('https://www.python.org/ftp/python/3.9.0/python-3.9.0-embed-win32.zip', 'd81fc534080e10bb4172ad7ae3da5247'),

    # no embeddable package available for 3.8.11+
    (3,8,10,64): ('https://www.python.org/ftp/python/3.8.10/python-3.8.10-embed-amd64.zip', '3acb1d7d9bde5a79f840167b166bb633'),
    (3,8,10,32): ('https://www.python.org/ftp/python/3.8.10/python-3.8.10-embed-win32.zip', '659adf421e90fba0f56a9631f79e70fb'),
    (3,8,9,64): ('https://www.python.org/ftp/python/3.8.9/python-3.8.9-embed-amd64.zip', 'cff9e470ee6b57c63c16b8a93c586b28'),
    (3,8,9,32): ('https://www.python.org/ftp/python/3.8.9/python-3.8.9-embed-win32.zip', '40830c33f775641ccfad5bf17ea3a893'),
    (3,8,8,64): ('https://www.python.org/ftp/python/3.8.8/python-3.8.8-embed-amd64.zip', '2096fb5e665c6d2e746da7ff5f31d5db'),
    (3,8,8,32): ('https://www.python.org/ftp/python/3.8.8/python-3.8.8-embed-win32.zip', 'b3e271ee4fafce0ba784bd1b84c253ae'),
    (3,8,7,64): ('https://www.python.org/ftp/python/3.8.7/python-3.8.7-embed-amd64.zip', '61db96411fc00aea8a06e7e25cab2df7'),
    (3,8,7,32): ('https://www.python.org/ftp/python/3.8.7/python-3.8.7-embed-win32.zip', 'efbe9f5f3a6f166c7c9b7dbebbe2cb24'),
    (3,8,6,64): ('https://www.python.org/ftp/python/3.8.6/python-3.8.6-embed-amd64.zip', '5f95c5a93e2d8a5b077f406bc4dd96e7'),
    (3,8,6,32): ('https://www.python.org/ftp/python/3.8.6/python-3.8.6-embed-win32.zip', '7b287a90b33c2a9be55fabc24a7febbb'),
    (3,8,5,64): ('https://www.python.org/ftp/python/3.8.5/python-3.8.5-embed-amd64.zip', '73bd7aab047b81f83e473efb5d5652a0'),
    (3,8,5,32): ('https://www.python.org/ftp/python/3.8.5/python-3.8.5-embed-win32.zip', 'bc354669bffd81a4ca14f06817222e50'),
    (3,8,4,64): ('https://www.python.org/ftp/python/3.8.4/python-3.8.4-embed-amd64.zip', 'c68f60422a0e43dabf54b84a0e92ed6a'),
    (3,8,4,32): ('https://www.python.org/ftp/python/3.8.4/python-3.8.4-embed-win32.zip', '910c307f58282aaa88a2e9df38083ed2'),
    (3,8,3,64): ('https://www.python.org/ftp/python/3.8.3/python-3.8.3-embed-amd64.zip', 'c12ffe7f4c1b447241d5d2aedc9b5d01'),
    (3,8,3,32): ('https://www.python.org/ftp/python/3.8.3/python-3.8.3-embed-win32.zip', '8ee09403ec0cc2e89d43b4a4f6d1521e'),
    (3,8,2,64): ('https://www.python.org/ftp/python/3.8.2/python-3.8.2-embed-amd64.zip', '1a98565285491c0ea65450e78afe6f8d'),
    (3,8,2,32): ('https://www.python.org/ftp/python/3.8.2/python-3.8.2-embed-win32.zip', '1b1f0f0c5ee8601f160cfad5b560e3a7'),
    (3,8,1,64): ('https://www.python.org/ftp/python/3.8.1/python-3.8.1-embed-amd64.zip', '4d091857a2153d9406bb5c522b211061'),
    (3,8,1,32): ('https://www.python.org/ftp/python/3.8.1/python-3.8.1-embed-win32.zip', '980d5745a7e525be5abf4b443a00f734'),
    (3,8,0,64): ('https://www.python.org/ftp/python/3.8.0/python-3.8.0-embed-amd64.zip', '99cca948512b53fb165084787143ef19'),
    (3,8,0,32): ('https://www.python.org/ftp/python/3.8.0/python-3.8.0-embed-win32.zip', '2ec3abf05f3f1046e0dbd1ca5c74ce88'),

    # no embeddable package available for 3.7.10/3.7.12
    (3,7,9,64): ('https://www.python.org/ftp/python/3.7.9/python-3.7.9-embed-amd64.zip', '60f77740b30030b22699dbd14883a4a3'),
    (3,7,9,32): ('https://www.python.org/ftp/python/3.7.9/python-3.7.9-embed-win32.zip', '97c6558d479dc53bf448580b66ad7c1e'),
    (3,7,8,64): ('https://www.python.org/ftp/python/3.7.8/python-3.7.8-embed-amd64.zip', '5ae191973e00ec490cf2a93126ce4d89'),
    (3,7,8,32): ('https://www.python.org/ftp/python/3.7.8/python-3.7.8-embed-win32.zip', '5f0f83433bd57fa55182cb8ea42d43d6'),
    (3,7,7,64): ('https://www.python.org/ftp/python/3.7.7/python-3.7.7-embed-amd64.zip', '6aa3b1c327561bda256f2deebf038dc9'),
    (3,7,7,32): ('https://www.python.org/ftp/python/3.7.7/python-3.7.7-embed-win32.zip', 'e9db9cf43b4f2472d75a055380871045'),
    (3,7,6,64): ('https://www.python.org/ftp/python/3.7.6/python-3.7.6-embed-amd64.zip', '5f84f4f62a28d3003679dc693328f8fd'),
    (3,7,6,32): ('https://www.python.org/ftp/python/3.7.6/python-3.7.6-embed-win32.zip', 'accb8a137871ec632f581943c39cb566'),
    (3,7,5,64): ('https://www.python.org/ftp/python/3.7.5/python-3.7.5-embed-amd64.zip', '436b0f803d2a0b393590030b1cd59853'),
    (3,7,5,32): ('https://www.python.org/ftp/python/3.7.5/python-3.7.5-embed-win32.zip', '726877d1a1f5a7dc68f6a4fa48964cd1'),
    (3,7,4,64): ('https://www.python.org/ftp/python/3.7.4/python-3.7.4-embed-amd64.zip', '9b00c8cf6d9ec0b9abe83184a40729a2'),
    (3,7,4,32): ('https://www.python.org/ftp/python/3.7.4/python-3.7.4-embed-win32.zip', '9fab3b81f8841879fda94133574139d8'),
    (3,7,3,64): ('https://www.python.org/ftp/python/3.7.3/python-3.7.3-embed-amd64.zip', '854ac011983b4c799379a3baa3a040ec'),
    (3,7,3,32): ('https://www.python.org/ftp/python/3.7.3/python-3.7.3-embed-win32.zip', '70df01e7b0c1b7042aabb5a3c1e2fbd5'),
    (3,7,2,64): ('https://www.python.org/ftp/python/3.7.2/python-3.7.2.post1-embed-amd64.zip', 'f81568590bef56e5997e63b434664d58'),
    (3,7,2,32): ('https://www.python.org/ftp/python/3.7.2/python-3.7.2.post1-embed-win32.zip', '26881045297dc1883a1d61baffeecaf0'),
    (3,7,1,64): ('https://www.python.org/ftp/python/3.7.1/python-3.7.1-embed-amd64.zip', '74f919be8add2749e73d2d91eb6d1da5'),
    (3,7,1,32): ('https://www.python.org/ftp/python/3.7.1/python-3.7.1-embed-win32.zip', 'aa4188ea480a64a3ea87e72e09f4c097'),
    (3,7,0,64): ('https://www.python.org/ftp/python/3.7.0/python-3.7.0-embed-amd64.zip', 'cb8b4f0d979a36258f73ed541def10a5'),
    (3,7,0,32): ('https://www.python.org/ftp/python/3.7.0/python-3.7.0-embed-win32.zip', 'ed9a1c028c1e99f5323b9c20723d7d6f'),

    # no embeddable package available for 3.6.9/3.6.10
    (3,6,8,64): ('https://www.python.org/ftp/python/3.6.8/python-3.6.8-embed-amd64.zip', '73df7cb2f1500ff36d7dbeeac3968711'),
    (3,6,8,32): ('https://www.python.org/ftp/python/3.6.8/python-3.6.8-embed-win32.zip', '60470b4cceba52094121d43cd3f6ce3a'),
    (3,6,7,64): ('https://www.python.org/ftp/python/3.6.7/python-3.6.7-embed-amd64.zip', '7617e04b9dafc564f680e37c2f2398b8'),
    (3,6,7,32): ('https://www.python.org/ftp/python/3.6.7/python-3.6.7-embed-win32.zip', 'a993744c9daa6d159712c8a35374ca9c'),
    (3,6,6,64): ('https://www.python.org/ftp/python/3.6.6/python-3.6.6-embed-amd64.zip', '7148ec14edfdc13f42e06a14d617c921'),
    (3,6,6,32): ('https://www.python.org/ftp/python/3.6.6/python-3.6.6-embed-win32.zip', 'b4c424de065bad238c71359f3cd71ef2'),
    (3,6,5,64): ('https://www.python.org/ftp/python/3.6.5/python-3.6.5-embed-amd64.zip', '04cc4f6f6a14ba74f6ae1a8b685ec471'),
    (3,6,5,32): ('https://www.python.org/ftp/python/3.6.5/python-3.6.5-embed-win32.zip', 'b0b099a4fa479fb37880c15f2b2f4f34'),
    (3,6,4,64): ('https://www.python.org/ftp/python/3.6.4/python-3.6.4-embed-amd64.zip', 'd2fb546fd4b189146dbefeba85e7266b'),
    (3,6,4,32): ('https://www.python.org/ftp/python/3.6.4/python-3.6.4-embed-win32.zip', '15802be75a6246070d85b87b3f43f83f'),
    (3,6,3,64): ('https://www.python.org/ftp/python/3.6.3/python-3.6.3-embed-amd64.zip', 'b1daa2a41589d7504117991104b96fe5'),
    (3,6,3,32): ('https://www.python.org/ftp/python/3.6.3/python-3.6.3-embed-win32.zip', 'cf1c75ad7ccf9dec57ba7269198fd56b'),
    (3,6,2,64): ('https://www.python.org/ftp/python/3.6.2/python-3.6.2-embed-amd64.zip', '0fdfe9f79e0991815d6fc1712871c17f'),
    (3,6,2,32): ('https://www.python.org/ftp/python/3.6.2/python-3.6.2-embed-win32.zip', '2ca4768fdbadf6e670e97857bfab83e8'),
    (3,6,1,64): ('https://www.python.org/ftp/python/3.6.1/python-3.6.1-embed-amd64.zip', '708496ebbe9a730d19d5d288afd216f1'),
    (3,6,1,32): ('https://www.python.org/ftp/python/3.6.1/python-3.6.1-embed-win32.zip', '8dff09a1b19b7a7dcb915765328484cf'),
    (3,6,0,64): ('https://www.python.org/ftp/python/3.6.0/python-3.6.0-embed-amd64.zip', '0ec0caeea75bae5d2771cf619917c71f'),
    (3,6,0,32): ('https://www.python.org/ftp/python/3.6.0/python-3.6.0-embed-win32.zip', '1adf2fb735c5000af32d42c39136727c'),

    # no embeddable package available for 3.5.5/3.5.9
    (3,5,4,64): ('https://www.python.org/ftp/python/3.5.4/python-3.5.4-embed-amd64.zip', '1b56c67f3c849446794a15189f425f53'),
    (3,5,4,32): ('https://www.python.org/ftp/python/3.5.4/python-3.5.4-embed-win32.zip', '3ce7b067ddd9a91bb221351d9370ebe9'),
    (3,5,3,64): ('https://www.python.org/ftp/python/3.5.3/python-3.5.3-embed-amd64.zip', '1264131c4c2f3f935f34c455bceedee1'),
    (3,5,3,32): ('https://www.python.org/ftp/python/3.5.3/python-3.5.3-embed-win32.zip', '7dbd6043bd041ed3db738ad90b6d697f'),
    (3,5,2,64): ('https://www.python.org/ftp/python/3.5.2/python-3.5.2-embed-amd64.zip', 'f1c24bb78bd6dd792a73d5ebfbd3b20e'),
    (3,5,2,32): ('https://www.python.org/ftp/python/3.5.2/python-3.5.2-embed-win32.zip', 'ad637a1db7cf91e344318d55c94ad3ca'),
    (3,5,1,64): ('https://www.python.org/ftp/python/3.5.1/python-3.5.1-embed-amd64.zip', 'b07d15f515882452684e0551decad242'),
    (3,5,1,32): ('https://www.python.org/ftp/python/3.5.1/python-3.5.1-embed-win32.zip', '6e783d8fd44570315d488b9a9881ff10'),
    (3,5,0,64): ('https://www.python.org/ftp/python/3.5.0/python-3.5.0-embed-amd64.zip', '09a9bcabcbf8c616c21b1e5a6eaa9129'),
    (3,5,0,32): ('https://www.python.org/ftp/python/3.5.0/python-3.5.0-embed-win32.zip', '6701f6eba0697949bc9031e887e27b32'),
    # and that's it - no embeddable zip file before 3.5!
    }

# download url, md5 sum for Get-pip
# (note: afaik there is no official, published md5 checksum for Get-pip)
GETPIP_URL = ('https://bootstrap.pypa.io/get-pip.py', '')

# users will run this script on their own pc to finalize installation 
BOOTSTRAP_PY_SCRIPT = """\
# -*- coding: utf-8 -*-
# This was created by the WinPackIt script - please do not remove

import os
import subprocess
from pathlib import Path

HERE = Path(__file__).parent.resolve()
os.chdir(str(HERE))
PY_DIR = (HERE / '..' / '{pydirname}').resolve()
PROJECY_DIRS = {proj_dirs}
ENTRY_POINTS = {entrypoints}
BUILD_DIR = HERE.parent.resolve()
PYC_ONLY = {pyc_only}
COMPILE_PYCS = {compile_pycs} # compile py to pyc "delayed install"
HAVE_PIP = {have_pip} # Pip "delayed install"
HAVE_DEPS = {have_deps} # dependencies "delayed install"
WELCOME_MESSAGE = {welcome}
GOODBYE_MESSAGE = {goodbye}

def compile_pycs():
    if not COMPILE_PYCS:
        return
    pyexec = str(PY_DIR / 'python.exe')
    with open('install.log', 'a') as f:
        f.write('*** compile py modules ***\\n')
        f.flush()
        for d in PROJECY_DIRS:
            d = Path(HERE.parent / d).resolve()
            args = [pyexec, '-m', 'compileall', str(d)]
            if PYC_ONLY:
                args.append('-b')
            subprocess.run(args, stdout=f, stderr=subprocess.STDOUT)
            if PYC_ONLY:
                for py in d.glob('**/*.py'):
                    py.unlink()
        f.write('*******************\\n\\n')

def install_dependencies():
    if not HAVE_DEPS:
        return
    pyexec = str(PY_DIR / 'python.exe')
    with open('install.log', 'a') as f:
        f.write('*** install dependencies ***\\n')
        f.flush()
        subprocess.run([pyexec, '-m', 'pip', 'install', 
                        '-r', 'requirements.txt', '--no-cache'], 
                       stdout=f, stderr=subprocess.STDOUT)
        f.write('*******************\\n\\n')

def install_pip():
    if not HAVE_PIP:
        return
    pyexec = str(PY_DIR / 'python.exe')
    with open('install.log', 'a') as f:
        f.write('*** install pip ***\\n')
        f.flush()
        subprocess.run([pyexec, 'get-pip.py', '--no-cache'], 
                       stdout=f, stderr=subprocess.STDOUT)
        f.write('*******************\\n\\n')

def make_shortcut():
    if not ENTRY_POINTS:
        return
    # There is no way to make a Windows shortcut from vanilla Python.
    # So we make a PowerShell script on-the-fly instead, and subprocess.run it.
    # Also, no f-strings here, to be 3.5-compatible.
    ps = '$Shell = New-Object -ComObject WScript.Shell\\n\\n'
    for pth, name, flavor in ENTRY_POINTS:
        ps += '$Shortcut = $Shell.CreateShortcut("%s/%s.lnk")\\n' % (BUILD_DIR, name)
        if flavor == '':
            abs_pth = (HERE.parent / pth).resolve()
            ps += '$Shortcut.TargetPath = "`"%s`""\\n' % abs_pth
            ps += '$Shortcut.Save()\\n\\n'
        else:
            pyexec = 'pythonw.exe' if flavor=='pyw' else 'python.exe'
            ps += '$Shortcut.TargetPath = "`"%s/%s`""\\n' % (PY_DIR, pyexec)
            abs_pth = Path(HERE.parent / pth)
            if PYC_ONLY:
                abs_pth = abs_pth.with_suffix('.pyc')
            abs_pth = abs_pth.resolve()
            ps += '$Shortcut.Arguments = "`"%s`""\\n' % abs_pth
            ps += '$Shortcut.WorkingDirectory = "%s"\\n' % abs_pth.parent
            ps += '$Shortcut.Save()\\n\\n'
    try:
        os.remove('make_shortcuts.ps1')
    except:
        pass
    with open('make_shortcuts.ps1', 'a') as f:
        f.write(ps)
    subprocess.run(['powershell', '-ExecutionPolicy', 'Bypass', 
                   './make_shortcuts.ps1'])

def post_deploy_action():
    # Insert your custom post-deploy actions here.
    # Make sure the code is compatible with the *target* Python, 
    # if different from your current Python. 
    pass

if __name__ == '__main__':
    print(WELCOME_MESSAGE)
    install_pip()
    install_dependencies()
    compile_pycs()
    make_shortcut()
    post_deploy_action()
    input(GOODBYE_MESSAGE)

"""

# output levels
LOG_ALWAYS = 0
LOG_VERBOSE = 1
LOG_DEBUG = 2

def _md5compare(filepath, md5hash=''):
    if not md5hash:
        return True
    with open(filepath,'rb') as fp:
        h = md5()
        buffer = fp.read(4096)
        while len(buffer) > 0:
            h.update(buffer)
            buffer = fp.read(4096)
    return h.hexdigest() == md5hash

class Packit:
    def __init__(self, settings):
        # "settings": in normal usage, a namedtuple used by the runner script
        # to collect all settings together (see make_runner_script below). 
        # If you are importing this class you may pass whatever object
        # your need with the same api (eg a dataclass).
        self.cfg = settings
        self.cache_dir = self.cfg.HERE / 'winpackit_cache'
        # our project configuration, to be figured out later
        self.proj_dirs = None # project dir(s)
        self.copy_dirs = None # other non-project dir(s)
        # target ("build") configuration, to be figured out later:
        timestr = time.strftime('%Y%m%d_%H%M%S')
        self.build_dir = self.cfg.HERE / f'winpackit_build_{timestr}'
        self.bootstrap_dir = None # "service" dir for bootstrap script
        self.target_py_version = None # Python version
        self.target_py_dir = None # Python root directory
        self.pip_is_present = False # if Pip is currently installed
        self.target_proj_dirs = None # project dir(s)
        self.target_proj_dirs_relative = None # id, relative to self.build_dir
        self.target_copy_dirs = None # other non-project dir(s)
        self.entry_points = None # entry points (to both "projects" and "copy")
        # options to delay installing things on target:
        self.delay_have_pip = False
        self.delay_have_dependencies = False
        self.delay_compile_pycs = False
        if self.cfg.PIP_CACHE:
            self.cfg.PIP_ARGS.append(f'--cache-dir={self.cache_dir}')
        else:
            self.cfg.PIP_ARGS.append('--no-cache-dir')
        if self.cfg.VERBOSE == 0:
            self.cfg.PIP_ARGS.append('-qqq')
        self.cfg.PROJECT_FILES_IGNORE_PATTERNS.append('__pycache__')
        
    def msg(self, verbose, *args):
        if verbose <= self.cfg.VERBOSE:
            print(*args)

    def run_subprocess(self, *args):
        """Call subprocess.run(args). Return False if retcode!=0."""
        ret = subprocess.run(args)
        if ret.returncode != 0:
            self.msg(LOG_VERBOSE, 'ERROR: unable to run external process!')
            self.msg(LOG_VERBOSE, 'Process was called with arguments:')
            self.msg(LOG_VERBOSE, ret.args)
            self.msg(LOG_VERBOSE, f'Process exited with code {ret.returncode}.')
            return False
        self.msg(LOG_DEBUG, '->Debug - ret.args:', ret.args)
        return True

    def getfile(self, fileurl, checksum='', on_error_abort=False):
        """Download fileurl into self.cache_dir. 
        Return downloaded filepath, or empty string on failed download or 
        failed md5 checksum verification. If checksum=None, no verification 
        will occur. 
        If on_error_abort=True, on failed download exit with stacktrace.""" 
        filename = fileurl.split('/')[-1]
        target_filepath = self.cache_dir / filename
        if self.cfg.USE_CACHE and target_filepath.exists():
            self.msg(LOG_VERBOSE, f'Using cached {filename}...')
        else:
            try:  # Python 3.8 has "missing_ok=True" here...
                target_filepath.unlink()
            except FileNotFoundError:
                pass
            self.msg(LOG_VERBOSE, 
                     f'Downloading {filename}...\nDownload from {fileurl}')
            try:
                urlretrieve(str(fileurl), target_filepath)
            except Exception as e:
                if on_error_abort:
                    self.msg(LOG_ALWAYS, 
                             f"FATAL: can't download {filename}! Aborting...")
                    raise  # this will exit with a stacktrace
                self.msg(LOG_VERBOSE, f"ERROR: can't download {filename}!")
                self.msg(LOG_VERBOSE, 'The following exception was raised:')
                self.msg(LOG_VERBOSE, e.__class__.__name__, e.args)
                return ''
        if not _md5compare(target_filepath, checksum):
            new = target_filepath.with_name(f'XXX_BADMD5_{filename}')
            target_filepath.rename(new)
            if on_error_abort:
                self.msg(LOG_ALWAYS, f'FATAL: bad md5 checksum for {filename}!')
                sys.exit(1)
            self.msg(LOG_VERBOSE, f'ERROR: bad md5 checksum for {filename}!')
            return ''
        self.msg(LOG_DEBUG, '->Debug - target_filepath:', target_filepath)
        return target_filepath

    def parse_pyversion(self):
        """Read self.cfg.PYTHON_VERSION and figure out which Python we want.
        Return and set self.target_py_version."""
        self.msg(LOG_VERBOSE, "Choosing Python version...")
        # fallback version: current Python OR min possible with current arch.
        ma, mi, mc = sys.version_info[:3]
        arch = 64 if sys.maxsize > 2**32 else 32
        if (ma, mi, mc) < MIN_TARGET_VERSION:
            ma, mi = MIN_TARGET_VERSION[:2]
            mc = MAX_MICRO_VERSIONS[(ma, mi)] # long story short, latest 3.5.x
        fallback = ma, mi, mc, arch
        self.msg(LOG_DEBUG, '->Debug - fallback Py version:', fallback)
        # architecture parsing
        wanted_py = self.cfg.PYTHON_VERSION
        ma, mi, mc, arch = None, None, None, 64
        try:
            wanted_py, architecture = wanted_py.split('-')
            if architecture == '32':
                arch = 32
        except ValueError:
            pass
        # If can't parse version numbers, use fallback
        try:
            wanted_py = list(map(int, wanted_py.split('.')))
        except ValueError:
            self.msg(LOG_VERBOSE, f"Can't figure out <{self.cfg.PYTHON_VERSION}>.",
                     f'Dafaulting to <{fallback}>.')
            self.target_py_version = fallback
            return self.target_py_version
        # major number parsing
        ma = wanted_py[0]
        if ma < MIN_TARGET_VERSION[0]:  # if Python 2, use fallback
            self.msg(LOG_VERBOSE, 
                     f"Can't use <{self.cfg.PYTHON_VERSION}> as target Python.", 
                     f'Defaulting to <{fallback}>.')
            self.target_py_version = fallback
            return self.target_py_version
        elif ma > MAX_MAJOR_VERSION:
            ma = MAX_MAJOR_VERSION
        # minor number parsing
        try:
            mi = wanted_py[1]
            if mi > MAX_MINOR_VERSIONS[ma]:
                mi = MAX_MINOR_VERSIONS[ma]
        except IndexError:
            mi = MAX_MINOR_VERSIONS[ma]
        # micro number parsing
        try:
            mc = wanted_py[2]
            if mc > MAX_MICRO_VERSIONS[(ma, mi)]:
                mc = MAX_MICRO_VERSIONS[(ma, mi)]
        except IndexError:
            mc = MAX_MICRO_VERSIONS[(ma, mi)]
        self.target_py_version = ma, mi, mc, arch
        self.msg(LOG_VERBOSE, f'Version <{self.target_py_version}> needed.')
        return self.target_py_version

    def prepare_dirs(self):
        """Make build dir, parse PROJECTS and COPY_DIRS settings to figure out
        original/target dirs to be copied later, and entry point machinery."""
        self.cache_dir.mkdir(exist_ok=True)
        if self.build_dir.exists():
            try:
                shutil.rmtree(self.build_dir)
            except:
                self.msg(LOG_ALWAYS, 
                         f"FATAL: Can't delete existing <{self.build_dir}>.")
                raise # this will exit with stacktrace
        self.build_dir.mkdir()
        self.bootstrap_dir = self.build_dir / 'winpackit_bootstrap'
        self.bootstrap_dir.mkdir(exist_ok=True)
        self.proj_dirs = []
        self.copy_dirs = []
        self.target_proj_dirs = []
        self.target_proj_dirs_relative = []
        self.target_copy_dirs = []
        self.entry_points = []
        if self.cfg.PROJECTS:
            for project in self.cfg.PROJECTS:
                proj_dir = self.cfg.HERE / Path(project[0])
                target_projdir = self.build_dir / proj_dir.name
                self.proj_dirs.append(proj_dir)
                self.target_proj_dirs.append(target_projdir)
                self.target_proj_dirs_relative.append(proj_dir.name)
                try:
                    self._prepare_entry_points(project[1:], proj_dir)
                except KeyError: # no entry-point here
                    pass
        if self.cfg.COPY_DIRS:
            for cdir in self.cfg.COPY_DIRS:
                copydir = self.cfg.HERE / Path(cdir[0])
                target_copydir = self.build_dir / copydir.name
                self.copy_dirs.append(copydir)
                self.target_copy_dirs.append(target_copydir)
                try:
                    self._prepare_entry_points(cdir[1:], copydir)
                except KeyError: # no entry-point here
                    pass
        self.msg(LOG_DEBUG, '->Debug - entry points:', self.entry_points)

    def _prepare_entry_points(self, entrypoints, basedir):
        for entrypath, name in entrypoints:
            entrypath = Path(entrypath)
            entrypath = basedir.name / entrypath 
            if entrypath.suffix == '.py':
                flavor = 'py'
            elif entrypath.suffix == '.pyw':
                flavor = 'pyw'
            else:
                flavor = ''
            # entrypath: the target Path, relative to root project directory
            entry = [entrypath, name, flavor]
            self.entry_points.append(entry)

    def obtain_python(self):
        """Download Python, return filepath. If fail, exit with stacktrace."""
        self.msg(LOG_VERBOSE, "\n****** Obtaining Python ******")
        pyfile, checksum = PY_URL[self.parse_pyversion()]
        f = self.getfile(pyfile, checksum=checksum, on_error_abort=True)
        self.msg(LOG_VERBOSE, 'Python successfully obtained.')
        return f

    def obtain_getpip(self):
        """Download Get-pip, return filepath. If fails, return empty string."""
        self.msg(LOG_VERBOSE, "\n****** Obtaining Get-pip ******")
        if not self.cfg.PIP_REQUIRED:
            self.msg(LOG_VERBOSE, 'Skipped: no Pip required in config file.')
            return ''
        f, checksum = GETPIP_URL
        getpip = self.getfile(f, checksum=checksum, on_error_abort=False)
        if getpip:
            self.msg(LOG_VERBOSE, 'Get-pip successfully obtained.')
        else:
            self.msg(LOG_VERBOSE, 'ERROR: Get-pip not obtained.')
        return getpip

    def unpack_python(self, pyfile):
        """Unzip Python package. If fail, exit with stacktrace."""
        self.msg(LOG_VERBOSE, "\n****** Installing Python ******")
        self.target_py_dir = self.build_dir / pyfile.stem
        self.target_py_dir.mkdir(exist_ok=True)
        self.msg(LOG_VERBOSE, 'Unzipping...')
        try:
            with zipfile.ZipFile(pyfile, 'r') as python_zip:
                python_zip.extractall(self.target_py_dir)
        except:
            self.msg(LOG_ALWAYS, 
                     f"FATAL: can't unzip {pyfile} in {self.target_py_dir}!")
            raise  # this will exit with a stacktrace
        (self.target_py_dir / 'Lib' / 'site-packages').mkdir(parents=True)
        self.msg(LOG_VERBOSE, 'Fixing path search machinery...')
        if self.target_py_version < (3, 6, 0, 32):
            ret = self._fix_imports_py35()
        else:
            ret = self._fix_imports()
        self.msg(LOG_VERBOSE, 'Python successfully installed.')
        if self.cfg.VERBOSE >= LOG_DEBUG:
            self.msg(LOG_DEBUG, '->Debug - checking sys.path on target Python')
            pyexec = self.target_py_dir / 'python.exe'
            subprocess.run((str(pyexec), '-c', 'import sys; print(sys.path)'))
        return ret

    def _fix_imports(self):
        # we add paths to ._pth file, which is better than using 
        # sitecustomize.py because this way we don't need to import site, 
        # thus providing a better isolation for our distribution.
        self.msg(LOG_DEBUG, '->Debug - Fixing ._pth file')
        pth_file = [i for i in os.listdir(self.target_py_dir) 
                    if i.endswith('._pth')][0]
        with open(self.target_py_dir / pth_file, 'a') as f:
            f.write('Lib/site-packages\n')
            for pth in self.target_proj_dirs:
                f.write(f'../{pth.name}\n')
            #f.write('import site\n') # this could be dangerous!
        return True

    def _fix_imports_py35(self):
        # Python 3.5 has no support for ._pth files
        # BUT ships with a "pyvenv.cfg" that SHOULD be good enough.
        # Compare https://docs.python.org/3.5/using/windows.html#finding-modules
        # with    https://docs.python.org/3.6/using/windows.html#finding-modules
        # However, to enforce our "all PROJECTS must be in sys.path" rule here,
        # we must add a sitecustomize.py file
        self.msg(LOG_DEBUG, '->Debug - py3.5, no support for ._pth files!')
        self.msg(LOG_DEBUG, '->Debug - Fixing sitecustomize.py')
        customizepath = self.target_py_dir/'Lib'/'site-packages'/'sitecustomize.py'
        customizetxt = 'import sys\nfrom pathlib import Path\n'
        for pth in self.target_proj_dirs:
            customizetxt += "sys.path.insert(0, '')\n"
            customizetxt += f'p = Path(sys.prefix).parent / "{pth.name}"\n'
            customizetxt += 'sys.path.append(str(p))\n'
        _ = customizepath.write_text(customizetxt)
        return True

    def _install_pip_now(self, getpipfile):
        """Use Get-pip to install Pip. Return False if something went wrong.
        Also, set self.pip_is_present if Pip was successfully installed."""
        pyexec = self.target_py_dir / 'python.exe'
        args = str(pyexec), str(getpipfile), *self.cfg.PIP_ARGS
        if self.run_subprocess(*args):
            self.msg(LOG_VERBOSE, 'Pip successfully installed', 
                     '(ignore the "add to PATH" warnings above).')
            self.pip_is_present = True
            return True
        return False
    
    def _install_pip_delayed(self, getpipfile):
        """Install Pip in the 'delayed install' scenario: copy Get-pip into 
        the distribution folder, then leave a post-deploy instruction.
        Also, set self.pip_is_present."""
        dest = self.bootstrap_dir / 'get-pip.py'
        shutil.copy(getpipfile, dest)
        self.delay_have_pip = True
        self.pip_is_present = True
        self.msg(LOG_VERBOSE, 'Pip will be installed on the user machine.')
        return True

    def install_pip(self, getpipfile):
        """Install Pip. Return False if something went wrong.
        Also, set self.pip_is_present if Pip was successfully installed."""
        self.msg(LOG_VERBOSE, "\n****** Installing Pip ******")
        if not self.cfg.PIP_REQUIRED:
            self.msg(LOG_VERBOSE, 'Skipped: no Pip required in config file.')
            return True
        if not getpipfile:
            self.msg(LOG_VERBOSE, 'ERROR: no Get-pip present.')
            return False
        if self.cfg.DELAYED_INSTALL:
            return self._install_pip_delayed(getpipfile)
        else:
            return self._install_pip_now(getpipfile)

    def _install_dependencies_now(self):
        """Uses pip to install dependencies. 
        Return False if something went wrong."""
        pyexec = self.target_py_dir / 'python.exe'
        return_codes = []
        if self.cfg.REQUIREMENTS:
            self.msg(LOG_VERBOSE, f'Installing from {self.cfg.REQUIREMENTS}...')
            args = [str(pyexec), '-m', 'pip'] + self.cfg.PIP_ARGS 
            args += ['install', '-r', self.cfg.REQUIREMENTS] 
            args += self.cfg.PIP_INSTALL_ARGS
            ret = self.run_subprocess(*args)
            return_codes.append(ret)
        else:
            self.msg(LOG_VERBOSE, 'No requirements file found.')
        if self.cfg.DEPENDENCIES:
            self.msg(LOG_VERBOSE, 'Installing from custom list of packages...')
            for package in self.cfg.DEPENDENCIES:
                args = [str(pyexec), '-m', 'pip', 'install', package]
                args += self.cfg.PIP_ARGS + self.cfg.PIP_INSTALL_ARGS
                ret = self.run_subprocess(*args)
                return_codes.append(ret)
        else:
            self.msg(LOG_VERBOSE, 'No packages list found.')
        if all(return_codes):
            self.msg(LOG_VERBOSE, 'All dependencies successfully installed.')
            return True
        else:
            self.msg(LOG_VERBOSE, 
                     'ERROR: not all dependencies successfully installed.')
            return False

    def _install_dependencies_delayed(self):
        """Install dependencies in the 'delayed install' scenario: leave a
        requirements.txt in the dist folder and post-deploy instructions."""
        dest = self.bootstrap_dir / 'requirements.txt'
        if self.cfg.REQUIREMENTS:
            shutil.copy(self.cfg.REQUIREMENTS, dest)
        with open(dest, 'a') as f:
            for req in self.cfg.DEPENDENCIES:
                f.write(req+'\n')
        self.delay_have_dependencies = True
        self.msg(LOG_VERBOSE, 
                 'Dependencies will be installed on the user machine.')
        return True

    def install_dependencies(self):
        """Install dependencies. Return False if something went wrong."""
        self.msg(LOG_VERBOSE, "\n****** Installing dependencies ******")
        want_dependencies = self.cfg.REQUIREMENTS or self.cfg.DEPENDENCIES
        if not want_dependencies:
            self.msg(LOG_VERBOSE, 'Skipped: no dependency wanted.')
            return True
        if not self.pip_is_present:
            self.msg(LOG_VERBOSE, 
                     "ERROR: can't install dependencies, no Pip present.")
            return False
        if self.cfg.DELAYED_INSTALL:
            return self._install_dependencies_delayed()
        else:
            return self._install_dependencies_now()

    def _copy_files(self, orig, dest, ignore=None):
        """Run shutil.copytree, return False if errors occurred."""
        try:
            shutil.copytree(orig, dest, ignore=ignore)
            self.msg(LOG_VERBOSE, f'Files copied into {dest}.')
            return True
        except Exception as e:
            self.msg(LOG_VERBOSE, f"ERROR: can't copy {orig}!")
            self.msg(LOG_VERBOSE, 'The following exception was raised:')
            self.msg(LOG_VERBOSE, e.__class__.__name__, e.args)
            return False

    def copy_project_files(self):
        """Copy project(s) files. Return False if any error occurred."""
        self.msg(LOG_VERBOSE, "\n****** Copying project files ******")
        if not self.target_proj_dirs:
            self.msg(LOG_VERBOSE, 'Skipped, no projects present.')
            return True
        self.msg(LOG_DEBUG, '->Debug - Copytree ignore patterns:', 
                 self.cfg.PROJECT_FILES_IGNORE_PATTERNS)
        no_errors = True
        for orig, dest in zip(self.proj_dirs, self.target_proj_dirs):
            if not self._copy_files(orig, dest, ignore=shutil.ignore_patterns(
                                    *self.cfg.PROJECT_FILES_IGNORE_PATTERNS)):
                no_errors = False
        if not no_errors:
            self.msg(LOG_VERBOSE, 'ERROR: not all projects successfully copied.')
        return no_errors

    def copy_other_files(self):
        """Copy non-project files, i.e. those in COPY_DIRS."""
        self.msg(LOG_VERBOSE, "\n****** Copying other dirs ******")
        if not self.target_copy_dirs:
            self.msg(LOG_VERBOSE, 'Skipped, no other dirs to copy.')
            return True
        no_errors = True
        for orig, dest in zip(self.copy_dirs, self.target_copy_dirs):
            if not self._copy_files(orig, dest):
                no_errors = False
        if not no_errors:
            self.msg(LOG_VERBOSE, 'ERROR: not all projects successfully copied.')
        return no_errors

    def _compile_files_delayed(self):
        """Leave instructions to compile py modules 
        in the 'delayed install' scenario."""
        self.delay_compile_pycs = True
        self.msg(LOG_VERBOSE, 'Modules will be compiled on the user machine.')
        return True

    def _compile_files_now(self):
        """Compile all py modules, remove originals if needed."""
        got_errors = False
        # MUST compile with target python, not our current python!
        py_exec = self.target_py_dir / 'python.exe'
        quiet = '-q' if self.cfg.VERBOSE else '-qq'
        for d in self.target_proj_dirs:
            args = [str(py_exec), '-m', 'compileall', str(d)]
            if self.cfg.PYC_ONLY_DISTRIBUTION:
                args.append('-b')
            args.append(quiet)
            ret = self.run_subprocess(*args)
            if not ret:
                self.msg(LOG_VERBOSE, 
                         f'ERROR: not all modules successfully compiled in {d}.')
                got_errors = True
        if got_errors:
            self.msg(LOG_VERBOSE, 'ERROR: not all modules successfully compiled.')
            return False
        self.msg(LOG_VERBOSE, 'All modules successfully compiled.')
        if self.cfg.PYC_ONLY_DISTRIBUTION:
            for d in self.target_proj_dirs:
                for f in d.glob('**/*.py'):
                    f.unlink()
            self.msg(LOG_VERBOSE, 'Original *.py modules removed.')
            # we need to point our entrypoint list to the new pyc files, 
            # since there are no more py files
            for n, entrypoint in enumerate(self.entry_points):
                if entrypoint[2] != '':
                    self.entry_points[n][0] = self.entry_points[n][0].with_suffix('.pyc')
            self.msg(LOG_DEBUG, '->Debug - renamed (py->pyc) entry-points:', 
                     self.entry_points)
        return True

    def compile_files(self):
        """Compile py modules."""
        self.msg(LOG_VERBOSE, "\n****** Compiling project modules ******")
        if not self.target_proj_dirs:
            self.msg(LOG_VERBOSE, 'Skipped, no projects present.')
            return True
        if not self.cfg.COMPILE:
            self.msg(LOG_VERBOSE, 'Skipped, no compiling required.')
            return True
        if self.cfg.PYC_ONLY_DISTRIBUTION:
            # we must rename '*.pyw' file to '*.py', or they won't be compiled!
            for n, entrypoint in enumerate(self.entry_points):
                if entrypoint[2] == 'pyw':
                    old = self.build_dir / entrypoint[0]
                    new = old.with_suffix('.py')
                    os.rename(old, new)
                    # book-keeping...
                    self.entry_points[n][0] = self.entry_points[n][0].with_suffix('.py')
            self.msg(LOG_DEBUG, '->Debug - renamed (pyw->py) entry-points:', 
                     self.entry_points)
        if self.cfg.DELAYED_INSTALL:
            return self._compile_files_delayed()
        else:
            return self._compile_files_now()

    def make_bootstrap(self):
        """Creates bootstrap machinery for the project."""
        self.msg(LOG_VERBOSE, "\n****** Creating bootstrap script ******")
        if not self.entry_points:
            self.msg(LOG_VERBOSE, 'Skipped, no entry point present.')
            return True
        # all entrypoints should have been copied by now...
        got_errors = False
        for p, n, f in self.entry_points:
            if not (self.build_dir / p).exists():
                self.msg(LOG_DEBUG, '->Debug - non-existent entrypoint:', p)
                got_errors = True
        entrypoints = [[str(p), n, f] for p, n, f in self.entry_points]
        script = BOOTSTRAP_PY_SCRIPT.format(
                                pydirname=self.target_py_dir.name,
                                proj_dirs=str(self.target_proj_dirs_relative),
                                entrypoints=str(entrypoints),
                                pyc_only=self.cfg.PYC_ONLY_DISTRIBUTION,
                                compile_pycs=str(self.delay_compile_pycs), 
                                have_pip=str(self.delay_have_pip),
                                have_deps=str(self.delay_have_dependencies),
                                welcome=repr(self.cfg.WELCOME_MESSAGE),
                                goodbye=repr(self.cfg.GOODBYE_MESSAGE))
        with open(self.bootstrap_dir / 'bootstrap.py', 'a') as f:
            f.write(script)
        txt = f'"./{self.target_py_dir.name}/python.exe"'
        txt += f' "./{self.bootstrap_dir.name}/bootstrap.py"'
        with open(self.build_dir / 'install.bat', 'a') as f:
            f.write('echo off\n')
            f.write(txt)
        if got_errors:
            self.msg(LOG_VERBOSE, 'ERROR: not all entry points actually exist.')
            return False
        self.msg(LOG_VERBOSE, 'Bootstrap entry point successfully created.')
        return True

    def run_custom_action(self):
        """Run your custom post-build function (i.e. config.custom_action)."""
        self.msg(LOG_VERBOSE, "\n****** Running custom action ******")
        ret = self.cfg.custom_action(self)
        if ret:
            self.msg(LOG_VERBOSE, 'Custom action successfully executed.')
        else:
            self.msg(LOG_VERBOSE, 'ERROR: custom action returned "False".')
        return ret

    def run_pip_freeze(self):
        """Run 'pip freeze' against our target build setup."""
        if self.cfg.VERBOSE == 0:
            return True
        self.msg(LOG_VERBOSE, '\n****** Running a final "pip freeze" ******')
        if not self.cfg.PIP_REQUIRED:
            self.msg(LOG_VERBOSE, 'Skipped: no Pip required in config file.')
            return True
        if self.cfg.DELAYED_INSTALL:
            self.msg(LOG_VERBOSE, 'Skipped: no Pip present (delayed install).')
            return True
        if not self.pip_is_present:
            self.msg(LOG_VERBOSE, "ERROR: no Pip present.")
            return False
        pyexec = self.target_py_dir / 'python.exe' 
        self.run_subprocess(str(pyexec), '-m', 'pip', 'freeze')
        return True

    def main(self):
        retcodes = []
        self.prepare_dirs()
        python_file = self.obtain_python()
        retcodes.append(self.unpack_python(python_file))
        getpip_file = self.obtain_getpip()
        retcodes.append(self.install_pip(getpip_file))
        retcodes.append(self.install_dependencies())
        retcodes.append(self.copy_project_files())
        retcodes.append(self.compile_files())
        retcodes.append(self.copy_other_files())
        retcodes.append(self.make_bootstrap())
        retcodes.append(self.run_custom_action())
        retcodes.append(self.run_pip_freeze())
        if not all(retcodes):
            self.msg(LOG_ALWAYS, '\n\nDone - some errors occurred:')
            for op, ret in zip(['  Unpack Python........ ', 
                                '  Install pip.......... ', 
                                '  Install dependencies. ',
                                '  Copy project(s)...... ', 
                                '  Compile.............. ',
                                '  Copy other files..... ', 
                                '  Make bootstrap script ', 
                                '  Custom action........ ', 
                                '  Final pip freeze..... '], retcodes):
                str_ret = 'ok' if ret else 'ERROR'
                self.msg(LOG_ALWAYS, op, str_ret)
        else:
            self.msg(LOG_VERBOSE, '\n\nDone.')
        return retcodes


# this is the auto-generated config script
PACKIT_CONFIG_SCRIPT = """\
# -*- coding: utf-8 -*-

# This is a settings and runner module for the WinPackIt script. 
# To generate this file in your *current* directory, run `python -m winpackit`

# *** SEE WINPACKIT DOCS FOR MORE INFO ***

# Copyright 2019, Riccardo Polignieri
# License: MIT - https://opensource.org/licenses/MIT

# =============================================================================
# GENERAL SETTINGS
# =============================================================================

# To see what's going on (*recommended*)
# Set to `2` (debug messages), `1` (normal output) or `0` (silent)
VERBOSE = 1

# WinPackIt will cache pip-downloaded packages and Python distributable zips. 
# Set to `False` to ignore previously stored items. 
USE_CACHE = True

# The target Python version. 
# An empty or invalid string defaults to your current version *or* to 
# Python 3.5 if you run Python<3.5 (which should not be possible anyway!).
# Set to `'3'` to default to the *latest* Python 3. 
# See WinPackIt docs for details.
PYTHON_VERSION = '3'

# Set to `True` to program a "delayed install" on the target machine. 
# This way, you won't need to run the target Python on your own machine:
# pip-installing packages and compiling pyc files will occur at "install time". 
# You need this if you are on Linux/Mac (or if you run a 32 bit Windows but  
# you want to produce a 64 bit distribution). See WinPackIt docs for details.
DELAYED_INSTALL = False

# =============================================================================
# DEPENDENCIES SETTINGS
# =============================================================================

# If `False` will *not* install Pip: useful if no external package is required.
PIP_REQUIRED = True

# Path to a standard `requirements.txt` file for Pip. 
# The path should be relative to this file, or an absolute path. 
# If you set `PIP_REQUIRED = False` nothing will happen anyway.
REQUIREMENTS = ''

# A list of external packages to be pip-installed: use the familiar pip-install 
# format, e.g. `'arrow'`, `'arrow>=1'`, `'arrow==1.2'` etc.
# If both REQUIREMENTS and DEPENDENCIES are set, then REQUIREMENTS will be 
# processed first. 
DEPENDENCIES = []

# If `True`, use WinPackIt cache to store Pip cache too. 
# If `False`, `--no-cache` will be passed to Pip. 
PIP_CACHE = True

# A list of options to be passed to `pip.exe`
# See `https://pip.pypa.io/en/stable/reference/pip/#general-options`
# Note that `-qqq` will be passed if `VERBOSE = 0`
PIP_ARGS = []

# A list of options to be passed to `pip install`
# See `https://pip.pypa.io/en/stable/reference/pip_install/#options`
# (some may collide with the WinPackIt routine) 
PIP_INSTALL_ARGS = []

# =============================================================================
# FILE COPY SETTINGS
# =============================================================================

# A list of 0 of more "projects", e.g.
# PROJECTS = [
#    ['path/to/project1', ('main.py', 'Main'), ('readme.txt', 'Readme')],
#    ['path/to/project2', ('main.pyw', 'Main')],
#    [ ... ]]
# where project paths should be relative to this file or absolute, 
# and entry point paths *must* be relative to project directory.
# See WinPackIt docs for details.
PROJECTS = []

# A list of `shutil.ignore_patterns` that will be passed to 
# `shutils.copytree` when copying your files. 
# See `https://docs.python.org/3/library/shutil.html#shutil.ignore_patterns`
# Note that `__pycache__` will automatically be included in the list.
# E.g.: PROJECT_FILES_IGNORE_PATTERNS = ['.git', '.vscode', 'tests', ...]
PROJECT_FILES_IGNORE_PATTERNS = []

# If `True`, compile `*.py` files to `*.pyc`
COMPILE = True

# If `True`, also remove original `*.py` files, 
# producing the infamous, obfuscated "pyc-only distribution". 
# This setting will matter only if `COMPILE = True`
PYC_ONLY_DISTRIBUTION = False

# A list of 0 or more non-Python directories to copy (documentation, etc.).
# Use the same format as PROJECTS, e.g.
# COPY_DIRS = [['path/to/docs', ('index.html', 'online help')], [...]]
# See WinPackIt docs for details.
COPY_DIRS = []

# =============================================================================
# =============================================================================

# Welcome message to be shown to the user.
WELCOME_MESSAGE = '\nInstalling project... Please wait...\n\n'

# Final message to be shown to the user.
# This will be printed as "input(GOODBYE_MESSAGE)" to keep the console open.
# You should include "press ENTER to exit" here.
GOODBYE_MESSAGE = 'Done.\nPress ENTER to exit.'

# Insert here your custom code. 
# This function will be called at the very end of the packaging process;
# the only argument passed `packit_instance` is a reference to the working 
# instance of the `Packit` class, to give you access to the internals 
# (for example, `packit_instance.build_dir` points to the path of the 
# build directory, etc.). This function should return `True` or `False`.
def custom_action(packit_instance):
    packit_instance.msg(1, 'Nothing to do here.')
    return True


# =============================================================================
if __name__ == '__main__':
    import os
    from pathlib import Path
    from collections import namedtuple
    from winpackit import Packit
    HERE = Path(__file__).parent.resolve()
    os.chdir(str(HERE))
    cfg = namedtuple('cfg', ['HERE', 'VERBOSE', 'USE_CACHE', 'PYTHON_VERSION', 
                             'DELAYED_INSTALL', 'PIP_REQUIRED', 'REQUIREMENTS', 
                             'DEPENDENCIES', 'PIP_CACHE', 'PIP_ARGS', 
                             'PIP_INSTALL_ARGS', 'PROJECTS', 
                             'PROJECT_FILES_IGNORE_PATTERNS', 'COMPILE', 
                             'PYC_ONLY_DISTRIBUTION', 'COPY_DIRS',
                             'WELCOME_MESSAGE', 'GOODBYE_MESSAGE', 
                             'custom_action'])
    pack_settings = cfg(HERE, VERBOSE, USE_CACHE, PYTHON_VERSION, 
                        DELAYED_INSTALL, PIP_REQUIRED, REQUIREMENTS, 
                        DEPENDENCIES, PIP_CACHE, PIP_ARGS, PIP_INSTALL_ARGS, 
                        PROJECTS, PROJECT_FILES_IGNORE_PATTERNS, COMPILE, 
                        PYC_ONLY_DISTRIBUTION, COPY_DIRS, WELCOME_MESSAGE, 
                        GOODBYE_MESSAGE, custom_action)
    Packit(settings=pack_settings).main()

"""

def make_runner_script(namefile):
    namefile = Path(namefile)
    print(f'This is the WinPackIt script version {version}.')
    print('Generating a new runner module...')
    if namefile.exists():
        print(f'\nA file named {str(namefile)} is already present!')
        print('Delete or rename this file, then try again.')
        return 1
    _ = namefile.write_text(PACKIT_CONFIG_SCRIPT)
    print(f'\nRunner module {str(namefile)} generated.')
    print(f'Please customize and run it ("python {namefile.name}")', 
           'to package your project.')
    return 0

if __name__ == '__main__':
    try:
        modname = Path(sys.argv[1])
    except:
        modname = Path.cwd() / 'run_winpackit.py'
    sys.exit(make_runner_script(modname))
    