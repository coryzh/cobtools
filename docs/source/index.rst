.. cobtools documentation master file, created by
   sphinx-quickstart on Fri Mar 13 15:11:19 2026.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.


cobtools
========
``cobtools`` is a Python toolkit of utilities I use for compact-binary research. 
The current version includes tools for astrometry, photometry, plotting, and querying astronomical databases.
These tools can be imported and used in Python scripts, and there are also command-line scripts available for easier 
usage.

Installation
------------

Install the latest development version directly from GitHub:

.. code-block:: console

   python -m pip install git+https://github.com/coryzh/cobtools.git


For development purposes, you can clone the repository and install it in editable mode:

.. code-block:: console

   git clone https://github.com/coryzh/cobtools.git
   cd cobtools
   python -m pip install -e .


Common tasks
------------
* :doc:`Estimate distances and velocities <cobtools.astrometry>`
* :doc:`Convert fluxes, magnitudes, and colour indices <cobtools.photometry>`
* :doc:`Query Gaia data <cobtools.query>`
* :doc:`Work with Gaia, LSST, and Lasair data models <cobtools.data_models>`
* :doc:`Create CMD and ECDF plots <cobtools.plot_utils>`
* :doc:`Browse the complete API reference <cobtools>`


API reference
-------------

.. toctree::
   :maxdepth: 2

   cobtools
