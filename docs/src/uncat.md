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

**Raster PDF:** A PDF where the primary textual content is locked up inside
bitmap images and not extractable as text. The opposite of a **vector PDF**. We
don't have an automatic way to determine raster-ness, nor a fully precise
definition of it. Note that some vector PDFs will contain text in raster images
(e.g., figures delivered as bitmaps) and some raster PDFs will contain vector
elements and/or text (e.g., a scanned PDF with a digital watermark applied).

**Refstring:** the text of a single reference as it appears at the end of a
scholarly paper. This information is not structured. TODO: figure out how
Unicode-y to be and how to handle HTML (e.g., hyperlinks in the references found
in PDFs can convey information that we might lose if we don't preserve the
linkiness.)


## Filesystem Structure

Relative to the repo root:

The `docs/` tree contains this documentation.

The `pidata/` tree contains a mixture of Python code and the actual
training data. Underneath `pidata/` you can find one subdirectory for each
collection.

Collection-level metadata and scripts live in the “collection subdirectory”, e.g.
within `pidata/esasp/` for the `esasp` collection.

All files in subdirectories of the collection subdirectory provide some kind of
metadata for a document. The precise depth and name of the sub-sub-directory
structure doesn’t matter. IDs are derived from filenames. For instance, the file
`pidata/esasp/foo/bar/123456.doc.toml` would automatically define a
document in the `esasp` collection with collection ID `foo/bar/123456` and global
ID `esasp/foo/bar/123456`.

Different filename extensions/endings define different categories of document
data. Unrecognized extensions are ignored.

**The `.doc.toml` extension** gives high-level document metadata.

**The `.rs.txt` extension** gives the ground-truth refstrings, folded to one per
line. These use Unicode to match typography as precisely as possible, and do
*not* use HTML. Numbering typography such as leading `[3]` should not be
included. Hyphens introduced for linebreaks should be removed.

**The `.bc.txt` extension** gives the ground-truth bibcodes, folded to one per
line, followed by a date of the form `YYYY-MM-DD` indicating when the bibcode
was last validated or updated. A sequence of 19 periods should be used for
refstrings that do not resolve to ADS bibcodes. Note that the contents of this
file may evolve while refstrings stay fixed, because new records are added to
ADS and existing records may be reidentified. (E.g., if the first author of an
entry was wrong, the last character will change when the mistake is corrected;
or a temporary Arxiv bibcode may be updated to the bibcode for a final published
paper.)
