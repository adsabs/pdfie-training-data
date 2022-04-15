# Licensed under GPLv3
# Copyright 2022 SAO/NASA Astrophysics Data System

"""
General code for working with the training database.
"""

from dataclasses import dataclass
import os.path
from pathlib import Path
from typing import FrozenSet, Generator, Set

__all__ = ["COLLECTIONS_ROOT", "RECOGNIZED_EXTENSIONS", "Document", "scan"]

COLLECTIONS_ROOT = Path(os.path.dirname(__file__))

RECOGNIZED_EXTENSIONS = [
    ".doc.toml",
    ".rr.txt",
]


@dataclass
class Document:
    collection_name: str
    collection_id: str
    extensions: FrozenSet[str]

    @classmethod
    def new_from_scan(cls, cname: str, cid: str, exts: Set[str]):
        return cls(
            collection_name=cname,
            collection_id=cid,
            extensions=frozenset(exts),
        )

    @property
    def global_id(self) -> str:
        return f"{self.collection_name}/{self.collection_id}"


def scan() -> Generator[Document, None, None]:
    """
    Scan all of the documents in the database.

    This function is a generator that yields Document instances.
    """

    for coll_item in COLLECTIONS_ROOT.iterdir():
        if not coll_item.is_dir():
            continue

        collection_name = coll_item.name
        coll_item = str(coll_item)
        n_strip_prefix = len(coll_item) + 1

        for dirpath, _dirnames, filenames in os.walk(coll_item):
            # Files in the toplevel collection subdirectory never correspond to
            # documents.
            if dirpath == coll_item:
                continue

            doc_data = {}

            for fn in filenames:
                for ext in RECOGNIZED_EXTENSIONS:
                    if fn.endswith(ext):
                        tail = fn[: -len(ext)]
                        cid = dirpath[n_strip_prefix:] + "/" + tail
                        doc_data.setdefault(cid, set()).add(ext)
                        break

            for cid, exts in doc_data.items():
                yield Document.new_from_scan(collection_name, cid, exts)
