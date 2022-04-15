# Licensed under GPLv3
# Copyright 2022 SAO/NASA Astrophysics Data System

"""
Export the database into a format suitable for use with the
arxiv-reference-extractor pipeline.
"""

import argparse
import os
from pathlib import Path

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

    docs = list(scan(bibcode=True, pdf_path=True))

    # Do the log files

    # logs_dir = out_dir / "logs" / session_id
    # logs_dir.mkdir(parents=True, exist_ok=True)
    # with (logs_dir / "extractrefs.out").open("wt") as f:

    for doc in docs:
        pdf_path = doc.pdf_path_symbolic.replace("$ADS_ARTICLES", ARTICLES_PREFIX)
        refs_path = os.path.join(REFERENCES_PREFIX, "sources", doc.global_id + ".raw")
        print(pdf_path, refs_path)


if __name__ == "__main__":
    main()
