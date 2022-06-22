#! /usr/bin/env python3
# Licensed under GPLv3
# Copyright 2022 SAO/NASA Astrophysics Data System

"""
Stub TOML for a one-off PDF ingestion.
"""

import argparse
import os.path
from pathlib import Path
import toml

from .. import util


COLL_PREFIX = Path(os.path.dirname(__file__))


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("name")
    parser.add_argument("pdf_path")
    settings = parser.parse_args()

    with open(settings.pdf_path, mode="rb") as f:
        n_bytes, sha256, db_path = util.ingest_stream_to_local_data(f)

    print(f"Ingested input to `{db_path}`")

    info = {
        "pdf_sha256": sha256,
        "pdf_n_bytes": n_bytes,
        "random_index": util.make_random_index(),
        "pdf_is_raster": False,
    }

    toml_path = COLL_PREFIX / "oneoff" / (settings.name + ".doc.toml")
    with open(toml_path, "wt") as f:
        toml.dump(info, f)

    print(f"Wrote TOML metadata to `{toml_path}`")


if __name__ == "__main__":
    main()
