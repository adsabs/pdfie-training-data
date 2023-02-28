# The `arxivads` Collection

This collection is for ArXiv.org PDFs that are mirrored within ADS' filesystem.

As always, see also the file `pidata/arxivads/README.md`.


## Identification

Items within this collection are identified by their arXiv identifier in
directory form, e.g., `arXiv/2111/01232`.


## Known issues

The ADS PDFs change over time! Arxiv papers get updated, but ADS has no sense of
Arxiv revisions, so it just updates the PDF that we point at. Some of our PDF
metadata are now out of data, as are our refstrings and other derived products.
Gross. We should develop a system for dealing with this.

The `check.py` script in the repo directory will scan an Arxiv-month, look for
updated PDFs, and rewrite the data for anything that's changed. Since this goes
back to the original ADS data, which have various problems, one should then
manually review the diffs in Git to make sure that corrections are not lost.

The `index.py` script mentioned below needs updating to handle bibcode ingest
and to record import dates relevant to the changing-PDFs issue.


## Ingestion

The `index.py` script in the repo directory will scan an Arxiv-month and create
records for every posting where *every single refstring* (known to ADS)
successfully resolves to a bibcode. The presumption is that these documents are
likely to have high-quality extractions. This process will of course generate a
highly biased subsample of Arxiv, but we don't expect that to be a problem for
our purposes.

Once documents are detected, you'll want to review their refstrings and bibcodes
and make sure everything is as high-quality as it can be.

A given month of Arxiv postings will yield about 200 new documents, sufficient
to grow this corpus to whatever size we want.
