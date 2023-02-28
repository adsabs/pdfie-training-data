# PDF Information Extraction Training Data

Training data for various PDF information extraction activities performed by
[ADS].

[ADS]: https://ui.adsabs.harvard.edu/

The basic model of this repo is that it contains *small* training datasets that
are organized into “collections” using homogeneous data formats. The big data —
namely, PDFs — are stored externally. Straightforward scripts transform subsets
of these data into formats used by ML tools, ADS pipelines, etc.

The data and associated Python support code are intermixed in the `pidata/`
subdirectory tree.

For detailed documentation, see the Markdown files in the `docs/src/`
subdirectory, which can be processed with [mdBook] into a nice HTML book or
[explored on GitHub][1]. The [mdBook] tool is easily to install and run, but you
can also just browse the Markdown source pretty easily if needed. **TODO:** host
built documentation online somewhere!

[mdBook]: https://rust-lang.github.io/mdBook/
[1]: https://github.com/adsabs/pdfie-training-data/blob/main/docs/src/SUMMARY.md
