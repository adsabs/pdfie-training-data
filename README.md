# PDF Information Extraction Training Data

Training data for various PDF information extraction activities.

The basic model of this repo is that it contains *small* training datasets that
are organized into “collections” using homogeneous data formats. The big data —
namely, PDFs — are stored externally. Straightforward scripts transform subsets
of these data into formats used by ML tools, ADS pipelines, etc.


## Summary statistics

For some summary statistics about the corpus, run:

```
$ python -m pidata
```


## arxiv-reference-extractor export

To export the corpus into a filesystem structure suitable for processing
using the [arxiv-reference-extractor] framework, use:

```
$ python -m pidata.export_arxiv
  [--ads-arxiv-fulltext-shadow=$PATH]
  $OUTDIR
```

This will create a tree defining a single “session” named `all`.

[arxiv-reference-extractor]: https://github.com/adsabs/arxiv-reference-extractor


## Ingesting one-off documents

We have a few PDFs of interest that aren't, and shouldn't be, part of ADS' holdings.
These can be ingested with:

```
$ python -m pidata.misc.ingest $NAME $PDF_PATH
```

followed by manual editing of the generated TOML and addition of whatever other
metadata files are appropriate. This requires the environment variable
`$PDFIE_LOCAL_DATA` to be set.
