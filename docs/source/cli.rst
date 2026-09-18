Command-line interface
======================

Distance from parallax
----------------------

.. click:: cobtools.cli.astrometry.parallax_to_distance:estimate_distance
   :prog: par_to_dist
   :nested: full

Peculiar velocity from astrometry
---------------------------------

.. click:: cobtools.cli.astrometry.vpec_from_astrometry:calc_vpec
   :prog: vpec_from_astrometry
   :nested: full

Gaia source query
-----------------

.. click:: cobtools.cli.gaia.query_single_source:query_useful_info
   :prog: gaia_single_source
   :nested: full

Peculiar velocity from Gaia
---------------------------

.. click:: cobtools.cli.astrometry.vpec_from_source_id:calc_vpec
   :prog: vpec_from_source_id
   :nested: full
