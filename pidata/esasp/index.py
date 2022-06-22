#! /usr/bin/env python3
# Licensed under GPLv3
# Copyright 2022 SAO/NASA Astrophysics Data System

"""
Generate the TOML files to index the ESASP PDFs.

This is the very first indexer I'm writing. We may just copy/paste this stuff
forever, or maybe centralize it into some common scripts.

Only a subset of ESASP has textual references available, so we index from that subset.
"""

import os.path
import toml

from .. import util

COLL_PREFIX = os.path.dirname(__file__)

REFERENCES_SUBDIR = "sources/ESASP"
ARTICLES_PDF_SUBDIR_TMPL = "bitmaps/seri/ESASP/{vol}/PDF/{bibcode}.pdf"
PDFS_ARE_RASTER = True


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
    pdf_path = os.path.join(util.ADS_ARTICLES_PREFIX, pdf_sub_path)
    n_bytes, sha256 = util.nbytes_and_sha256_of_path(pdf_path)

    metadata = {
        "bibcode": bibcode,
        "pdf_sha256": sha256,
        "pdf_n_bytes": n_bytes,
        "ads_pdf_path": "$ADS_ARTICLES/" + pdf_sub_path,
        "random_index": util.make_random_index(),
        "pdf_is_raster": PDFS_ARE_RASTER,
    }

    toml_path = os.path.join(COLL_PREFIX, vol, bibcode + ".doc.toml")
    print(toml_path)

    with open(toml_path, "wt") as f:
        toml.dump(metadata, f)


def main():
    ref_root = os.path.join(util.ADS_REFERENCES_PREFIX, REFERENCES_SUBDIR)

    for dirpath, _dirnames, filenames in os.walk(ref_root):
        for fn in filenames:
            do_one_doc(dirpath, fn)


if __name__ == "__main__":
    main()
