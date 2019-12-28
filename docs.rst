WinPackIt - the quick and dirty Python packager for Windows.
============================================================

WinPackIt is the ``winpackit.py`` module, a Python script with no external dependency required. 
It will package your Python project into a stand-alone Windows distribution. 

How does it work.
-----------------

Python 3.5 introduced the `embeddable package`_ distribution on Windows: that is, an "almost complete" Python zipped in a single, non-installer file. While intended mainly for embedding purposes, the opposite is also possible: with some tinkering, one can make this package into a full-fledged self-contained Python environment ready to support a Python application. 

Basically, that is what this script is for. 

When you run WinPackIt, 
    - it will download and unpack a Python embeddable package,
    - download and install Pip into it,
    - download and install any needed external dependency,
    - copy your project files,
    - optionally compile your file to ``.pyc``,
    - leave a friendly ``install.bat`` file for the final user to run.

At this point, you may distribute the resulting "build" folder to the final users; all they have to do... 
    - drop the folder anywhere on their Windows box,
    - open it and double-clic on the ``install.bat`` file;
    - this in turn will produce Windows shortcut(s) to the entry-point(s) of your app to double-click, tailored for their machine. 

What WinPackIt is *not*.
------------------------

The WinPackIt script will *not* "compile" your project into some sort of ``.exe`` file. It will just create a folder with Python and your application files in it - it's more like a portable Python environment than a single executable. 

Also, WinPackIt will not look anywhere else on the target machine, outside its "build" folder: it won't write in the Registry, won't set environment variables and so on. You can, of course, add your custom scripted actions to be executed at "install time" (i.e. when user runs the ``install.bat`` file on her own machine). 

Also, keep in mind that WinPackIt will install anything you can ``pip install`` on Windows - but nothing else. Hopefully, this means 99% packages these days. 

Important disclaimer.
^^^^^^^^^^^^^^^^^^^^^

WinPackIt is just a thin wrapper over basic system manipulations (file copy, subprocess run of Pip, etc.). It will do very little magic on itself, and will not try to guess your intentions. It will still require from you to carefully pick setting values and to know what's going on: if the file you pointed to is not there, if the package is not installable etc., WinPackIt won't try to solve the problem for you, and most of the time will happily crash. Always double-check the output log to be sure everything has gone as intended. Running WinPackIt with debug output (``VERBOSE=2``) is often a good idea.

Requirements.
-------------

You will need Python 3.6+ to run WinPackIt on your system. No external dependency is required. 

On the target side, you can produce builds based on any Python 3.5+. You don't have to match your own Python with the target Python: WinPackIt will run the *target* ``pip install``, not yours: so, Pip will take care of choosing the correct packages. Of course you still have to check that your program works as expected on the "build" environment. 

The system architecture can be tricky: you may choose between 32 bit and 64 bit versions of the target Python. However, if you are running a 32 bit Windows and you choose a 64 bit target Python, then WinPackIt won't be able to run the target Python on your machine, to install dependencies and compile ``.pyc`` files. Even so, it may still work, if you need no external package and you can live without compiling pycs. 

Symmetrically, if you choose a 64 bit target Python, keep in mind that of course your application will not run on users' 32 bit Windows machines. 

Linux/Mac users.
^^^^^^^^^^^^^^^^

The WinPackIt script runs on Linux too, of course. Except, the build process needs to run the target Python a few times in order to install external packages and compile ``.pyc`` files - and *that* will be impossible on Linux. Then again, if you need no external packages nor compiling, it should work as a charm. 

At some point, I plan to add code to support running the target Python on the *target* machine only. This should make some sort of cross-building possible, both across Windows/Linux and across 32/64 bit architectures. 

Even so, you might be able to produce a Windows distribution on your Linux box, but you will have no way to run and test it. 

A note on Tkinter.
^^^^^^^^^^^^^^^^^^

Speaking of requirements, be aware that the Python embeddable packages do *not* include Tkinter (even more, Idle). As Tkinter is *not* on PyPI, you can't just ``pip install`` it into your WinPackIt distribution. Maybe in the future I will add a workaround... But for now, if your application is based on Tkinter, you're out of luck. Sorry!

(Opinionated aside: it's worth repeating, 2020 and Tkinter is not on PyPI. Do I need to say more? Maybe it's time you do yourself a favor and start using a real Gui framework instead.)

A note on Python 2.7.
^^^^^^^^^^^^^^^^^^^^^

Stop using Python 2.7, right now.

Seriously, though: WinPackIt won't run on Python<3.6. You are welcome to fork it and make it compatible with previous versions. Even so, you won't be able to produce build distribution targeting Python<3.5.0, because there are no Python embeddable packages available to start with. 

So, no - you can't use WinPackIt to package your Python 2.7 program. 

Usage.
------

In short: 
    - ``pip install winpackit`` in your virtual environment, or even ``pipx install winpackit`` if your really like WinPackIt and would love to have it always at hand;
    - run ``python -m winpackit my_runner.py``;
    - this will produce a ``my_runner.py`` runner file for WinPackIt: open it and customize to your liking;
    - run ``python my_runner.py``;
    - this will produce a "build" folder of your project, as specified in the runner file settings, ready to be distributed to the final user.

Now, a bit more in depth. 

Installing.
-----------

WinPackIt is a stand-alone script with no dependency required. You may install with Pip (``pip install winpackit``, either in your system Python or into a virtual environment). Or, you may install with Pipx (``pipx install winpackit``) if you want to be able to run it from all your environments.

Or, you can just download the script and drop it anywhere you like, really. Just remember that the ``winpackit.py`` module will be *imported* by the runner script you're about to generate: be sure to leave it where the runner can find it (typically, in the same directory). 

Making a runner script.
-----------------------

Run ``python -m winpackit <my_runner.py>``, where ``<my_runner.py>`` will be the namepath (relative or absolute) of the runner script. If you omit the command line argument, WinPackIt will produce a file named ``run_winpackit.py`` in your current directory. 

The runner script is a template for you to customize. It is intended as specific to your current project: you should put the runner script in your project's root directory. You may have more than one script for a given project, in order to produce different builds (for instance, targeted at different Python versions).

If you are importing ``winpackit.py`` (e.g. because you are writing your own custom packager), then you may call ``winpackit.make_runner_script(namefile)`` to produce a ``namefile`` runner script. 

Customizing the runner script.
------------------------------

Here is where the real action happens. Open the runner script with your editor and fill in the various settings, according to the specific environment of your project. The script comes with a few comments to guide you. Let's take a look at the settings one by one. 

``VERBOSE``
^^^^^^^^^^^

Leave it to ``1`` for default output, or ``2`` if you need something more. Setting to ``0`` (silent) is not recommended.

``USE_CACHE``
^^^^^^^^^^^^^

WinPackIt will cache downloaded items into a ``winpackit_cache`` folder. Setting this to ``True`` will check for previously downloaded items first, saving bandwidth.

``PYTHON_VERSION``
^^^^^^^^^^^^^^^^^^

This will be the *target* Python version (i.e., that of your distribution). Leave it to ``3`` to get the latest Python available, or set it to a minor version (e.g., ``3.7``) to point to the most recent micro version of that line, or just pin it to a specific version (``3.7.4``). You may add a ``-32`` or ``-64`` qualifier to specify the system architecture (as in ``3.7.4-32``). Default will be 64 bit. 

An invalid (or blank) value will default to your current Python version. If your Python doesn't match any available embeddable distribution, ``PYTHON_VERSION`` will default to ``3.5``. Remember that no embeddable Python distribution is available prior to ``3.5.0`` version. 

**Note**: also, there is no embeddable distribution available for security fix-only versions ``3.5.5+`` and ``3.6.9+``. 

``PIP_REQUIRED``
^^^^^^^^^^^^^^^^

Set to ``False`` to *not* have Pip installed on your distribution. Useful if your project has no external dependency. 

``REQUIREMENTS``
^^^^^^^^^^^^^^^^

Path (absolute or relative to this file) to a valid standard ``requirements.txt`` requirement list for Pip. This file will be passed to Pip for processing as it is: WinPackIt won't do any check on it. If you have "pinned" your packages, make sure they will match your ``PYTHON_VERSION`` set above. 

``DEPENDENCIES``
^^^^^^^^^^^^^^^^

Set this to a list (of strings) of required external packages to install with Pip. Each string will be passed to ``pip install`` as it is: you may add any version qualifier supported by Pip. 

You can set ``DEPENDENCIES`` and/or ``REQUIREMENTS`` as you see fit. If you set both, then ``REQUIREMENTS`` will be processed first.

``PIP_CACHE``
^^^^^^^^^^^^^

If set, WinPackIt will use its own cache folder (that is, if ``USE_CACHE`` is set too) to store Pip cache too. If not, ``--no-cache`` option will be passed to Pip executable. 

``PIP_ARGS``
^^^^^^^^^^^^

A list of general options to be passed to Pip. See the Pip documentation for the available choices. Note that if ``VERBOSE=0``, the option ``-qqq`` will be passed by default. Also, ``--no-cache`` will be passed if you set ``PIP_CACHE=False``.

``PIP_ISTALL_ARGS``
^^^^^^^^^^^^^^^^^^^

A list of specific options to be passed to ``pip install``. See the Pip documentation for the available choices. 

Be aware that some ``PIP_ARGS`` and ``PIP_INSTALL_ARGS`` may conflict with the WinPackIt workflow. Both those settings are provided as convenience hooks for experienced users only. Your best bet should be to leave them unset. If you use them, always double-check the output.

``PROJECTS``
^^^^^^^^^^^^

A list of lists, containing your Python project folder(s) and entry point(s) data. A "project" is just a folder: WinPackIt will copy it inside its output distribution folder. An "entry point" is a file for the user to double-clic: WinPackIt will make a Windows shortcut to it. 

Usually you will have a single project with a single entry point, e.g.::

    PROJECTS = [
                ['path/to/my_project', ('main.py', 'Run My Program')],
               ]

The first item is the path of your project folder, either absolute or relative to the WinPackIt runner script. The project folder will be copied at the top level of the "build" directory: ``winpackit_build_<timestamp>/my_project``. The project folder may contain whatever you want: of course, it should be mostly Python modules and packages. If you don't want some file/subfolders to be copied, use the ``PROJECT_FILES_IGNORE_PATTERNS`` setting below.

The second item of the project list is a tuple, holding exactly two strings. The first one is the path to an entry point file: it *must* be relative to the project folder. The second one is a user-friendly name that WinPackIt will use for the Windows shortcut file (here, ``Run My Program.lnk``). 

This is perhaps the most basic setup. Now let's see a more complex example::

    PROJECTS = [
        ['path/to/my_project', ('main.pyw', 'My GUI Program'), 
                               ('utils/cleanup.py', 'Maintenance Routine'), 
                               ('docs/docs.pdf', 'Documentation')],
        ['to/other_project', ('main.py', 'My Other Program!'),
                             ('readme.txt', 'Readme')],
        ['to/various_utils'],
               ]

This setting demonstrates a few more options. First, you may package as many "projects" as you want inside a single WinPackIt distribution. This can be a way to pack together several independent programs. However, keep in mind that WinPackIt will add each project folder to the Python ``sys.path``: we will discuss this topic more in detail below.

You can have multiple entry points as well: WinPackIt will generate a Windows shortcut for each one. If the entry point is a Python module (``.py`` or ``.pyw``), the shortcut will link it to the appropriate Python executable (``python.exe`` or ``pythonw.exe``). Any other file type will just be passed to ``ShellExecuteEx``, thus leaving to Windows to figure out which program is best suited to run it. 

Finally, you may even pack a project with no entry point at all: since WinPackIt will add it to ``sys.path`` anyway, it can still be imported by other projects in the same distribution. Note that this is usually bad design: we will discuss this more in detail later. 

``PROJECT_FILES_IGNORE_PATTERNS``
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

WinPackIt will copy your project folder(s) by means of  ``shutils.copytree``: you may pass a ``shutils.ignore_patterns`` list to it, to leave out unwanted files/folders. Please note that ``__pycache__`` will be automatically added to the exclusion list. 

``COMPILE``
^^^^^^^^^^^

If set, WinPackIt will compile your modules to ``.pyc`` files.

``PYC_ONLY_DISTRIBUTION``
^^^^^^^^^^^^^^^^^^^^^^^^^

If set, WinPackIt will also remove the original ``.py`` files from the distribution, producing the infamous "pyc-only distribution" for obfuscation purposes. Be aware that this is considered one of the *weakest* possible ways of protecting your code. 

If you set this option, entry point modules will also be compiled and removed. However, WinPackIt will remember the original extension (``.py`` or ``.pyw``) and will associate the compiled module with the intended Python executable. 

``COPY_DIRS``
^^^^^^^^^^^^^

A list of additional, non-Python directories to be copied into the distribution folder. The same ``PROJECT`` list format applies. The only difference is that WinPackIt will not add these folders to the Python ``sys.path``. 

This setting is intended for any additional material you may want to include in your distribution, e.g. documentation::

    COPY_DIRS = [
                 ['path/to/docs', ('index.html', 'Documentation')],
                ]

``custom_action``
^^^^^^^^^^^^^^^^^

Write here any custom code you want executed at the end of the packaging process. From here, you may access the internals of the ``winpackit.Packit`` instance at the core of WinPackIt itself... however, you will have to study the source code a bit. 

Running the runner script.
--------------------------

Once you have customized the runner script to your liking, give it a try with ``python my_runner.py``. 

The script will output a timestamped directory ``winpackit_build_<timestamp>`` with your packaged project inside, ready to be distributed. 

Post-deploy actions.
--------------------

If you open the "build" directory, you will find that WinPackIt left a ``winpackit_bootstrap/bootstrap.py`` Python script that is meant to be executed by the user to finalize the "installation" process of your program. This script will be launched by the ``install.bat`` batch file that you can see in the root "build" directory.

The bootstrap script outputs the Windows shortcuts listed in your ``PROJECTS`` and ``COPY_DIRS`` settings (see above). The shortcut files *must* be created on the target machine, their configuration depending on the user file system. 

You may take the opportunity to add your custom post-deploy actions in the bootstrap module. Just remember that this code will run on the *target* machine, not your own - keep your paths straight. 

Testing the distribution.
-------------------------

To test the distribution, just act like you were the final user. Rename/move the "build" directory, open it and double-click on the ``install.bat`` batch file. This will produce the shortcuts in the same directory: you may freely move them around (typically on your desktop folder!). When you double-click on the shortcut to the main entry point, you program should start. 

If you rename/move again the "build" folder, of course your shortcuts will stop working. Throw them away and generate new ones simply by running ``install.bat`` again. 

About isolation and import machinery.
-------------------------------------

The goal of WinPackIt is to produce a *stand-alone* distribution - that is, not only self-sufficient but also *isolated* from any other Python installation that could possibly live (or will live) on the target system. Therefore, WinPackIt won't use the canonical Python bootstrap machinery (the ``site.py`` module) for ``sys.path`` and the import system. WinPackIt will rely instead on the top-level ``pythonXX._pth`` file to manually add paths to ``sys.path``. By not using ``site.py``, WinPackIt ensures that any ``PATH``, ``PYTHONPATH`` etc. that may be present on the target system will be left out of your application's ``sys.path``. 

WinPackIt will list *all* your ``PROJECTS`` directories in the ``pythonXX._pth`` file, as discussed above. Be aware that this design is both useful and dangerous. The intended use case is to include one "main" project along with one or more "side" folders containing tools that won't be pip-installed but you still need to import, thus mimicking the behavior of ``PYTHONPATH`` dirs or maybe that of PEP 370's "per user site-packages directory". 

However, keep in mind that the ``PYTHONPATH``/PEP 370 machinery is better suited to host common *development* tools, but not also packages needed in the production environment. Therefore, while supported by WinPackIt, the strategy of having more than one ``PROJECTS`` directory is not actually encouraged. The best design is to have exactly *one* self-contained project, and pip-install all the needed dependencies.

The worst case scenario is when you include several, unrelated *projects* in the same distribution (as opposite to one project, several imported tools): each project will "see" all the others in its own ``sys.path`` and you will have to be very careful of possible name shadowing. Just don't do this - if you have different projects, make a separate WinPackIt distribution for each of them.

Python 3.5 support.
^^^^^^^^^^^^^^^^^^^

Python 3.5 has no support for ``._pth`` files. In order to be consistent with the other Python versions, WinPackIt adds all ``PROJECTS`` dirs to ``sys.path``, by means of a custom ``sitecustomize.py`` module. However, ``site.py`` *will* be imported and consequently your distribution environment *could* be a little less isolated.

Internals, examples, tests.
---------------------------

``winpackit.py`` code is quite straightforward, if not always well-documented. If you need to dig in, you may start with the ``Packit.main`` function, listing the various operations to perform during a typical build session. 

The GitHub repository has a few sample projects that can be packaged with WinPackIt: the test suite build them in various ways. 

.. _embeddable package: https://docs.python.org/3/using/windows.html#the-embeddable-package

