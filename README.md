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


## Export for arxiv-reference-extractor processing

To export the corpus into a filesystem structure suitable for processing
using the [arxiv-reference-extractor] framework, use:

```
$ python -m pidata.export_arxiv
  [--ads-arxiv-fulltext-shadow=$PATH]
  $OUTDIR
```

This will create a tree defining two “sessions,” named `all` and `bibcodes`. The
former contains all vector PDFs with refstring “ground truth” data. The latter
contains the subset of those that also have ADS bibcode ground-truth data.

[arxiv-reference-extractor]: https://github.com/adsabs/arxiv-reference-extractor


## Export for testing the reference resolver microservice

To export the corpus into a file that can be used to test the ADS [reference
resolver service][refsvc], use:

[refsvc]: https://github.com/adsabs/reference_service

```
$ python -m pidata.export_resolver_test
  [--normalize]
  [--ascii]
  outfile.txt
```

This will create a file `outfile.txt` containing ground-truth refstrings and the
bibcodes that they *should* resolve to. The `--normalize` option will normalize
Unicode punctuation in the output refstrings; for instance, the curly double
quote `“` will be changed into the straight double quote `"`. The `--ascii`
option will further drop the output down into plain ASCII; for instance, `é`
will become `e`, and Unicode codepoints with no corresponding ASCII values will
be dropped.


## Ingesting one-off documents

We have a few PDFs of interest that aren't, and shouldn't be, part of ADS' holdings.
These can be ingested with:

```
$ python -m pidata.misc.ingest $NAME $PDF_PATH
```

followed by manual editing of the generated TOML and addition of whatever other
metadata files are appropriate. This requires the environment variable
`$PDFIE_LOCAL_DATA` to be set.
