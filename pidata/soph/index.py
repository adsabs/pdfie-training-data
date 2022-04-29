#! /usr/bin/env python3
# Licensed under GPLv3
# Copyright 2022 SAO/NASA Astrophysics Data System

"""
Generate TOML and refstring files for SoPh.

There are more files with reference data than there are fulltext PDFs. The XML
data are (sometimes) only identified by bibcode, so we need to associate
fulltext files with bibcodes, which we can do through the file
`/proj/ads/abstracts/config/links/fulltext/all.links`. Many of the PDFs listed
there, though, are from ArXiv, not official publisher data.

In some cases the XML reference files are on a per-article basis, e.g.:
`$ADS_REFERENCES/sources/SoPh/0080/10.1007_BF00147969.xref.xml`, with
structure::

    <ADSBIBCODE>$bibcode</ADSBIBCODE>
    <citation_list>
        <citation>
            <unstructured_citation>text...</>
        </>
        <citation>
        ...
    </citation_list>

In other cases, data for several articles are in one file, e.g.:
`$ADS_REFERENCES/sources/SoPh/0209/iss1.springer.xml`::

    <ADSBIBCODE>$bibcode1</ADSBIBCODE>
    <Citation>
        {structured data}
        <BibUnstructured>text...</BibUnstructured>
    </Citation>
    <Citation>
    ...
    </Citation>
    <ADSBIBCODE>$bibcode2</ADSBIBCODE>
    <Citation>
    ...

There are also JATS files with no "unstructured" version of the reference, e.g.
`$ADS_REFERENCES/sources/SoPh/0297/iss.jats.xml`.

"""

from dataclasses import dataclass
import hashlib
import os.path
import toml
from typing import Dict

REFERENCES_PREFIX = os.environ.get("ADS_REFERENCES", "/proj/ads/references")
FULLTEXT_PREFIX = os.environ.get("ADS_FULLTEXT", "/proj/ads/fulltext")
ABSTRACTS_PREFIX = os.environ.get("ADS_ABSTRACTS", "/proj/ads/abstracts")
COLL_PREFIX = os.path.dirname(__file__)

REFERENCES_SUBDIR = "sources/SoPh/"
FULLTEXT_SUBDIR = "sources/SoPh/"

FULLTEXT_LINKS_PATH = os.path.join(ABSTRACTS_PREFIX, "config/links/fulltext/all.links")

@dataclass
class Doc:
    bibcode: str = None
    pdf_path: str = None
    xml_path: str = None


def scan_candidates():
    # First scan the "links" file for bibcodes and PDF paths. Filter by
    # fulltext path to identify the publisher PDFs. NB: `/proj/ads/fulltext`
    # is just a symlink to `/proj/ads/articles/fulltext`, but the former
    # is the prefix used in this file.

    cands = {}
    prefix = os.path.join(FULLTEXT_PREFIX, FULLTEXT_SUBDIR)
    seen_volumes = set()

    with open(FULLTEXT_LINKS_PATH, "rt") as f:
        for line in f:
            pieces = line.split()
            if len(pieces) > 1 and pieces[1].startswith(prefix):
                bibcode = pieces[0]
                pdf_path = pieces[1]
                doc = Doc(bibcode=bibcode, pdf_path=pdf_path)
                cands[bibcode] = doc

                volume = pdf_path[len(prefix):].split('/', 1)[0]
                seen_volumes.add(volume)

    print("Found {len(cands)} bibcode/publisher-PDF links")


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
