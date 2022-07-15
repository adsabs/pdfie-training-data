#! /usr/bin/env python3
# Licensed under GPLv3
# Copyright 2022 SAO/NASA Astrophysics Data System

"""
Generate TOML and refstring files for ADS's ArXiv holdings.

This scans a month at a time, searching for items that seem to have top-quality
extractions.

"""

import argparse
from dataclasses import dataclass
import html.entities
import os.path
from pathlib import Path
import toml
from typing import Dict, List, Optional, TextIO

from .. import util


COLL_PREFIX = Path(os.path.dirname(__file__))
RESOLVED_SUBDIR = "resolved"  # within $ADS_REFERENCES_PREFIX
FULLTEXT_SUBDIR = "sources/ArXiv/fulltext"  # within $ADS_ABSTRACTS_PREFIX
PDFS_ARE_RASTER = False
MIN_NUMBER_OF_REFS = 8

@dataclass
class Doc:
    bibcode: str = None
    pdf_path: str = None
    refstrings: List[str] = None

    def create_toml_metadata(self):
        ads_pdf_path = self.pdf_path.replace(
            str(util.ADS_ABSTRACTS_PREFIX), "$ADS_ABSTRACTS"
        )

        n_bytes, sha256 = util.nbytes_and_sha256_of_path(self.pdf_path)

        return {
            "bibcode": self.bibcode,
            "pdf_sha256": sha256,
            "pdf_n_bytes": n_bytes,
            "ads_pdf_path": ads_pdf_path,
            "random_index": util.make_random_index(),
            "pdf_is_raster": PDFS_ARE_RASTER,
        }



def assess_candidate(arxiv_id: str, rr: Path) -> Optional[Doc]:
    """
    Check a candidate for inclusion.
    """
    pdf_path = util.ADS_ABSTRACTS_PREFIX / FULLTEXT_SUBDIR / (arxiv_id + ".pdf")
    if not pdf_path.exists():
        return None

    with rr.open("rt") as f:
        bibcode = f.readline().strip()[4:-4]
        refstrings = []

        for line in f:
            score, ref_bibcode, sep, refstring = line.strip().split(None, 3)

            # 0 score is no match. 5 score is guessed bibcode that may or may
            # not actually be real. It seems that if we demand all 1's, which
            # are confident resolutions, we can still get enough successes for
            # this to be worthwhile, so let's not mess with the 5's.
            if int(score) != 1:
                return None

            refstrings.append(refstring)

        if len(refstrings) < MIN_NUMBER_OF_REFS:
            # Maybe they all succeeded because parsing failed and we only pulled
            # out a few? No idea whether this is a problem in practice, but
            # again, we succeed often enough *with* this filter that I'm not
            # motivated to try to relax it.
            return None

    return Doc(
        bibcode = bibcode,
        pdf_path = str(pdf_path),
        refstrings = refstrings,
    )


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "prefix",
        help="ArXiv item prefix to filter by, e.g. `arXiv/2111`"
    )

    settings = parser.parse_args()

    pfx_len = len(str(util.ADS_REFERENCES_PREFIX / RESOLVED_SUBDIR)) + 1
    res_path = util.ADS_REFERENCES_PREFIX / RESOLVED_SUBDIR / settings.prefix
    n_scanned = 0
    n_accepted = 0
    n_skipped_preexist = 0
    n_tot_refstrings = 0

    out_dir = COLL_PREFIX / settings.prefix
    out_dir.mkdir(parents=True, exist_ok=True)

    for fn in res_path.iterdir():
        if not fn.name.endswith(".raw.result"):
            continue

        n_scanned += 1
        arxiv_stem = fn.name[:-11]
        arxiv_id = str(fn)[pfx_len:-11]
        doc = assess_candidate(arxiv_id, fn)
        if doc is None:
            continue

        # OK, we probably want to use it!

        toml_path = out_dir / (arxiv_stem + ".doc.toml")
        if toml_path.exists():
            n_skipped_preexist += 1
            continue

        n_accepted += 1
        n_tot_refstrings += len(doc.refstrings)

        with toml_path.open("wt") as f:
            toml.dump(doc.create_toml_metadata(), f)

        rs_path = out_dir / (arxiv_stem + ".rs.txt")
        with rs_path.open("wt") as f:
            for rs in doc.refstrings:
                print(rs, file=f)

    print(f"Scanned {n_scanned} items.")
    if n_skipped_preexist:
        print(f"Skipped {n_skipped_preexist} items with existing doc.toml files.")
    print(f"Accepted {n_accepted} items containing a total of {n_tot_refstrings} refstrings.")


if __name__ == "__main__":
    main()
