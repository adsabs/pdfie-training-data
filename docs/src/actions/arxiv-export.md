# Export for arxiv-reference-extractor processing

To export the corpus into a filesystem structure suitable for processing
using the [arxiv-reference-extractor] framework, use:

[arxiv-reference-extractor]: https://github.com/adsabs/arxiv-reference-extractor

```
$ python -m pidata.export_arxiv
  [--ads-arxiv-fulltext-shadow=$PATH]
  $OUTDIR
```

It would not be unreasonable to think of this functionality as a bit of a hack.
Basically, the Arxiv reference extractor is built to, well, extract references
from Arxiv postings. It prefers to get references by processing each post’s TeX
source, but can extract references from the post PDF if needed. So, the
reference extraction system provides a framework to extract references from a
large number of PDFs as part of its functionality. This command (ab)uses that
capability by plugging in the contents of this training set into that framework,
even though only some PDFs in this corpus correspond to actual Arxiv postings.

(In principle, we might one day have a freestanding “PDF IE” service that
extracts information from any kind of PDF, and the Arxiv pipeline might use that
service specifically to extract references from Arxiv PDFs. But right now, the
PDF extraction infrastructure is all embedded in the Arxiv pipeline, as are
various useful tools for doing analytics on the results.)

This command will create a filesystem tree defining two “sessions” (see the
Arxiv reference extractor documentation) named `all` and `bibcodes`. The former
contains all vector PDFs with refstring “ground truth” data. The latter contains
the subset of those that also have ADS bibcode ground-truth data.

The `--ads-arxiv-fulltext-shadow` option activates, as one might guess, an even
more specialized and hacky mode. Its agument specifies the path to a “fulltext”
tree that the ArXiv reference extractor framework would use for its
containerized processing. The shadow mode will create symlinks *out of* that
tree *into* the ADS PDF paths specified in the metadata for each document in
this corpus, allowing the Arxiv reference extractor framework to actually locate
the PDFs it needs to do its job. This functionality will only work when running
on the ADS system or NFS/sshfs mounts have been set up to emulate it, because
the destinations of those symlinks are match the ADS filesystem structure.
