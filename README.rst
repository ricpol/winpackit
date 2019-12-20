WinPackIt - the quick and dirty Python packager for Windows.
============================================================

WinPackIt is the ``winpackit.py`` module, a Python script with no external dependency required. 
It will package your Python project into a stand-alone Windows distribution. 

How does it work.
-----------------

Python 3.5 introduced the `embeddable package <https://docs.python.org/3/using/windows.html#the-embeddable-package>_` distribution on Windows: that is, an "almost complete" Python zipped in a single, non-installer file. While intended mainly for embedding purposes, the opposite is also possible: with some tinkering, one can make this package into a full-fledged self-contained Python environment ready to support a Python application. 

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
- open it and double-clic the ``install.bat`` file;
- this in turn will produce Windows shortcut(s) to the entry-point(s) of your app to double-click, tailored for their machine. 

Requirements.
-------------

You will need Python 3.6+ to run WinPackIt. No external dependency is required. On the target side, you can produce builds based on any Python 3.5+. You don't have to match your own Python with the target Python.

Linux/Mac users.
^^^^^^^^^^^^^^^^

The WinPackIt script runs on Linux too, of course. Except, the build process needs to run the target Python a few times in order to install external packages and compile ``.pyc`` files - and *that* will be impossible on Linux. Then again, if you need no external packages nor compiling, it should work as a charm. See docs for more details. 

Usage.
------

- ``pip install winpackit`` in your virtual environment, or even ``pipx install winpackit`` if your really like WinPackIt and would love to have it always at hand;
- run ``python -m winpackit my_runner.py``;
- this will produce a ``my_runner.py`` runner file for WinPackIt: open it and customize to your liking;
- run ``python my_runner.py``;
- this will produce a "build" folder of your project, as specified in the runner file settings, ready to be distributed to the final user.

**See the docs for more details.**
