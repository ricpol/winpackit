# -*- coding: utf-8 -*-

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

    def test_parse_pyversion_max_version(self):
        # NOTE: these yield *current* most recent versions... 
        # will need to be updated as new versions are released...
        self.cfg.PYTHON_VERSION = '3.5.20'
        self.assertEqual(self.packit.parse_pyversion(), (3, 5, 4, 64))
        self.cfg.PYTHON_VERSION = '3.7'
        self.assertEqual(self.packit.parse_pyversion(), (3, 7, 5, 64))
        self.cfg.PYTHON_VERSION = '3.7-32'
        self.assertEqual(self.packit.parse_pyversion(), (3, 7, 5, 32))
        self.cfg.PYTHON_VERSION = '3.18'
        self.assertEqual(self.packit.parse_pyversion(), (3, 8, 0, 64))
        self.cfg.PYTHON_VERSION = '3'
        self.assertEqual(self.packit.parse_pyversion(), (3, 8, 0, 64))
        self.cfg.PYTHON_VERSION = '3-32'
        self.assertEqual(self.packit.parse_pyversion(), (3, 8, 0, 32))
        self.cfg.PYTHON_VERSION = '4'
        self.assertEqual(self.packit.parse_pyversion(), (3, 8, 0, 64))
        self.cfg.PYTHON_VERSION = 'bogus'
        with mock.patch('sys.version_info', (2, 7, 10)):
            self.assertEqual(self.packit.parse_pyversion(), (3, 5, 4, 64))

    def test_getfile(self):
        with self.assertRaises(Exception):
            self.packit.getfile('bogus', on_error_abort=True)
        testpath = self.packit.cache_dir / 'testfile'
        open(testpath, 'a').close()
        self.cfg.USE_CACHE = True
        self.assertEqual(self.packit.getfile('bogus/dir/testfile'), testpath)


class BaseBuildTestCase(unittest.TestCase):
    def setUp(self):
        self.cfg = _Cfg()
        self.basedir = self.cfg.HERE / 'testoutput'
        self.basedir.mkdir(exist_ok=True)
        
    def tearDown(self):
        del self.cfg

    def start(self, buildir):
        self.packit = Packit(settings=self.cfg)
        self.packit.cache_dir = self.basedir / 'test_cachedir'
        self.packit.build_dir = self.basedir / buildir
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
        self.cfg.PIP_ISTALL_ARGS = ['--no-compile']
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



class BuildTestCase1(BaseBuildTestCase):
    # builds the same project with various Python version
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

    def test_build_py35032(self):
        self.cfg.PYTHON_VERSION = '3.5.0-32'
        buildir = Path('BuildTestCase1_build_py35032')
        ret = self.start(buildir)
        self.assertTrue(all(ret))

    def test_build_py35064(self):
        self.cfg.PYTHON_VERSION = '3.5.0'
        buildir = Path('BuildTestCase1_build_py35064')
        ret = self.start(buildir)
        self.assertTrue(all(ret))

    def test_build_py35464(self):
        self.cfg.PYTHON_VERSION = '3.5.4'
        buildir = Path('BuildTestCase1_build_py35464')
        ret = self.start(buildir)
        self.assertTrue(all(ret))

    def test_build_py36064(self):
        self.cfg.PYTHON_VERSION = '3.6.0'
        buildir = Path('BuildTestCase1_build_py36064')
        ret = self.start(buildir)
        self.assertTrue(all(ret))

    def test_build_py36864(self):
        self.cfg.PYTHON_VERSION = '3.6.8'
        buildir = Path('BuildTestCase1_build_py36864')
        ret = self.start(buildir)
        self.assertTrue(all(ret))

    def test_build_py37064(self):
        self.cfg.PYTHON_VERSION = '3.7.0'
        buildir = Path('BuildTestCase1_build_py37064')
        ret = self.start(buildir)
        self.assertTrue(all(ret))

    def test_build_py37564(self):
        self.cfg.PYTHON_VERSION = '3.7.5'
        buildir = Path('BuildTestCase1_build_py37564')
        ret = self.start(buildir)
        self.assertTrue(all(ret))

    def test_build_py38064(self):
        self.cfg.PYTHON_VERSION = '3.8.0'
        buildir = Path('BuildTestCase1_build_py38064')
        ret = self.start(buildir)
        self.assertTrue(all(ret))


if __name__ == '__main__':
    unittest.main()
