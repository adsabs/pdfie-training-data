# Licensed under GPLv3
# Copyright 2022 SAO/NASA Astrophysics Data System

"""
Export the database into a format suitable for use with the
arxiv-reference-extractor pipeline.
"""

import argparse
import os
from pathlib import Path
import shutil

from . import scan

ARTICLES_PREFIX = os.environ.get("ADS_ARTICLES", "/proj/ads/articles")
REFERENCES_PREFIX = os.environ.get("ADS_REFERENCES", "/proj/ads/references")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("out_dir")
    settings = parser.parse_args()

    out_dir = Path(settings.out_dir)

    # Possible elaboration: group everything into different sessions in
    # different ways? One obvious way to do that would be by collection, but
    # it's not obvious to me that that's actually useful.
    session_id = "all"

    fulltext_prefix = "pdfietd"

    docs = list(scan(bibcode=True, rs=True, no_raster=True))
    print(f"Scan yielded {len(docs)} documents.")

    # Do the log files

    logs_dir = out_dir / "logs" / session_id
    logs_dir.mkdir(parents=True, exist_ok=True)

    with (logs_dir / "extractrefs.out").open("wt") as f:
        for doc in docs:
            arxiv_id = doc.global_id.replace(".", "_")
            fake_pdf_path = f"{fulltext_prefix}/{arxiv_id}.pdf"
            refs_path = os.path.join(
                REFERENCES_PREFIX, "sources", fulltext_prefix, arxiv_id + ".raw"
            )
            print(fake_pdf_path, refs_path, file=f)

    print(f"Wrote `{logs_dir / 'extractrefs.out'}`")

    with (logs_dir / "fulltextharvest.out").open("wt") as f:
        for doc in docs:
            arxiv_id = doc.global_id.replace(".", "_")
            fake_pdf_path = f"{fulltext_prefix}/{arxiv_id}.pdf"
            print(fake_pdf_path, doc.bibcode, "fakeaccno", "fakesubdate", file=f)

    print(f"Wrote `{logs_dir / 'fulltextharvest.out'}`")

    # Copy out the ground-truth refstring files.

    gt_dir = out_dir / "references" / "groundtruth"

    for doc in docs:
        arxiv_id = doc.global_id.replace(".", "_")
        ap = Path(arxiv_id)
        ref_dir = gt_dir / fulltext_prefix / ap.parent
        ref_dir.mkdir(parents=True, exist_ok=True)
        ref_path = ref_dir / (ap.name + ".txt")
        shutil.copy(doc.ext_path(".rs.txt"), ref_path)

    print(f"Wrote files in `{gt_dir}`")


if __name__ == "__main__":
    main()
