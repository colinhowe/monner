from setuptools import setup
    
import os

root_dir = os.path.dirname(__file__)
if not root_dir:
    root_dir = '.'
long_desc = open(root_dir + '/README.rst').read()

setup(
    name='monner',
    version='0.5.0',
    description='Monitors the system whilst executing a given program',
    url='https://github.com/colinhowe/monner',
    author='Colin Howe',
    author_email='colin@colinhowe.co.uk',
    scripts=['monner.py'],
    install_requires=['psutil >= 0.4.0'],
    classifiers=[
        'Development Status :: 4 - Beta',
        'License :: OSI Approved :: Apache Software License',
        'Operating System :: OS Independent',
        'Topic :: Utilities',
    ],
    entry_points= {
        'console_scripts': [
            'monner = monner:main'
        ]
    },
    license='Apache 2.0',
    long_description=long_desc,
)
