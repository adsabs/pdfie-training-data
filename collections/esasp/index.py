#! /usr/bin/env python3

"""
Generate the TOML files to index the ESASP PDFs.

This is the very first indexer I'm writing. We may just copy/paste this stuff
forever, or maybe centralize it into some common scripts.

Only a subset of ESASP has textual references available, so we index from that subset.
"""

import hashlib
import os.path
import toml

REFERENCES_PREFIX = os.environ.get("ADS_REFERENCES", "/proj/ads/references")
ARTICLES_PREFIX = os.environ.get("ADS_ARTICLES", "/proj/ads/articles")
COLL_PREFIX = os.path.dirname(__file__)

REFERENCES_SUBDIR = "sources/ESASP"
ARTICLES_PDF_SUBDIR_TMPL = "bitmaps/seri/ESASP/{vol}/PDF/{bibcode}.pdf"


def do_one_doc(refdirpath: str, reffn: str):
    """
    refdirpath is like `/proj/ads/references/sources/ESASP/0624`
    reffn is like `2006ESASP.624E..85B.raw`
    """

    bibcode, ext = os.path.splitext(reffn)
    if ext != ".raw":
        return

    vol = os.path.basename(refdirpath)

    # Hack!
    bibcode = bibcode.replace("ESASP.624", "soho...18")

    pdf_sub_path = ARTICLES_PDF_SUBDIR_TMPL.format(vol=vol, bibcode=bibcode)
    pdf_path = os.path.join(ARTICLES_PREFIX, pdf_sub_path)

    # Analyze PDF file

    b = bytearray(128 * 1024)
    mv = memoryview(b)
    h = hashlib.sha256()
    n_bytes = 0

    with open(pdf_path, "rb", buffering=0) as f:
        while n := f.readinto(mv):
            h.update(mv[:n])
            n_bytes += n

    # Emit

    metadata = {
        "bibcode": bibcode,
        "pdf_sha256": h.hexdigest(),
        "pdf_n_bytes": n_bytes,
        "pdf_path": "$ADS_ARTICLES/" + pdf_sub_path,
    }

    toml_path = os.path.join(COLL_PREFIX, vol, bibcode + ".doc.toml")
    print(toml_path)

    with open(toml_path, "wt") as f:
        toml.dump(metadata, f)


def main():
    ref_root = os.path.join(REFERENCES_PREFIX, REFERENCES_SUBDIR)

    for dirpath, _dirnames, filenames in os.walk(ref_root):
        for fn in filenames:
            do_one_doc(dirpath, fn)


if __name__ == "__main__":
    main()
