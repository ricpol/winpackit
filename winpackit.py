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
           'MIN_TARGET_VERSION', 'Packit', 'make_runner_script']

import sys
import os
import shutil
import zipfile
import time
import subprocess

from pathlib import Path
from urllib.request import urlretrieve

# Python version book-keeping
MAX_MICRO_VERSIONS = {(3, 5): 4, (3, 6): 8, (3, 7): 5, (3, 8): 0}
MAX_MINOR_VERSIONS = {3: 8}
MAX_MAJOR_VERSION = 3          # this won't change for... a while
MIN_TARGET_VERSION = (3, 5, 0) # this won't change, ever

# download urls for embeddable Pythons
PY_URL = {
    (3,8,0,64): 'https://www.python.org/ftp/python/3.8.0/python-3.8.0-embed-amd64.zip', 
    (3,8,0,32): 'https://www.python.org/ftp/python/3.8.0/python-3.8.0-embed-win32.zip', 

    (3,7,5,64): 'https://www.python.org/ftp/python/3.7.5/python-3.7.5-embed-amd64.zip', 
    (3,7,5,32): 'https://www.python.org/ftp/python/3.7.5/python-3.7.5-embed-win32.zip', 
    (3,7,4,64): 'https://www.python.org/ftp/python/3.7.4/python-3.7.4-embed-amd64.zip', 
    (3,7,4,32): 'https://www.python.org/ftp/python/3.7.4/python-3.7.4-embed-win32.zip', 
    (3,7,3,64): 'https://www.python.org/ftp/python/3.7.3/python-3.7.3-embed-amd64.zip', 
    (3,7,3,32): 'https://www.python.org/ftp/python/3.7.3/python-3.7.3-embed-win32.zip', 
    (3,7,2,64): 'https://www.python.org/ftp/python/3.7.2/python-3.7.2.post1-embed-amd64.zip', 
    (3,7,2,32): 'https://www.python.org/ftp/python/3.7.2/python-3.7.2.post1-embed-win32.zip', 
    (3,7,1,64): 'https://www.python.org/ftp/python/3.7.1/python-3.7.1-embed-amd64.zip', 
    (3,7,1,32): 'https://www.python.org/ftp/python/3.7.1/python-3.7.1-embed-win32.zip', 
    (3,7,0,64): 'https://www.python.org/ftp/python/3.7.0/python-3.7.0-embed-amd64.zip', 
    (3,7,0,32): 'https://www.python.org/ftp/python/3.7.0/python-3.7.0-embed-win32.zip', 

    (3,6,8,64): 'https://www.python.org/ftp/python/3.6.8/python-3.6.8-embed-amd64.zip', 
    (3,6,8,32): 'https://www.python.org/ftp/python/3.6.8/python-3.6.8-embed-win32.zip', 
    (3,6,7,64): 'https://www.python.org/ftp/python/3.6.7/python-3.6.7-embed-amd64.zip', 
    (3,6,7,32): 'https://www.python.org/ftp/python/3.6.7/python-3.6.7-embed-win32.zip', 
    (3,6,6,64): 'https://www.python.org/ftp/python/3.6.6/python-3.6.6-embed-amd64.zip', 
    (3,6,6,32): 'https://www.python.org/ftp/python/3.6.6/python-3.6.6-embed-win32.zip', 
    (3,6,5,64): 'https://www.python.org/ftp/python/3.6.5/python-3.6.5-embed-amd64.zip', 
    (3,6,5,32): 'https://www.python.org/ftp/python/3.6.5/python-3.6.5-embed-win32.zip', 
    (3,6,4,64): 'https://www.python.org/ftp/python/3.6.4/python-3.6.4-embed-amd64.zip', 
    (3,6,4,32): 'https://www.python.org/ftp/python/3.6.4/python-3.6.4-embed-win32.zip', 
    (3,6,3,64): 'https://www.python.org/ftp/python/3.6.3/python-3.6.3-embed-amd64.zip', 
    (3,6,3,32): 'https://www.python.org/ftp/python/3.6.3/python-3.6.3-embed-win32.zip', 
    (3,6,2,64): 'https://www.python.org/ftp/python/3.6.2/python-3.6.2-embed-amd64.zip', 
    (3,6,2,32): 'https://www.python.org/ftp/python/3.6.2/python-3.6.2-embed-win32.zip', 
    (3,6,1,64): 'https://www.python.org/ftp/python/3.6.1/python-3.6.1-embed-amd64.zip', 
    (3,6,1,32): 'https://www.python.org/ftp/python/3.6.1/python-3.6.1-embed-win32.zip', 
    (3,6,0,64): 'https://www.python.org/ftp/python/3.6.0/python-3.6.0-embed-amd64.zip', 
    (3,6,0,32): 'https://www.python.org/ftp/python/3.6.0/python-3.6.0-embed-win32.zip', 

    (3,5,4,64): 'https://www.python.org/ftp/python/3.5.4/python-3.5.4-embed-amd64.zip', 
    (3,5,4,32): 'https://www.python.org/ftp/python/3.5.4/python-3.5.4-embed-win32.zip', 
    (3,5,3,64): 'https://www.python.org/ftp/python/3.5.3/python-3.5.3-embed-amd64.zip', 
    (3,5,3,32): 'https://www.python.org/ftp/python/3.5.3/python-3.5.3-embed-win32.zip', 
    (3,5,2,64): 'https://www.python.org/ftp/python/3.5.2/python-3.5.2-embed-amd64.zip', 
    (3,5,2,32): 'https://www.python.org/ftp/python/3.5.2/python-3.5.2-embed-win32.zip', 
    (3,5,1,64): 'https://www.python.org/ftp/python/3.5.1/python-3.5.1-embed-amd64.zip', 
    (3,5,1,32): 'https://www.python.org/ftp/python/3.5.1/python-3.5.1-embed-win32.zip', 
    (3,5,0,64): 'https://www.python.org/ftp/python/3.5.0/python-3.5.0-embed-amd64.zip', 
    (3,5,0,32): 'https://www.python.org/ftp/python/3.5.0/python-3.5.0-embed-win32.zip', 
    # and that's it - no embeddable zip file before 3.5!
    }

# download url for Get-pip
GETPIP_URL = 'https://bootstrap.pypa.io/get-pip.py'

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
ENTRY_POINTS = {entrypoints}
BUILD_DIR = HERE.parent.resolve()
PYC_ONLY = {pyc_only}

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
    make_shortcut()
    post_deploy_action()
    print('\\n\\n')
    input('Done.\\nPress <enter> to quit.')

"""

# output levels
LOG_ALWAYS = 0
LOG_VERBOSE = 1
LOG_DEBUG = 2

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
        self.target_py_version = None # Python version
        self.target_py_dir = None # Python root directory
        self.pip_is_present = False # if Pip is currently installed
        self.target_proj_dirs = None # project dir(s)
        self.target_copy_dirs = None # other non-project dir(s)
        self.entry_points = None # entry points (to both "projects" and "copy")
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

    def getfile(self, fileurl, on_error_abort=False):
        """Download fileurl into self.cache_dir. 
        Return downloaded filepath, or empty string on failed download. 
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
        self.target_copy_dirs = []
        self.entry_points = []
        if self.cfg.PROJECTS:
            for project in self.cfg.PROJECTS:
                proj_dir = self.cfg.HERE / Path(project[0])
                target_projdir = self.build_dir / proj_dir.name
                self.proj_dirs.append(proj_dir)
                self.target_proj_dirs.append(target_projdir)
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
        pyfile = PY_URL[self.parse_pyversion()]
        f = self.getfile(pyfile, on_error_abort=True)
        self.msg(LOG_VERBOSE, 'Python successfully obtained.')
        return f

    def obtain_getpip(self):
        """Download Get-pip, return filepath. If fails, return empty string."""
        self.msg(LOG_VERBOSE, "\n****** Obtaining Get-pip ******")
        f = self.getfile(GETPIP_URL, on_error_abort=False)
        if f:
            self.msg(LOG_VERBOSE, 'Get-pip successfully obtained.')
        else:
            self.msg(LOG_VERBOSE, 'ERROR: Get-pip not obtained.')
        return f

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

    def install_pip(self, getpipfile):
        """Use Get-pip to install Pip. Return False if something went wrong.
        Also, set self.pip_is_present if Pip was successfully installed."""
        self.msg(LOG_VERBOSE, "\n****** Installing Pip ******")
        if not self.cfg.PIP_REQUIRED:
            self.msg(LOG_VERBOSE, 'Skipped: no Pip required in config file.')
            return True
        if not getpipfile:
            self.msg(LOG_VERBOSE, 'ERROR: no Get-pip present.')
            return False
        pyexec = self.target_py_dir / 'python.exe'
        args = str(pyexec), str(getpipfile), *self.cfg.PIP_ARGS
        if self.run_subprocess(*args):
            self.msg(LOG_VERBOSE, 'Pip successfully installed', 
                     '(ignore the "add to PATH" warnings above).')
            self.pip_is_present = True
            return True
        return False
        
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
    
    def _copy_files(self, orig, dest, ignore=None):
        """Run shutil.copytree, return False if errors occurred."""
        try:
            shutil.copytree(orig, dest, ignore)
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

    def compile_files(self):
        """Compile all py modules, remove originals if needed."""
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
                if entrypoint[2] != '':
                    # book-keeping...
                    self.entry_points[n][0] = self.entry_points[n][0].with_suffix('.pyc')
            self.msg(LOG_DEBUG, '->Debug - renamed pyc entry_points:',
                     self.entry_points)
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
        return True

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
                got_errors = True
        entrypoints = [[str(p), n, f] for p, n, f in self.entry_points]
        script = BOOTSTRAP_PY_SCRIPT.format(
                                        pydirname=self.target_py_dir.name,
                                        entrypoints=str(entrypoints),
                                        pyc_only=self.cfg.PYC_ONLY_DISTRIBUTION)
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
                             'PIP_REQUIRED', 'REQUIREMENTS', 'DEPENDENCIES', 
                             'PIP_CACHE', 'PIP_ARGS', 'PIP_INSTALL_ARGS',
                             'PROJECTS', 'PROJECT_FILES_IGNORE_PATTERNS',
                             'COMPILE', 'PYC_ONLY_DISTRIBUTION', 'COPY_DIRS',
                             'custom_action'])
    pack_settings = cfg(HERE, VERBOSE, USE_CACHE, PYTHON_VERSION, PIP_REQUIRED, 
                        REQUIREMENTS, DEPENDENCIES, PIP_CACHE, PIP_ARGS, 
                        PIP_INSTALL_ARGS, PROJECTS, PROJECT_FILES_IGNORE_PATTERNS,
                        COMPILE, PYC_ONLY_DISTRIBUTION, COPY_DIRS, custom_action)
    Packit(settings=pack_settings).main()

"""

def make_runner_script(namefile):
    namefile = Path(namefile)
    print('Generating a new runner module for the WinPackIt script...')
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
    