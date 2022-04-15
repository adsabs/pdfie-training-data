# Uncategorized Notes

Writing down some notes. Not structuring them now; will figure out how to
arrange things as work continues. Right???


## Nomenclature

**Document:** A single item in the training dataset. It has at least one unique
identifier, a uniquely associated PDF file, and lots of different kinds of
metadata.

**Collection:** A group of related documents. You can uniquely identify a
document from its collection name and some kind of sub-unique identifier within
the collection. The globally unique ID is the “global ID”, the within-collection
ID is the “collection ID”.

**Refstring:** the text of a single reference as it appears at the end of a
scholarly paper. This information is not structured. TODO: figure out how
Unicode-y to be and how to handle HTML (e.g., hyperlinks in the references found
in PDFs can convey information that we might lose if we don't preserve the
linkiness.)


## Filesystem Structure

Relative to the repo root:

The `docs/` tree contains this documentation.

The `collections/` tree contains a mixture of Python code and the actual
training data. Underneath `collections/` you can find one subdirectory for each
collection.

Collection-level metadata and scripts live in the “collection subdirectory”, e.g.
within `collections/esasp/` for the `esasp` collection.

All files in subdirectories of the collection subdirectory provide some kind of
metadata for a document. The precise depth and name of the sub-sub-directory
structure doesn’t matter. IDs are derived from filenames. For instance, the file
`collections/esasp/foo/bar/123456.doc.toml` would automatically define a
document in the `esasp` collection with collection ID `foo/bar/123456` and global
ID `esasp/foo/bar/123456`.

Different filename extensions/endings define different categories of document
data. Unrecognized extensions are ignored.

**The `.doc.toml` extension** gives high-level document metadata.

**The `.rr.txt` extension** gives resolved references: both a refstring and an
ADS bibcode, if the refstring resolves to one. These use Unicode to match
typography as precisely as possible, and do *not* use HTML.
