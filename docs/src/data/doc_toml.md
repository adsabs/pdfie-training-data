# General Document Metadata (`.doc.toml`)

The `.doc.toml` file gives general metadata about a document. Every document
must have an associated `.doc.toml` file, and in fact every document is
*defined* by the existence of this file.

The file is in [TOML] format.

[TOML]: https://toml.io/en/


## Example

Here’s the current file for `arXiv/2111/04795`:

```toml
bibcode = "2021arXiv211104795L"
pdf_sha256 = "8dd8d002c3468ef8bdafef00d2bbce985ab9a14baab8f14f7bc6974b011765fa"
pdf_n_bytes = 5610743
ads_pdf_path = "$ADS_ABSTRACTS/sources/ArXiv/fulltext/arXiv/2111/04795.pdf"
random_index = 312398
pdf_is_raster = false
arxiv_ads_add_date = "2022-07-15"
arxiv_ads_update_date = "2022-07-15"
```


## Fields

No fields are mandatory, but you are encouraged to populate all that make sense.

`bibcode`: The ADS bibcode corresponding to this document. There might be input
documents that do *not* have bibcodes.

`pdf_sha256`: The SHA256 digest of the PDF file associated with this document.
When generating new `.doc.toml` files, the Python function
`pidata.util.nbytes_and_sha256_of_path` can generate this value for you, as well
as the following one.

`pdf_n_bytes`: The number of bytes in the PDF file associated with this document.

`ads_pdf_path`: The path where this document's PDF can be found in the ADS
filesystem. Symbolic prefixes of `$ADS_ARTICLES` and `$ADS_ABSTRACTS` can (and
should) be used to abstract the paths somewhat.

`random_index`: a random integer between -1 and 999999, inclusive. The intent of
this field is to make it easy to process limited subsets of the full corpus in a
way that is randomized across the corpus, but repeatable. When generating new
`.doc.toml` files, the Python function `pidata.util.make_random_index` can
generate this value for you. A random index of -1 signifies "undefined", and
such a document will be excluded from all reproducible-random subsetting
operations.

`pdf_is_raster`: express whether the PDF is a raster or vector PDF. The default
is false, i.e., vector format. A raster PDF is one where the primary textual
content is locked up inside bitmap images and not extractable as text. There is
no automatic way to determine raster-ness, nor a fully precise definition of it:
some vector PDFs will contain text in raster images (e.g., figures delivered as
bitmaps) and some raster PDFs will contain vector elements and/or text (e.g., a
scanned PDF with a digital watermark applied).

Fields not specified here are allowed, as shown in the example above.
