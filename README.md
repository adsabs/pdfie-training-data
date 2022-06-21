# PDF Information Extraction Training Data

Training data for various PDF information extraction activities.

The basic model of this repo is that it contains *small* training datasets that
are organized into “collections” using homogeneous data formats. The big data —
namely, PDFs — are stored externally. Straightforward scripts transform subsets
of these data into formats used by ML tools, ADS pipelines, etc.

For some summary statistics about the corpus, run:

```
$ python -m pidata
```
