# The *Solar Physics* Collection

We're interested in this collection because the data are provided as PDF files
without structured reference information.

As always, see also the file `pidata/soph/README.md`.


## Identification

Items within this collection are grouped by volume, and named by their final
bibcode, e.g. `0294/2019SoPh..294..138W`.


## Ingestion

The script `index.py` in the repo directory will scan and ingest PDFs based on
which ones have XML metadata, based on the `all.links` file in the ADS
filesystem. This file is known to have issues with completeness and correctness
regarding SoPh, though.

