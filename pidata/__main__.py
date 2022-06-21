# Licensed under GPLv3
# Copyright 2022 SAO/NASA Astrophysics Data System

"""
Report some summary statistics about the corpus. Invoke this with ``python -m
pidata``.
"""

from collections import OrderedDict
from dataclasses import dataclass
from typing import Set

from . import scan


@dataclass
class AspectInfo:
    collections: Set[str]
    n_docs: int

    def __init__(self):
        self.collections = set()
        self.n_docs = 0


ASPECTS = [
    "Any data",
    "ADS bibcode",
    "Vector PDF source",
    "Raster PDF source",
    "Refstring ground truth",
]


def summarize():
    aspects = OrderedDict((a, AspectInfo()) for a in ASPECTS)

    def add(doc, key):
        info = aspects[key]
        info.n_docs += 1
        info.collections.add(doc.collection_name)

    # Scan

    for doc in scan(load_def=True):
        add(doc, "Any data")

        if doc.bibcode is not None:
            add(doc, "ADS bibcode")

        if doc.pdf_is_raster:
            add(doc, "Raster PDF source")
        else:
            add(doc, "Vector PDF source")

        if ".rs.txt" in doc.extensions:
            add(doc, "Refstring ground truth")

    # Report

    print("Document counts:")
    print()

    for desc, info in aspects.items():
        print(f"  {desc}: {info.n_docs} docs in {len(info.collections)} collections")


if __name__ == "__main__":
    summarize()
