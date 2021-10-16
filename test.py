# -*- coding: utf-8 -*-

# This is the Winpackit test suite. 
# Be aware that running the suite will produce a lot of output. 
# We recommend redirecting both stdout and stderr, eg:
# $ python test.py > output.txt 2>&1

import unittest
from unittest import mock
import os, sys, shutil
from pathlib import Path
from pprint import pprint

from winpackit import *

class _Cfg:
    def __init__(self):
        self.HERE = Path(__file__).resolve().parent
        self.PROJECTS = []
        self.PYTHON_VERSION = '3'
        self.DELAYED_INSTALL = False
        self.PIP_REQUIRED = False
        self.DEPENDENCIES = []
        self.REQUIREMENTS = ''
        self.PIP_CACHE = True
        self.PIP_ARGS = []
        self.PIP_INSTALL_ARGS = []
        self.PROJECT_FILES_IGNORE_PATTERNS = []
        self.COMPILE = False
        self.PYC_ONLY_DISTRIBUTION = False
        self.COPY_DIRS = []
        self.USE_CACHE = True
        self.VERBOSE = 2
        self.WELCOME_MESSAGE = 'starting...'
        self.GOODBYE_MESSAGE = "done, press enter to quit"
        self.custom_action = lambda i: True


class BasicTestCase(unittest.TestCase):
    def setUp(self):
        self.cfg = _Cfg()
        self.basedir = self.cfg.HERE / 'testoutput'
        self.basedir.mkdir(exist_ok=True)
        self.cfg.VERBOSE = 0
        self.cfg.PROJECTS = []
        self.packit = Packit(settings=self.cfg)
        self.packit.cache_dir = self.basedir / 'test_cachedir'
        self.packit.build_dir = self.basedir / 'BasicTestCase_build'
        self.packit.prepare_dirs()

    def tearDown(self):
        shutil.rmtree(self.packit.build_dir)
        shutil.rmtree(self.packit.cache_dir)
        self.packit = None
        del self.cfg

    def test_parse_pyversion(self):
        intro = f'\n#####\n##### RUNNING TEST parse_pyversion ...\n#####\n'
        self.packit.msg(0, intro)
        self.cfg.PYTHON_VERSION = '3.6.6-64'
        self.assertEqual(self.packit.parse_pyversion(), (3, 6, 6, 64))
        self.cfg.PYTHON_VERSION = '3.5.3'
        self.assertEqual(self.packit.parse_pyversion(), (3, 5, 3, 64))
        self.cfg.PYTHON_VERSION = 'bogus'
        with mock.patch('sys.version_info', (3, 6, 2)):
            self.assertEqual(self.packit.parse_pyversion(), (3, 6, 2, 64))
        self.cfg.PYTHON_VERSION = '2.7'
        with mock.patch('sys.version_info', (3, 7, 1)):
            self.assertEqual(self.packit.parse_pyversion(), (3, 7, 1, 64))

    def test_parse_pyversion_special_case(self): # see SPECIAL_CASE_VERSIONS
        intro = f'\n#####\n##### RUNNING TEST parse_pyversion_special_case ...\n#####\n'
        self.packit.msg(0, intro)
        self.cfg.PYTHON_VERSION = '3.9.3-32'
        self.assertEqual(self.packit.parse_pyversion(), (3, 9, 4, 32))
        self.cfg.PYTHON_VERSION = '3.9.3-64'
        self.assertEqual(self.packit.parse_pyversion(), (3, 9, 4, 64))
        self.cfg.PYTHON_VERSION = '3.9.3'
        self.assertEqual(self.packit.parse_pyversion(), (3, 9, 4, 64))

    def test_parse_pyversion_max_version(self):
        # NOTE: these yield *current* most recent versions... 
        # will need to be updated as new versions are released...
        intro = f'\n#####\n##### RUNNING TEST parse_pyversion_max_version ...\n#####\n'
        self.packit.msg(0, intro)
        self.cfg.PYTHON_VERSION = '3.5.20'
        self.assertEqual(self.packit.parse_pyversion(), (3, 5, 4, 64))
        self.cfg.PYTHON_VERSION = '3.7'
        self.assertEqual(self.packit.parse_pyversion(), (3, 7, 9, 64))
        self.cfg.PYTHON_VERSION = '3.7-32'
        self.assertEqual(self.packit.parse_pyversion(), (3, 7, 9, 32))
        self.cfg.PYTHON_VERSION = '3.18'
        self.assertEqual(self.packit.parse_pyversion(), (3, 10, 0, 64))
        self.cfg.PYTHON_VERSION = '3'
        self.assertEqual(self.packit.parse_pyversion(), (3, 10, 0, 64))
        self.cfg.PYTHON_VERSION = '3-32'
        self.assertEqual(self.packit.parse_pyversion(), (3, 10, 0, 32))
        self.cfg.PYTHON_VERSION = '4'
        self.assertEqual(self.packit.parse_pyversion(), (3, 10, 0, 64))
        self.cfg.PYTHON_VERSION = 'bogus'
        with mock.patch('sys.version_info', (2, 7, 10)):
            self.assertEqual(self.packit.parse_pyversion(), (3, 5, 4, 64))

    def test_getfile(self):
        intro = f'\n#####\n##### RUNNING TEST getfile ...\n#####\n'
        self.packit.msg(0, intro)
        with self.assertRaises(Exception):
            self.packit.getfile('bogus', on_error_abort=True)
        testpath = self.packit.cache_dir / 'testfile'
        open(testpath, 'a').close()
        self.cfg.USE_CACHE = True
        self.assertEqual(self.packit.getfile('bogus/dir/testfile'), testpath)

    @unittest.skip('this will download and check *all* the pythons...')
    def test_get_pythons(self):
        intro = f'\n#####\n##### RUNNING TEST get_pythons ...\n#####\n'
        self.packit.msg(0, intro)
        for url, checksum in PY_URL.values():
            self.assertTrue(self.packit.getfile(url, checksum))


class BaseBuildTestCase(unittest.TestCase):
    def setUp(self):
        self.cfg = _Cfg()
        self.basedir = self.cfg.HERE / 'testoutput'
        self.basedir.mkdir(exist_ok=True)
        
    def tearDown(self):
        del self.cfg

    def start(self, buildir):
        self.packit = Packit(settings=self.cfg)
        intro = f'\n#####\n##### RUNNING TEST {buildir.stem} ...\n#####\n'
        self.packit.msg(1, intro)
        self.packit.cache_dir = self.basedir / 'test_cachedir'
        self.packit.build_dir = self.basedir / buildir
        # skip md5 check to save time
        with mock.patch('winpackit._md5compare', lambda i, j: True):
            ret = self.packit.main()
        with open((self.packit.build_dir / '_testconfig.txt'), 'a') as f:
            f.write('This test build was made from this configuration:\n\n')
            pprint(self.cfg.__dict__, stream=f)
        return ret


class BuildTestCase(BaseBuildTestCase):
    # builds various example projects

    def test_build_no_project(self):
        buildir = Path('BuildTestCase_build_no_project')
        ret = self.start(buildir) 
        self.assertTrue(all(ret))

    def test_build0(self):
        self.cfg.PROJECTS = [['examples/project0', ('main.py', 'main'), 
                                                   ('readme.txt', 'readme')]]
        buildir = Path('BuildTestCase_build0')
        ret = self.start(buildir)
        self.assertTrue(all(ret))

    def test_build1(self):
        self.cfg.PROJECTS = [['examples/project1', ('main.py', 'main'), 
                                                   ('readme.txt', 'readme')]]
        self.cfg.COMPILE = True
        self.cfg.PYC_ONLY_DISTRIBUTION = True
        buildir = Path('BuildTestCase_build1')
        ret = self.start(buildir) 
        self.assertTrue(all(ret))

    def test_build2(self):
        self.cfg.PROJECTS = [
                ['examples/project1', ('main.py', 'main_project1'), 
                                      ('readme.txt', 'readme_project1')],
                ['examples/project2', ('code/main.py', 'main_project2'), 
                                      ('code/side.py', 'codeside'),
                                      ('code/foo/side.py', 'fooside'), 
                                      ('docs/readme.txt', 'readme_project2')]]
        buildir = Path('BuildTestCase_build2')
        ret = self.start(buildir) 
        self.assertTrue(all(ret))

    def test_build3(self):
        self.cfg.PROJECTS = [['examples/project3/code with spaces', 
                              ('main.py', 'main')]]
        self.cfg.COPY_DIRS = [['examples/project3/docs with spaces', 
                               ('readme.txt', 'readme')]]
        buildir = Path('BuildTestCase_build3')
        ret = self.start(buildir)
        self.assertTrue(all(ret))

    @unittest.skip('This one is going to pip-install *many* packages')
    def test_build4(self):
        self.cfg.PROJECTS = [['examples/project4', ('main.py', 'main'), 
                                                   ('readme.txt', 'readme')]]
        self.cfg.PIP_REQUIRED = True
        self.cfg.PIP_ARGS = ['--no-color']
        self.cfg.PIP_INSTALL_ARGS = ['--no-compile']
        self.cfg.DEPENDENCIES = ['wxpython', 'numpy']
        self.cfg.REQUIREMENTS = 'examples/project4/requirements.txt'
        buildir = Path('BuildTestCase_build4')
        ret = self.start(buildir)
        self.assertTrue(all(ret))

    def test_build5(self):
        self.cfg.PROJECTS = [['examples/project5/one', ('main.py', 'Main')], 
                             ['examples/project5/two']]
        buildir = Path('BuildTestCase_build5')
        ret = self.start(buildir)
        self.assertTrue(all(ret))

    def test_build6(self):
        self.cfg.COMPILE = True
        self.cfg.PYC_ONLY_DISTRIBUTION = True
        self.cfg.PROJECTS = [['examples/project6', ('main.pyw', 'Main'),
                                                   ('readme.txt', 'readme')]]
        buildir = Path('BuildTestCase_build6')
        ret = self.start(buildir)
        self.assertTrue(all(ret))

    def test_build_ignore_patterns(self):
        self.cfg.PROJECTS = [
                ['examples/project1', ('main.py', 'main_project1'), 
                                      ('readme.txt', 'readme_project1')]]
        self.cfg.PROJECT_FILES_IGNORE_PATTERNS = ['a.gif', 'foo']
        buildir = Path('BuildTestCase_build_ignore_patterns')
        ret = self.start(buildir) 
        self.assertTrue(all(ret))


class FailBuildTestCase(BaseBuildTestCase):
    # test various failures

    def test_fail1(self): # this obtains a bogus get_pip.py
        self.cfg.PIP_REQUIRED = True
        buildir = Path('BuildTestCase_fail1')
        with mock.patch('winpackit.Packit.obtain_getpip', lambda i: 'bogus'):
            ret = self.start(buildir)
            self.assertEqual(ret, [True, False, True, True, True, True, True, True, False])

    def test_fail2(self): # this installs a bogus dependency
        self.cfg.PIP_REQUIRED = True
        self.cfg.DEPENDENCIES = ['total_bogus_packet_wont_install']
        buildir = Path('BuildTestCase_fail2')
        ret = self.start(buildir)
        self.assertEqual(ret, [True, True, False, True, True, True, True, True, True])

    def test_fail3(self): # this packs a non-existent project
        self.cfg.PROJECTS = [['examples/project0', ('main.py', 'main'), 
                                                   ('readme.txt', 'readme')],
                             ['examples/BOGUS']]
        buildir = Path('BuildTestCase_fail3')
        ret = self.start(buildir)
        self.assertEqual(ret, [True, True, True, False, True, True, True, True, True])

    def test_fail4(self): # this will hit a compile error
        self.cfg.PROJECTS = [['examples/project7', ('main.py', 'main')]]
        self.cfg.COMPILE = True
        buildir = Path('BuildTestCase_fail4')
        ret = self.start(buildir)
        self.assertEqual(ret, [True, True, True, True, False, True, True, True, True])

    def test_fail5(self): # this packs a non-existent "other" dir
        self.cfg.PROJECTS = [['examples/project0', ('main.py', 'main'), 
                                                   ('readme.txt', 'readme')]]
        self.cfg.COPY_DIRS = [['examples/BOGUS']]
        buildir = Path('BuildTestCase_fail5')
        ret = self.start(buildir)
        self.assertEqual(ret, [True, True, True, True, True, False, True, True, True])

    def test_fail6(self): # this has a bogus entrypoint
        self.cfg.PROJECTS = [['examples/project0', ('main.py', 'main'), 
                                                   ('BOGUS', 'readme')]]
        buildir = Path('BuildTestCase_fail6')
        ret = self.start(buildir)
        self.assertEqual(ret, [True, True, True, True, True, True, False, True, True])


class BuildTestCaseAllPythons(BaseBuildTestCase):
    # builds the same project with the latest version of all Pythons
    def setUp(self):
        self.cfg = _Cfg()
        self.basedir = self.cfg.HERE / 'testoutput'
        self.basedir.mkdir(exist_ok=True)
        self.cfg.PIP_REQUIRED = True
        self.cfg.PROJECTS = [['examples/project5/one', ('main.py', 'Main')], 
                             ['examples/project5/two'],
                             ['examples/project1', ('main.py', 'main_project1'), 
                                                   ('readme.txt', 'readme_project1')]]
        self.cfg.COPY_DIRS = [['examples/project3/docs with spaces', 
                               ('readme.txt', 'docs_readme')]]
        self.cfg.DEPENDENCIES = ['arrow']
        self.cfg.COMPILE = True
        self.cfg.PYC_ONLY_DISTRIBUTION = True

    def test_build_py35_32(self):
        self.cfg.PYTHON_VERSION = '3.5-32'
        buildir = Path('BuildTestCase1_build_py35_32')
        ret = self.start(buildir)
        self.assertTrue(all(ret))

    def test_build_py35_64(self):
        self.cfg.PYTHON_VERSION = '3.5'
        buildir = Path('BuildTestCase1_build_py35_64')
        ret = self.start(buildir)
        self.assertTrue(all(ret))

    def test_build_py36_32(self):
        self.cfg.PYTHON_VERSION = '3.6-32'
        buildir = Path('BuildTestCase1_build_py36_32')
        ret = self.start(buildir)
        self.assertTrue(all(ret))

    def test_build_py36_64(self):
        self.cfg.PYTHON_VERSION = '3.6'
        buildir = Path('BuildTestCase1_build_py36_64')
        ret = self.start(buildir)
        self.assertTrue(all(ret))

    def test_build_py37_32(self):
        self.cfg.PYTHON_VERSION = '3.7-32'
        buildir = Path('BuildTestCase1_build_py37_32')
        ret = self.start(buildir)
        self.assertTrue(all(ret))

    def test_build_py37_64(self):
        self.cfg.PYTHON_VERSION = '3.7'
        buildir = Path('BuildTestCase1_build_py37_64')
        ret = self.start(buildir)
        self.assertTrue(all(ret))

    def test_build_py38_32(self):
        self.cfg.PYTHON_VERSION = '3.8-32'
        buildir = Path('BuildTestCase1_build_py38_32')
        ret = self.start(buildir)
        self.assertTrue(all(ret))

    def test_build_py38_64(self):
        self.cfg.PYTHON_VERSION = '3.8'
        buildir = Path('BuildTestCase1_build_py38_64')
        ret = self.start(buildir)
        self.assertTrue(all(ret))

    def test_build_py39_32(self):
        self.cfg.PYTHON_VERSION = '3.9-32'
        buildir = Path('BuildTestCase1_build_py39_32')
        ret = self.start(buildir)
        self.assertTrue(all(ret))

    def test_build_py39_64(self):
        self.cfg.PYTHON_VERSION = '3.9'
        buildir = Path('BuildTestCase1_build_py39_64')
        ret = self.start(buildir)
        self.assertTrue(all(ret))

    def test_build_py310_32(self):
        self.cfg.PYTHON_VERSION = '3.10-32'
        buildir = Path('BuildTestCase1_build_py310_32')
        ret = self.start(buildir)
        self.assertTrue(all(ret))

    def test_build_py310_64(self):
        self.cfg.PYTHON_VERSION = '3.10'
        buildir = Path('BuildTestCase1_build_py310_64')
        ret = self.start(buildir)
        self.assertTrue(all(ret))

class DelayedBuildTestCase(BaseBuildTestCase):
    # a few "delayed build" tests
    def setUp(self):
        super().setUp()
        self.cfg.DELAYED_INSTALL = True

    def test_delay1(self): # this installs a delayed Pip
        self.cfg.PIP_REQUIRED = True
        self.cfg.PROJECTS = [['examples/project0', ('main.py', 'main'), 
                                                   ('readme.txt', 'readme')]]
        buildir = Path('DelayedBuildTestCase_build1')
        ret = self.start(buildir)
        self.assertTrue(all(ret))

    def test_delay2(self): # this installs delayed dependencies from a req file
        self.cfg.PIP_REQUIRED = True
        self.cfg.PROJECTS = [['examples/project4', ('main.py', 'main'), 
                                                   ('readme.txt', 'readme')]]
        self.cfg.REQUIREMENTS = 'examples/project4/requirements_small.txt'
        buildir = Path('DelayedBuildTestCase_build2')
        ret = self.start(buildir)
        self.assertTrue(all(ret))

    def test_delay3(self): # this installs delayed dependencies from a list
        self.cfg.PIP_REQUIRED = True
        self.cfg.PROJECTS = [['examples/project4', ('main.py', 'main'), 
                                                   ('readme.txt', 'readme')]]
        self.cfg.DEPENDENCIES = ['arrow']
        buildir = Path('DelayedBuildTestCase_build3')
        ret = self.start(buildir)
        self.assertTrue(all(ret))

    def test_delay4(self): # this installs delayed dependencies from both
        self.cfg.PIP_REQUIRED = True
        self.cfg.PROJECTS = [['examples/project4', ('main.py', 'main'), 
                                                   ('readme.txt', 'readme')]]
        self.cfg.DEPENDENCIES = ['arrow']
        self.cfg.REQUIREMENTS = 'examples/project4/requirements_small.txt'
        buildir = Path('DelayedBuildTestCase_build4')
        ret = self.start(buildir)
        self.assertTrue(all(ret))

    def test_delay5(self): # this installs with delayed compile pycs
        self.cfg.COMPILE = True
        self.cfg.PROJECTS = [['examples/project5/one', ('main.py', 'main_project5')], 
                             ['examples/project5/two'],
                             ['examples/project6', ('main.pyw', 'main_project6'), 
                                                   ('readme.txt', 'readme_project6')]]
        buildir = Path('DelayedBuildTestCase_build5')
        ret = self.start(buildir)
        self.assertTrue(all(ret))

    def test_delay6(self): # this installs a delayed pyc-only distribution
        self.cfg.COMPILE = True
        self.cfg.PYC_ONLY_DISTRIBUTION = True
        self.cfg.PROJECTS = [['examples/project5/one', ('main.py', 'main_project5')], 
                             ['examples/project5/two'],
                             ['examples/project6', ('main.pyw', 'main_project6'), 
                                                   ('readme.txt', 'readme_project6')],
                             ['examples/project3/code with spaces', 
                              ('main.py', 'main_project3')]]
        buildir = Path('DelayedBuildTestCase_build6')
        ret = self.start(buildir)
        self.assertTrue(all(ret))

if __name__ == '__main__':
    unittest.main()
