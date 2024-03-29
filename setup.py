from setuptools import setup, find_packages
from os import path

here = path.abspath(path.dirname(__file__))

with open(path.join(here, 'readme.rst'), encoding='utf-8') as f:
    long_description = f.read()

setup(
    name='WinPackIt', 
    version='0.8.0',
    description='The quick and dirty Python packager for Windows',  
    long_description=long_description,
    long_description_content_type='text/x-rst',
    url='https://github.com/ricpol/winpackit',
    author='Riccardo Polignieri',  
    # author_email='', 
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Environment :: Console', 
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Build Tools',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Operating System :: Microsoft :: Windows',
    ],
    keywords='packaging build development',  
    py_modules=['winpackit'],
    python_requires='>=3.6',
    project_urls={
        'Source': 'https://github.com/ricpol/winpackit',
        'Docs': 'https://github.com/ricpol/winpackit/blob/master/docs.rst',
    },
)
