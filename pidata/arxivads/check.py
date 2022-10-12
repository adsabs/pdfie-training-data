#! /usr/bin/env python3

"""
Check for updates to ADS's versions of ArXiv content.

ADS has no concept of versioning of ArXiv items. When an ArXiv posting is
updated, ADS just overwrites its copy, losing information about the previous
version. This makes it challenging for us to maintain a stable source of ground
truth!
"""

import argparse
from dataclasses import dataclass
import os.path
from pathlib import Path
import toml
import time
from typing import Dict, List

from pidata import util


COLL_PREFIX = Path(os.path.dirname(__file__))
RESOLVED_SUBDIR = "resolved"  # within $ADS_REFERENCES_PREFIX
FULLTEXT_SUBDIR = "sources/ArXiv/fulltext"  # within $ADS_ABSTRACTS_PREFIX


@dataclass
class Doc:
    toml_path: Path = None
    info: Dict[str, object] = None
    cur_n_bytes: int = None
    cur_sha256: str = None
    cur_bibcode: str = None
    cur_refstrings: List[str] = None
    cur_bibcodes: List[str] = None

    def __init__(self, toml_path: Path, rr_path: Path):
        self.toml_path = toml_path

        with toml_path.open("rt") as f:
            self.info = toml.load(f)

        ads_pdf_path = self.info["ads_pdf_path"]
        pdf_path = ads_pdf_path.replace(
            "$ADS_ABSTRACTS", str(util.ADS_ABSTRACTS_PREFIX)
        )
        self.cur_n_bytes, self.cur_sha256 = util.nbytes_and_sha256_of_path(pdf_path)

        with rr_path.open("rt") as f:
            self.cur_bibcode = f.readline().strip()[4:-4]
            refstrings = []
            bibcodes = []

            for line in f:
                score, ref_bibcode, _sep, refstring = line.strip().split(None, 3)

                if int(score) != 1:
                    util.warn(f"refstring score != 1: {line!r}")

                refstrings.append(refstring)
                bibcodes.append(ref_bibcode)

        self.cur_refstrings = refstrings
        self.cur_bibcodes = bibcodes

    def needs_update(self):
        return (
            self.cur_n_bytes != self.info["pdf_n_bytes"]
            or self.cur_sha256 != self.info["pdf_sha256"]
        )

    def rewrite(self):
        today = time.strftime("%Y-%m-%d")

        self.info["pdf_n_bytes"] = self.cur_n_bytes
        self.info["pdf_sha256"] = self.cur_sha256
        self.info["arxiv_ads_update_date"] = today

        with self.toml_path.open("wt") as f:
            toml.dump(self.info, f)

        rs_path = str(self.toml_path).replace(".doc.toml", ".rs.txt")
        with open(rs_path, "wt") as f:
            for refstring in self.cur_refstrings:
                print(refstring, file=f)

        bc_path = str(self.toml_path).replace(".doc.toml", ".bc.txt")
        with open(bc_path, "wt") as f:
            for bibcode in self.cur_bibcodes:
                print(bibcode, today, file=f)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "prefix", help="ArXiv item prefix to filter by, e.g. `arXiv/2111`"
    )
    settings = parser.parse_args()

    res_path = util.ADS_REFERENCES_PREFIX / RESOLVED_SUBDIR / settings.prefix
    out_dir = COLL_PREFIX / settings.prefix
    pfx_len = len(str(COLL_PREFIX)) + 1
    n_scanned = 0
    n_to_update = 0

    for fn in out_dir.iterdir():
        if not fn.name.endswith(".doc.toml"):
            continue

        n_scanned += 1
        arxiv_stem = fn.name[:-9]
        arxiv_id = str(fn)[pfx_len:-9]
        print(arxiv_id, "...")

        rr_path = res_path / (arxiv_stem + ".raw.result")
        doc = Doc(fn, rr_path)

        if doc.needs_update():
            print("... needs update")
        else:
            continue

        n_to_update += 1
        doc.rewrite()

    print()
    print(f"Scanned {n_scanned} documents")
    print(f"There were {n_to_update} needing updates")


if __name__ == "__main__":
    main()
