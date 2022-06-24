# Licensed under GPLv3
# Copyright 2022 SAO/NASA Astrophysics Data System

"""
General code for working with the training database.
"""

from dataclasses import dataclass
import os.path
from pathlib import Path
import toml
from typing import FrozenSet, Generator, Optional, Set, Tuple, Union

__all__ = [
    "COLLECTIONS_ROOT",
    "RECOGNIZED_EXTENSIONS",
    "Document",
    "scan",
    "scan_for_ext",
]

COLLECTIONS_ROOT = Path(os.path.dirname(__file__))

RECOGNIZED_EXTENSIONS = [
    ".doc.toml",
    ".rs.txt",
]


@dataclass
class Document:
    collection_name: str
    collection_id: str
    extensions: FrozenSet[str]
    bibcode: Optional[str]
    pdf_sha256_hex: Optional[str]
    pdf_n_bytes: Optional[int]
    ads_pdf_path_symbolic: Optional[str]
    pdf_is_raster: bool
    random_index: int

    @classmethod
    def new_from_scan(cls, cname: str, cid: str, exts: Set[str]):
        return cls(
            collection_name=cname,
            collection_id=cid,
            extensions=frozenset(exts),
            bibcode=None,
            pdf_sha256_hex=None,
            pdf_n_bytes=None,
            ads_pdf_path_symbolic=None,
            pdf_is_raster=False,
            random_index=-1,
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
        self.pdf_sha256_hex = info.get("pdf_sha256")
        self.pdf_n_bytes = info.get("pdf_n_bytes")
        self.ads_pdf_path_symbolic = info.get("ads_pdf_path")
        self.pdf_is_raster = info.get("pdf_is_raster", False)
        self.random_index = info.get("random_index", -1)

    def ext_path(self, ext: str) -> Path:
        return COLLECTIONS_ROOT / self.collection_name / (self.collection_id + ext)


def scan(
    load_def=False, bibcode=False, rs=False, no_raster=False
) -> Generator[Document, None, None]:
    """
    Scan all of the documents in the database.

    This function is a generator that yields Document instances.

    If *load_def* is True, the document's metadata will be loaded from its
    associated `.doc.toml` file. This adds I/O overhead to the scan.

    If *bibcode* is True, only documents with metadata that specify their ADS
    bibcodes are yielded. Implies *load_def*.

    If *rs* is True, only documents with `.rs.txt` refstring files are yielded.

    If *no_raster* is True, documents with raster-based PDFs are skipped.
    Implies *load_def*.
    """

    for coll_item in COLLECTIONS_ROOT.iterdir():
        if not coll_item.is_dir():
            continue

        collection_name = coll_item.name
        coll_item = str(coll_item)
        n_strip_prefix = len(coll_item) + 1
        need_doc_def = load_def or bibcode or no_raster

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

                if rs and ".rs.txt" not in exts:
                    continue

                if need_doc_def:
                    doc._augment_with_doc_def()

                    if bibcode and doc.bibcode is None:
                        continue

                    if no_raster and doc.pdf_is_raster:
                        continue

                yield doc


def scan_for_ext(
    rootdir: Union[Path, str], extension: str
) -> Generator[Tuple[str, Path], None, None]:
    """
    Scan a directory tree for files with a given extension.

    This function is a slightly more generalized version of `scan` that is aimed
    at scanning trees of exported from the database. It simple walks a tree
    starting from the specified root and yields paths with the specified
    extension.

    The yielded values are tuples of ``(global_id, filepath)``, where the
    ``global_id`` is inferred from the filepath by removing the rootdir prefix
    and the matched extension.
    """

    rootdir = str(rootdir)
    n_strip_prefix = len(rootdir) + 1
    tail_slice = -len(extension)

    for dirpath, _dirnames, filenames in os.walk(rootdir):
        for fn in filenames:
            if fn.endswith(extension):
                tail = fn[:tail_slice]
                gid = dirpath[n_strip_prefix:] + "/" + tail
                yield (gid, Path(dirpath) / fn)
