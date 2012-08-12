======
Monner
======

Author: Colin Howe (@colinhowe)

License: Apache 2.0

About
=====

Allows you to monitor the CPU, memory and network usage when running a program.

Output is tab-separated for easy loading into spreadsheet programs.

Installation
============

Install from pypi::

    pip install monner

Install from source::

    python setup.py install

Run::

    monner --target-output /dev/null -c wget http://www.google.com

The option --target-output will redirect stdout and stderr for the target
program.

Sample output::

    CPU (%)	Memory used (mb)	Network in (kb)	Network out (kb)
       99.5	          3470.4	            1.2	             0.0
      100.0	          3470.9	           50.7	             0.0
      100.0	          3470.8	            2.2	             0.0

Fields Available
================

There are multiple fields available to monitor. Including: CPU usage, memory
usage, network usage, disk usage and more. For the full list see ``monner -h``

Feedback
========

Feedback is always welcome! Github or twitter (@colinhowe) are the best places
to reach me.

