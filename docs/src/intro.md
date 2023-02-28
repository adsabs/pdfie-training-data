# Introduction

This documentation describes a corpus of training data for various PDF
information extraction (IE) activities undertaken by [ADS].

[ADS]: https://ui.adsabs.harvard.edu/

The training corpus is stored in a Git repository (original copy:
[adsabs/pdfie-training-data] on GitHub) that combines data, code, and this
documentation. The data in the repository do not include actual PDFs, which are
instead stored externally.

[adsabs/pdfie-training-data]: https://github.com/adsabs/pdfie-training-data


## High-Level Data Structure

The corpus consists of a number of *documents*. Each document has:

- An identifier that is globally unique within this framework
- Exactly one associated PDF file
- Various other pieces of associated training data and metadata, stored in a
  flexible and extensible manner.

Documents are organized into *collections*, which group documents of similar
characteristics. (E.g., there is an `esasp` collection for a set of PDFs from
the ESA Special Publications series.) Each collection has a globally unique
identifier. Each document is uniquely identified within its collection by its
*collection ID*, and each document's *global ID* is the combination of its
collection's unique identifier and its collection ID. (There are examples
below.)

Processing generally occurs document-by-document, without caring about which
particular collection a document belongs to. But collections may have associated
housekeeping scripts that “know” some things about the shared characterisics
about the documents in a collection.


## Repository Structure

The structure of the Git repository, relative to its root, is as follows:

- The `docs/` tree contains this documentation.
- The `pidata/` tree contains a mixture of Python code and the actual training
  data.

Underneath `pidata/` you can find one subdirectory for each collection.
Information about individual documents is stored in sets of files found in
further subdirectories of the collection subdirectory. For instance, the
`pidata/esasp/` directory contains data associated with the aforementioned ESA
Special Publications. Within that tree, there are three files with names of the
form `pidata/esasp/0624/2006ESASP.624E.100N.*`. These files define a document
with a collection ID of `0624/2006ESASP.624E.100N`. The global ID of this
document is `esasp/0624/2006ESASP.624E.100N`.

The different files defining a document can by identified by their *extensions*,
that is, the text that corresponds to the asterisk above. Document
`esasp/0624/2006ESASP.624E.100N` currently has data for three extensions:

- [`.doc.toml`](./data/doc_toml.md), defining essential document metadata. Every
  document must have a corresponding `.doc.toml` file, and in fact the existence
  of this file is what “creates” a document.
- [`.rs.txt`](./data/rs_txt.md), giving the “ground-truth” reference strings
  (*refstrings*) that should be extracted from the document.
- [`.bc.txt`](./data/bc_txt.md), giving the ground-truth bibcodes that those
  refstrings should resolve to (although sometimes the resolver is not actually
  able to figure out the correct bibcode even when it is given the correct
  refstring as input)

The `pidata/esasp/` directory also contains a `README.md` file, describing
characteristics of the collection, and Python modules with utility code specific
to this collection. From the repository top-level directory, Python code can
`import pidata.esasp` to gain access to these modules.


## Extensibility

Right now, this corpus focuses purely on reference string extraction. However,
the data architecture is designed so that new tasks can be supported merely be
adding new “extensions” with the appropriate data for one or more documents. The
different actions scan the whole corpus but filter by the metadata that they
need to do their specific jobs.