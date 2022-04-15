# Licensed under GPLv3
# Copyright 2022 SAO/NASA Astrophysics Data System

"""
General code for working with the training database.
"""

from dataclasses import dataclass
import os.path
from pathlib import Path
import toml
from typing import FrozenSet, Generator, Optional, Set

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
    bibcode: Optional[str]
    pdf_sha256_hex: Optional[str]
    pdf_n_bytes: Optional[int]
    pdf_path_symbolic: Optional[str]

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

    def _augment_with_doc_def(self):
        toml_path = os.path.join(
            COLLECTIONS_ROOT, self.collection_name, self.collection_id + ".doc.toml"
        )

        try:
            with open(toml_path, "rt") as f:
                info = toml.load(f)
        except FileNotFoundError:
            info = {}

        self.bibcode = info.get("bibcode")
        self.pdf_sha256 = info.get("pdf_sha256")
        self.pdf_n_bytes = info.get("pdf_n_bytes")
        self.pdf_path_symbolic = info.get("pdf_path")


def scan(bibcode=False, pdf_path=False) -> Generator[Document, None, None]:
    """
    Scan all of the documents in the database.

    This function is a generator that yields Document instances.

    If *bibcode* is True, the document must have a metadata file that specifies
    its bibcode.

    *pdf_path* is like *bibcode* for that respective field.
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
                doc = Document.new_from_scan(collection_name, cid, exts)

                if bibcode or pdf_path:
                    doc._augment_with_doc_def()

                    if bibcode and doc.bibcode is None:
                        continue

                    if pdf_path and doc.pdf_path is None:
                        continue

                yield doc
